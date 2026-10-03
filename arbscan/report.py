"""Markdown rendering of scan results."""
from __future__ import annotations

from . import book, cycles, spot
from .cycles import Result, Snapshot
from .fees import Assumptions


def md_table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def pct(r: Result) -> str:
    return f"{r.pnl_pct:+.2f}%" if r.feasible else "n/a"


def money(r: Result) -> str:
    if not r.feasible:
        return "n/a"
    unit = "KES" if r.start_ccy == "KES" else "$"
    return f"{r.pnl:+,.0f} KES" if unit == "KES" else f"{r.pnl:+,.2f} $"


def sized_prices(snap: Snapshot, A: Assumptions, sizes) -> str:
    rows = []
    for s in sizes:
        K = s * A.mid_usdkes

        def one(venue, key, side):
            ad = (book.best_ask if side == "ask" else book.best_bid)(snap.ads(venue, key), K)
            return f"{ad['price']:.2f}" if ad else "none"

        rows.append([f"${s:,.0f} (KES {K:,.0f})",
                     one("binance", "ask_paybill", "ask"), one("binance", "ask_mpesa", "ask"),
                     one("binance", "bid_mpesa", "bid"), one("bybit", "ask_all", "ask"), one("bybit", "bid_all", "bid")])
    return md_table(["Order size", "Binance ask (Paybill)", "Binance ask (M-Pesa)", "Binance bid (M-Pesa)",
                     "Bybit ask", "Bybit bid"], rows)


def headline_vs_sized(snap: Snapshot, A: Assumptions, size_usd: float) -> str:
    K = size_usd * A.mid_usdkes
    rows = []
    for venue, key, side in (("bybit", "ask_all", "ask"), ("binance", "ask_mpesa", "ask"),
                             ("binance", "bid_mpesa", "bid"), ("bybit", "bid_all", "bid")):
        ads = snap.ads(venue, key)
        h = book.headline(ads, side)
        fn = book.best_ask if side == "ask" else book.best_bid
        ad = fn(ads, K)
        rows.append([f"{venue}:{key}", f"{h:.2f}", f"{ad['price']:.2f}" if ad else "none",
                     f"{(ad['price'] / h - 1) * 100:+.2f}%" if ad else "-"])
    return md_table(["Book", "Headline (any size)", f"Fillable at ${size_usd:,.0f}", "Gap"], rows)


def kes_only(snap: Snapshot, A: Assumptions, sizes) -> str:
    rows = []
    for s in sizes:
        res = [r for r in cycles.kes_matrix(snap, A, s) if r.feasible]
        res.sort(key=lambda r: r.pnl_pct, reverse=True)
        best, worst = res[0], res[-1]
        rows.append([f"${s:,.0f}", best.name, pct(best), money(best), worst.name, pct(worst)])
    return md_table(["Size", "Best loop", "Net %", "Net", "Worst loop", "Net %"], rows)


def raenest(snap: Snapshot, A: Assumptions, sizes, spreads=(0.0, 0.0025, 0.005, 0.01)) -> str:
    rows = []
    for s in sizes:
        for sp in spreads:
            Asp = A.with_(raenest_spread=sp)
            k = cycles.kes_usdt_raenest_kes(snap, Asp, s)
            u = cycles.usd_raenest_loop(snap, Asp, s)
            rows.append([f"${s:,.0f}", f"{sp:.2%}", f"{Asp.mid_usdkes * (1 - sp):.2f}", pct(k), money(k), pct(u),
                         f"{k.extra.get('breakeven_rate', float('nan')):.2f}"])
    return md_table(["Size", "Raenest spread vs mid", "Raenest USD->KES rate", "KES-start net %", "KES-start net",
                     "USD-start net %", "Break-even rate"], rows)


