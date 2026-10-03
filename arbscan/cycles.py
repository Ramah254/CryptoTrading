"""Cycle evaluators. Each returns a :class:`Result` with a step trace; PnL is in the START currency.

All P2P prices come from ``book.best_ask/best_bid`` so only fillable, credible ads are used.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Iterable

from . import book, fees
from .fees import Assumptions


class Infeasible(Exception):
    """No credible ad can fill this order size."""


@dataclass
class Step:
    label: str
    detail: str


@dataclass
class Result:
    name: str
    start_ccy: str
    start_amt: float
    end_amt: float = 0.0
    steps: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)
    feasible: bool = True
    reason: str = ""

    @property
    def pnl(self) -> float:
        return self.end_amt - self.start_amt

    @property
    def pnl_pct(self) -> float:
        return 100.0 * (self.end_amt / self.start_amt - 1.0) if self.start_amt else float("nan")


class Snapshot:
    def __init__(self, data: dict):
        self.d = data

    @classmethod
    def load(cls, path: str) -> "Snapshot":
        with open(path, encoding="utf-8") as fh:
            return cls(json.load(fh))

    def ads(self, venue: str, key: str) -> list:
        """KES/USDT ads for ``venue``/``key``. OKX only has indicative top-1 prices (no limits)."""
        if venue == "okx_top1_indicative":
            side, method = key.split("_", 1)            # e.g. ask_mpesa
            price = self.d["p2p_kes_usdt"][venue][side][method]
            return [{"adv": "OKX top-1 (indicative)", "price": price, "min_kes": 0, "max_kes": 1e12,
                     "completion": 1.0, "orders": 10_000, "method": method}]
        return self.d["p2p_kes_usdt"][venue][key]["ads"]


def _kes(size_usd: float, A: Assumptions) -> float:
    return size_usd * A.mid_usdkes


# --- building blocks ---------------------------------------------------------------------
def buy_usdt(snap: Snapshot, venue: str, key: str, kes_budget: float):
    """Spend ``kes_budget`` (M-Pesa) on USDT. Paybill is free to the payer; send-money is not."""
    ad = book.best_ask(snap.ads(venue, key), kes_budget)
    if ad is None:
        raise Infeasible(f"no credible {venue}/{key} ask can fill KES {kes_budget:,.0f} in one order")
    free = key.endswith("paybill") or ad.get("method") == "paybill"
    send = kes_budget if free else fees.mpesa_sendable(kes_budget)
    return send / ad["price"], ad, kes_budget - send


def sell_usdt(snap: Snapshot, venue: str, key: str, kes_size: float, usdt: float):
    ad = book.best_bid(snap.ads(venue, key), kes_size)
    if ad is None:
        raise Infeasible(f"no credible {venue}/{key} bid can fill KES {kes_size:,.0f} in one order")
    return usdt * ad["price"], ad


def _cap_note(res: Result, kes: float) -> None:
    if kes > fees.MPESA_DAILY_CAP:
        res.notes.append(f"KES {kes:,.0f} exceeds the M-Pesa daily cap (KES {fees.MPESA_DAILY_CAP:,.0f}); split over days.")


# --- Family 1: KES -> USDT -> KES (P2P only) -----------------------------------------------
def kes_usdt_kes(snap: Snapshot, A: Assumptions, size_usd: float,
                 buy=("binance", "ask_paybill"), sell=("binance", "bid_mpesa")) -> Result:
    K = _kes(size_usd, A)
    r = Result(f"KES>USDT [{buy[0]}:{buy[1]}] >KES [{sell[0]}:{sell[1]}]", "KES", K)
    try:
        usdt, ad, fee = buy_usdt(snap, *buy, K)
        r.steps.append(Step("buy", f"{ad['adv']} @ {ad['price']:.2f}; M-Pesa fee KES {fee:.0f} -> {usdt:.4f} USDT"))
        if buy[0] != sell[0]:
            usdt -= A.exch_withdraw_usdt
            r.steps.append(Step("transfer", f"withdraw {A.exch_withdraw_usdt} USDT between venues"))
        end, bad = sell_usdt(snap, *sell, K, usdt)
        r.steps.append(Step("sell", f"{bad['adv']} @ {bad['price']:.2f} -> KES {end:,.0f}"))
        r.end_amt = end
        r.extra.update(ask=ad["price"], bid=bad["price"], mpesa_fee=fee)
    except Infeasible as e:
        r.feasible, r.reason = False, str(e)
    _cap_note(r, K)
    return r


# --- Family 2: Raenest stablecoin loop ---------------------------------------------------------
def _raenest_net_usd(usd: float, A: Assumptions) -> float:
    return usd - fees.raenest_conversion_fee_usd(usd) - A.raenest_payout_fee_usd


def kes_usdt_raenest_kes(snap: Snapshot, A: Assumptions, size_usd: float,
                         buy=("binance", "ask_paybill"), rate: float | None = None) -> Result:
    """M-Pesa KES -> USDT (P2P) -> Raenest USD (stablecoin deposit) -> KES (Raenest payout)."""
    K = _kes(size_usd, A)
    R = rate if rate is not None else A.mid_usdkes * (1 - A.raenest_spread)
    r = Result(f"KES>USDT[{buy[1]}]>Raenest USD>KES (Raenest rate {R:.2f})", "KES", K)
    try:
        usdt, ad, fee = buy_usdt(snap, *buy, K)
        r.steps.append(Step("buy", f"{ad['adv']} @ {ad['price']:.2f}; M-Pesa fee KES {fee:.0f} -> {usdt:.4f} USDT"))
        usd = (usdt - A.exch_withdraw_usdt) * A.usdt_usd - A.raenest_stable_fee_usd
        r.steps.append(Step("deposit", f"withdraw fee {A.exch_withdraw_usdt} USDT + Raenest ${A.raenest_stable_fee_usd} -> ${usd:,.2f}"))
        net = _raenest_net_usd(usd, A)
        r.steps.append(Step("convert", f"Raenest conv fee ${fees.raenest_conversion_fee_usd(usd):.2f} + payout ${A.raenest_payout_fee_usd} -> ${net:,.2f} @ {R:.2f}"))
        r.end_amt = net * R
        r.extra["breakeven_rate"] = K / net            # minimum Raenest USD->KES rate for PnL = 0
        r.extra["ask"] = ad["price"]
    except Infeasible as e:
        r.feasible, r.reason = False, str(e)
    _cap_note(r, K)
    return r


def usd_raenest_loop(snap: Snapshot, A: Assumptions, size_usd: float,
                     buy=("binance", "ask_paybill"), rate: float | None = None) -> Result:
    """Same loop started from a Raenest USD balance: USD -> KES (Raenest) -> USDT -> Raenest USD."""
    R = rate if rate is not None else A.mid_usdkes * (1 - A.raenest_spread)
    r = Result(f"USD@Raenest>KES(rate {R:.2f})>USDT[{buy[1]}]>USD@Raenest", "USD", size_usd)
    net = _raenest_net_usd(size_usd, A)
    kes = net * R
    r.steps.append(Step("convert", f"conv fee ${fees.raenest_conversion_fee_usd(size_usd):.2f} + payout ${A.raenest_payout_fee_usd} -> KES {kes:,.0f}"))
    try:
        usdt, ad, fee = buy_usdt(snap, *buy, kes)
        r.steps.append(Step("buy", f"{ad['adv']} @ {ad['price']:.2f}; M-Pesa fee KES {fee:.0f} -> {usdt:.4f} USDT"))
        usd = (usdt - A.exch_withdraw_usdt) * A.usdt_usd - A.raenest_stable_fee_usd
        r.steps.append(Step("deposit", f"withdraw fee {A.exch_withdraw_usdt} USDT + Raenest ${A.raenest_stable_fee_usd} -> ${usd:,.2f}"))
        r.end_amt = usd
        # closed form: ((S - fee - payout) * R / ask - w - r) = S  (M-Pesa fee is zero on Paybill)
        if buy[1].endswith("paybill"):
            conv = fees.raenest_conversion_fee_usd(size_usd)
            r.extra["breakeven_rate"] = ad["price"] * (size_usd + A.exch_withdraw_usdt + A.raenest_stable_fee_usd) / (
                size_usd - conv - A.raenest_payout_fee_usd)
        r.extra["ask"] = ad["price"]
    except Infeasible as e:
        r.feasible, r.reason = False, str(e)
    _cap_note(r, kes)
    return r


# --- Family 3: PayPal ----------------------------------------------------------------------------
def paypal_loop(snap: Snapshot, A: Assumptions, size_usd: float, premium: float | None = None,
                buy=("binance", "ask_paybill")) -> Result:
    """PayPal USD -> M-Pesa KES (PayPal rate, 3% built in) -> USDT (P2P) -> PayPal USD (P2P sale)."""
    p = premium if premium is not None else A.paypal_bid_premium
    r = Result(f"USD@PayPal>KES(-{A.paypal_to_mpesa:.0%})>USDT[{buy[1]}]>USD@PayPal (premium {p:.3f})", "USD", size_usd)
    kes = size_usd * A.mid_usdkes * (1 - A.paypal_to_mpesa)
    r.steps.append(Step("withdraw", f"PayPal->M-Pesa at mid x (1-{A.paypal_to_mpesa:.0%}) -> KES {kes:,.0f}"))
    try:
        usdt, ad, fee = buy_usdt(snap, *buy, kes)
        r.steps.append(Step("buy", f"{ad['adv']} @ {ad['price']:.2f}; M-Pesa fee KES {fee:.0f} -> {usdt:.4f} USDT"))
        r.end_amt = usdt * A.usdt_usd * p
        r.steps.append(Step("sell", f"sell to a PayPal buyer at {p:.3f} USD/USDT -> ${r.end_amt:,.2f}"))
        send = kes - fee
        r.extra["breakeven_premium"] = ad["price"] * size_usd / (send * A.usdt_usd)
        r.extra["ask"] = ad["price"]
    except Infeasible as e:
        r.feasible, r.reason = False, str(e)
    r.notes.append("Breaches PayPal's Acceptable Use Policy (currency-exchange activity) and chargebacks fall on you.")
    return r


# --- Family 4: GBP via Faster Payments -----------------------------------------------------------
def gbp_loop(snap: Snapshot, A: Assumptions, size_usd: float, buy=("binance", "ask_paybill")) -> Result:
    """KES -> USDT -> GBP (Faster Payments bid) -> Raenest GBP -> KES (Raenest). Uses the best sane FP bid."""
    K = _kes(size_usd, A)
    r = Result("KES>USDT>GBP(Faster Payments)>Raenest GBP>KES", "KES", K)
    ads = [a for a in snap.d["p2p_other"]["binance_gbp_usdt_bid"] if not a.get("decoy") and a["completion"] >= 0.95]
    bid = max(ads, key=lambda a: a["price"])
    try:
        usdt, ad, fee = buy_usdt(snap, *buy, K)
        gbp = usdt * bid["price"]
        dep = fees.raenest_gbp_deposit_fee_gbp(gbp)
        gbp_net = gbp - dep
        usd_eq = gbp_net / A.usdgbp
        net_usd = usd_eq - fees.raenest_conversion_fee_usd(usd_eq) - A.raenest_payout_fee_usd
        r.end_amt = net_usd * A.mid_usdkes * (1 - A.raenest_spread)
        r.steps.append(Step("buy", f"{ad['adv']} @ {ad['price']:.2f} -> {usdt:.4f} USDT"))
        r.steps.append(Step("sell", f"{bid['adv']} @ {bid['price']:.3f} GBP/USDT (limits GBP {bid['min_gbp']}-{bid['max_gbp']}) -> GBP {gbp:,.2f}"))
        r.steps.append(Step("deposit", f"Raenest GBP deposit fee GBP {dep:.2f}"))
        r.steps.append(Step("convert", f"-> USD-eq {usd_eq:,.2f}, net ${net_usd:,.2f} -> KES {r.end_amt:,.0f}"))
        r.extra["gbp_bid"] = bid["price"]
    except Infeasible as e:
        r.feasible, r.reason = False, str(e)
    return r


# --- Family 5: KES -> BTC -> USDT -> KES (P2P BTC + Binance spot) ----------------------------------
def btc_triangles(snap: Snapshot, A: Assumptions, size_usd: float) -> list[Result]:
    K = _kes(size_usd, A)
    out = []
    p2p = snap.d["p2p_other"]["binance_btc_kes_mpesa"]
    bt = snap.d["spot"]["binance"]["book"]["BTC/USDT"]
    f = A.spot_taker_fee

    # (a) KES -> BTC (P2P ask) -> USDT (spot sell) -> KES (P2P bid)
    ra = Result("KES>BTC(P2P ask)>USDT(spot)>KES(P2P bid)", "KES", K)
    ask = book.best_ask(p2p["ask"], K)
    try:
        if ask is None:
            raise Infeasible("no credible BTC ask for this size")
        send = fees.mpesa_sendable(K)
        btc = send / ask["price"]
        usdt = btc * bt[0] * (1 - f)
        ra.end_amt, bad = sell_usdt(snap, "binance", "bid_mpesa", K, usdt)
        ra.steps.append(Step("buy BTC", f"{ask['adv']} @ KES {ask['price']:,.0f}"))
        ra.steps.append(Step("spot", f"sell BTC at {bt[0]:,.2f} (-{f:.2%} fee) -> {usdt:.4f} USDT"))
        ra.steps.append(Step("sell USDT", f"{bad['adv']} @ {bad['price']:.2f}"))
    except Infeasible as e:
        ra.feasible, ra.reason = False, str(e)
    out.append(ra)

    # (b) KES -> USDT (P2P ask) -> BTC (spot buy) -> KES (P2P BTC bid)
    rb = Result("KES>USDT(P2P ask)>BTC(spot)>KES(P2P bid)", "KES", K)
    try:
        usdt, ad, fee = buy_usdt(snap, "binance", "ask_paybill", K)
        btc = usdt / bt[1] * (1 - f)
        bid = book.best_bid(p2p["bid"], K)
        if bid is None:
            raise Infeasible("no credible BTC bid for this size")
        rb.end_amt = btc * bid["price"]
        rb.steps.append(Step("buy USDT", f"{ad['adv']} @ {ad['price']:.2f}"))
        rb.steps.append(Step("spot", f"buy BTC at {bt[1]:,.2f} (-{f:.2%} fee) -> {btc:.8f} BTC"))
        rb.steps.append(Step("sell BTC", f"{bid['adv']} @ KES {bid['price']:,.0f}"))
    except Infeasible as e:
        rb.feasible, rb.reason = False, str(e)
    out.append(rb)
    return out


# --- Cross-venue matrix and the scoreboard ---------------------------------------------------------
ASKS = (("binance", "ask_paybill"), ("binance", "ask_mpesa"), ("bybit", "ask_all"), ("okx_top1_indicative", "ask_paybill"))
BIDS = (("binance", "bid_mpesa"), ("binance", "bid_all"), ("bybit", "bid_all"), ("okx_top1_indicative", "bid_mpesa"))


def kes_matrix(snap: Snapshot, A: Assumptions, size_usd: float) -> list[Result]:
    return [kes_usdt_kes(snap, A, size_usd, b, s) for b in ASKS for s in BIDS]


def scoreboard(snap: Snapshot, A: Assumptions, sizes: Iterable[float],
               spreads=(0.0, 0.0025, 0.005, 0.01), premiums=(1.00, 1.02, 1.04, 1.06)) -> list[Result]:
    out: list[Result] = []
    for s in sizes:
        out += kes_matrix(snap, A, s)
        for sp in spreads:
            Asp = A.with_(raenest_spread=sp)
            out.append(kes_usdt_raenest_kes(snap, Asp, s))
            out.append(usd_raenest_loop(snap, Asp, s))
        for p in premiums:
            out.append(paypal_loop(snap, A, s, premium=p))
        out.append(gbp_loop(snap, A, s))
        out += btc_triangles(snap, A, s)
    return out