def paypal(snap: Snapshot, A: Assumptions, sizes, premiums=(1.00, 1.02, 1.04, 1.06)) -> str:
    rows = []
    for s in sizes:
        be = cycles.paypal_loop(snap, A, s).extra.get("breakeven_premium", float("nan"))
        for p in premiums:
            r = cycles.paypal_loop(snap, A, s, premium=p)
            rows.append([f"${s:,.0f}", f"{p:.3f}", pct(r), money(r), f"{be:.4f}"])
    return md_table(["Size", "PayPal bid (USD per USDT)", "Net %", "Net", "Break-even bid"], rows)


def other_loops(snap: Snapshot, A: Assumptions, sizes) -> str:
    rows = []
    for s in sizes:
        for r in [cycles.gbp_loop(snap, A, s)] + cycles.btc_triangles(snap, A, s):
            rows.append([f"${s:,.0f}", r.name, pct(r) if r.feasible else f"n/a ({r.reason})"])
    return md_table(["Size", "Loop", "Net %"], rows)


def spot_section(snap: Snapshot) -> str:
    out = []
    for name, ex in snap.d["spot"].items():
        tri = spot.triangles(ex["book"], ex["taker_fee"], top=3)
        out.append(f"**{name} triangles** (taker fee {ex['taker_fee']:.2%} per leg)")
        out.append(md_table(["Cycle", "Gross (bps)", "Net (bps)"],
                            [[t["cycle"], f"{t['gross_bps']:+.2f}", f"{t['net_bps']:+.1f}"] for t in tri]))
    b, k = snap.d["spot"]["binance"], snap.d["spot"]["kraken"]
    # Kraken quotes USD; align the shared symbols by also mapping USDT pairs
    xs = spot.cross_exchange("binance", b["book"], b["taker_fee"], "kraken", k["book"], k["taker_fee"], top=6)
    out.append("**Cross-exchange (buy at one ask, sell at the other bid; transfer cost ignored)**")
    out.append(md_table(["Pair", "Buy", "Sell", "Gross (bps)", "Net after taker fees (bps)"],
                        [[x["pair"], x["buy"], x["sell"], f"{x['gross_bps']:+.2f}", f"{x['net_bps']:+.1f}"] for x in xs]))
    return "\n\n".join(out)


def remit(snap: Snapshot, A: Assumptions) -> str:
    out = []
    for key, mid, ccy in (("usd_kes_1000", A.mid_usdkes, "USD"), ("gbp_kes_1000", A.gbpkes_mid, "GBP")):
        rows = []
        for p in sorted(snap.d["remit"][key], key=lambda p: -p["received"]):
            rows.append([p["provider"], f"{p['rate']:.4f}", f"{p['fee']:.2f}", f"{p['received']:,.0f}",
                         f"{(p['received'] / (1000 * mid) - 1) * 100:+.2f}%", "first-transfer promo" if p["promo"] else ""])
        out.append(f"**{ccy} 1,000 -> KES (mid {mid:.2f})**")
        out.append(md_table(["Provider", "Rate", f"Fee ({ccy})", "KES received", "vs mid", "Note"], rows))
    return "\n\n".join(out)


def render(snap: Snapshot, A: Assumptions, sizes) -> str:
    parts = [
        f"# arbscan results (snapshot {snap.d['meta']['asof_utc']}, mid USD/KES {A.mid_usdkes:.2f})",
        "## Fillable P2P prices by order size (Binance/Bybit, KES per USDT)", sized_prices(snap, A, sizes),
        "## Headline vs fillable (decoy check) at $1,000", headline_vs_sized(snap, A, 1000),
        "## KES -> USDT -> KES (all venue pairs; best and worst)", kes_only(snap, A, sizes),
        "## Raenest loop: KES -> USDT -> Raenest USD -> KES (spread = Raenest margin vs mid, unknown)", raenest(snap, A, sizes),
        "## PayPal loop: USD -> M-Pesa (3%) -> USDT -> PayPal buyer", paypal(snap, A, sizes),
        "## GBP and BTC detours", other_loops(snap, A, sizes),
        "## Spot crypto", spot_section(snap),
        "## Inbound remitters (relevant if the sender is abroad)", remit(snap, A),
    ]
    return "\n\n".join(parts) + "\n"
