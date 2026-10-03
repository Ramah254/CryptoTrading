"""Live data fetchers and snapshot builder (stdlib only).

Status of each endpoint, checked 2026-10-03:

* VERIFIED against real payloads (fixtures in tests/fixtures): open.er-api.com, api.wise.com comparisons,
  data-api.binance.vision bookTicker, api.kraken.com Ticker.
* UNVERIFIED: Binance / Bybit / OKX P2P endpoints. They were written from the public web-app request shapes,
  could not be called from the dev sandbox (egress policy), and may need small adjustments on first run.

Hosts needed: open.er-api.com, api.wise.com, data-api.binance.vision, api.kraken.com,
p2p.binance.com, api2.bybit.com, www.okx.com
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (compatible; arbscan/0.1)", "Accept": "application/json"}
HOSTS = ("open.er-api.com", "api.wise.com", "data-api.binance.vision", "api.kraken.com",
         "p2p.binance.com", "api2.bybit.com", "www.okx.com")

BINANCE_SYMBOLS = {
    "BTCUSDT": "BTC/USDT", "ETHUSDT": "ETH/USDT", "ETHBTC": "ETH/BTC", "BNBUSDT": "BNB/USDT", "BNBBTC": "BNB/BTC",
    "BNBETH": "BNB/ETH", "XRPUSDT": "XRP/USDT", "XRPBTC": "XRP/BTC", "SOLUSDT": "SOL/USDT", "SOLBTC": "SOL/BTC",
    "SOLETH": "SOL/ETH", "TRXUSDT": "TRX/USDT", "TRXBTC": "TRX/BTC", "LTCUSDT": "LTC/USDT", "LTCBTC": "LTC/BTC",
    "USDCUSDT": "USDC/USDT", "BTCUSDC": "BTC/USDC", "ETHUSDC": "ETH/USDC", "FDUSDUSDT": "FDUSD/USDT",
}
KRAKEN_KEYS = {
    "XXBTZUSD": "BTC/USD", "XBTUSDT": "BTC/USDT", "XETHZUSD": "ETH/USD", "ETHUSDT": "ETH/USDT",
    "XETHXXBT": "ETH/BTC", "SOLUSD": "SOL/USD", "SOLXBT": "SOL/BTC", "XLTCZUSD": "LTC/USD",
    "XLTCXXBT": "LTC/BTC", "XXRPZUSD": "XRP/USD", "XXRPXXBT": "XRP/BTC", "USDTZUSD": "USDT/USD",
    "USDCUSD": "USDC/USD", "USDCUSDT": "USDC/USDT",
}
KRAKEN_REQUEST = "USDTUSD,USDCUSD,USDCUSDT,XBTUSD,XBTUSDT,ETHUSD,ETHUSDT,ETHXBT,XRPUSD,XRPXBT,SOLUSD,SOLXBT,LTCUSD,LTCXBT"


# --- transport ------------------------------------------------------------------------------
def _request(url: str, payload: dict | None = None, timeout: float = 20.0):
    data = None
    headers = dict(UA)
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


# --- pure parsers (unit-tested on real payloads) -------------------------------------------------
def parse_er_api(d: dict) -> dict:
    r = d["rates"]
    return {"usdkes_mid_erapi": r["KES"], "usdgbp_erapi": r["GBP"], "usdeur_erapi": r["EUR"]}


def parse_wise_comparison(d: dict) -> list[dict]:
    out = []
    for p in d["providers"]:
        q = p["quotes"][0]
        out.append({"provider": p["name"], "rate": q["rate"], "fee": q["fee"], "received": q["receivedAmount"],
                    "src": "wise_api", "promo": False, "mid": bool(q.get("isConsideredMidMarketRate"))})
    return out


def parse_binance_book(arr: list) -> dict:
    return {BINANCE_SYMBOLS[x["symbol"]]: [float(x["bidPrice"]), float(x["askPrice"])]
            for x in arr if x["symbol"] in BINANCE_SYMBOLS}


def parse_kraken(d: dict) -> dict:
    return {KRAKEN_KEYS[k]: [float(v["b"][0]), float(v["a"][0])] for k, v in d["result"].items() if k in KRAKEN_KEYS}


def _pay_names(methods) -> str:
    return ",".join(sorted(str(m).lower() for m in methods))


def parse_binance_p2p(d: dict) -> list[dict]:
    """UNVERIFIED shape: {"data":[{"adv":{...},"advertiser":{...}}]}"""
    ads = []
    for it in d.get("data") or []:
        a, u = it["adv"], it["advertiser"]
        names = [m.get("tradeMethodName") or m.get("identifier") or "" for m in a.get("tradeMethods", [])]
        ads.append({"adv": u.get("nickName", "?"), "price": float(a["price"]),
                    "min_kes": float(a["minSingleTransAmount"]),
                    "max_kes": float(a.get("dynamicMaxSingleTransAmount") or a["maxSingleTransAmount"]),
                    "avail_usdt": float(a["tradableQuantity"]),
                    "completion": float(u.get("monthFinishRate") or 0.0), "orders": int(u.get("monthOrderCount") or 0),
                    "method": "paybill" if "paybill" in _pay_names(names) else "mpesa"})
    return ads


def parse_bybit_p2p(d: dict) -> list[dict]:
    """UNVERIFIED shape: {"result":{"items":[...]}}"""
    ads = []
    for it in (d.get("result") or {}).get("items", []):
        ads.append({"adv": it.get("nickName", "?"), "price": float(it["price"]),
                    "min_kes": float(it["minAmount"]), "max_kes": float(it["maxAmount"]),
                    "avail_usdt": float(it.get("lastQuantity") or 0.0),
                    "completion": float(it.get("recentExecuteRate") or 0.0) / 100.0,
                    "orders": int(it.get("recentOrderNum") or 0), "method": "mpesa"})
    return ads


def parse_okx_p2p(d: dict, side: str) -> list[dict]:
    """UNVERIFIED shape: {"data":{"sell":[...],"buy":[...]}}"""
    ads = []
    for it in (d.get("data") or {}).get(side, []):
        pm = _pay_names(it.get("paymentMethods", []))
        ads.append({"adv": it.get("nickName", "?"), "price": float(it["price"]),
                    "min_kes": float(it["quoteMinAmountPerOrder"]), "max_kes": float(it["quoteMaxAmountPerOrder"]),
                    "avail_usdt": float(it.get("availableAmount") or 0.0),
                    "completion": float(it.get("completedRate") or 0.0),
                    "orders": int(it.get("completedOrderQuantity") or 0),
                    "method": "paybill" if "paybill" in pm else "mpesa"})
    return ads


# --- fetchers ------------------------------------------------------------------------------------
def fetch_fx() -> dict:
    return parse_er_api(_request("https://open.er-api.com/v6/latest/USD"))


def fetch_wise(src: str, dst: str, amount: int = 1000) -> list[dict]:
    url = f"https://api.wise.com/v4/comparisons/?sourceCurrency={src}&targetCurrency={dst}&sendAmount={amount}"
    return parse_wise_comparison(_request(url))


def fetch_binance_book() -> dict:
    syms = json.dumps(list(BINANCE_SYMBOLS), separators=(",", ":"))
    url = "https://data-api.binance.vision/api/v3/ticker/bookTicker?symbols=" + urllib.request.quote(syms)
    return parse_binance_book(_request(url))


def fetch_kraken_book() -> dict:
    return parse_kraken(_request("https://api.kraken.com/0/public/Ticker?pair=" + KRAKEN_REQUEST))


def fetch_binance_p2p(trade_type: str, pay_types: list[str] | None, rows: int = 20) -> list[dict]:
    payload = {"fiat": "KES", "asset": "USDT", "tradeType": trade_type, "page": 1, "rows": rows,
               "payTypes": pay_types or [], "countries": [], "publisherType": None, "transAmount": "",
               "proMerchantAds": False, "shieldMerchantAds": False, "filterType": "all", "periods": [],
               "additionalKycVerifyFilter": 0, "classifies": ["mass", "profession"]}
    return parse_binance_p2p(_request("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", payload))


def fetch_bybit_p2p(side: str, size: int = 20) -> list[dict]:
    """side '1' = buy USDT (merchants selling), '0' = sell USDT."""
    payload = {"userId": "", "tokenId": "USDT", "currencyId": "KES", "payment": [], "side": side,
               "size": str(size), "page": "1", "amount": "", "authMaker": False, "canTrade": False}
    return parse_bybit_p2p(_request("https://api2.bybit.com/fiat/otc/item/online", payload))


def fetch_okx_p2p(side: str) -> list[dict]:
    """side 'sell' = asks (merchants selling USDT), 'buy' = bids."""
    url = ("https://www.okx.com/v3/c2c/tradingOrders/books?quoteCurrency=KES&baseCurrency=USDT"
           f"&side={'sell' if side == 'sell' else 'buy'}&paymentMethod=all&userType=all&receivingAds=false&t={int(time.time() * 1000)}")
    return parse_okx_p2p(_request(url), "sell" if side == "sell" else "buy")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def build_snapshot(base: dict) -> tuple[dict, list[str]]:
    """Refresh ``base`` (a loaded snapshot) with live data. Returns (snapshot, errors).

    Anything that fails keeps its previous value and is listed in errors so stale data is never silent.
    """
    snap = json.loads(json.dumps(base))
    errors: list[str] = []
    now = _stamp()

    def attempt(name, fn):
        try:
            return fn()
        except (urllib.error.URLError, OSError, KeyError, ValueError, TypeError) as e:
            errors.append(f"{name}: {type(e).__name__}: {e}")
            return None

    fx = attempt("fx", fetch_fx)
    if fx:
        snap["fx"].update(fx)
    for key, (src, dst) in (("usd_kes_1000", ("USD", "KES")), ("gbp_kes_1000", ("GBP", "KES"))):
        w = attempt(f"wise {src}->{dst}", lambda s=src, d=dst: fetch_wise(s, d))
        if w:
            snap["remit"][key] = w
    for name, fn in (("binance", fetch_binance_book), ("kraken", fetch_kraken_book)):
        bk = attempt(f"spot {name}", fn)
        if bk:
            snap["spot"][name]["book"] = bk
            snap["spot"][name]["at_utc"] = now

    p = snap["p2p_kes_usdt"]
    for venue, key, fn in (
        ("binance", "ask_mpesa", lambda: fetch_binance_p2p("BUY", ["MPesaKenya"])),
        ("binance", "ask_paybill", lambda: fetch_binance_p2p("BUY", ["MpesaPaybill"])),
        ("binance", "bid_mpesa", lambda: fetch_binance_p2p("SELL", ["MPesaKenya"])),
        ("binance", "bid_all", lambda: fetch_binance_p2p("SELL", None)),
        ("bybit", "ask_all", lambda: fetch_bybit_p2p("1")),
        ("bybit", "bid_all", lambda: fetch_bybit_p2p("0")),
    ):
        ads = attempt(f"p2p {venue}/{key}", fn)
        if ads:
            p[venue][key] = {"at_utc": now, "ads": ads}

    okx_ask, okx_bid = attempt("p2p okx ask", lambda: fetch_okx_p2p("sell")), attempt("p2p okx bid", lambda: fetch_okx_p2p("buy"))
    if okx_ask and okx_bid:
        a, b = min(x["price"] for x in okx_ask), max(x["price"] for x in okx_bid)
        p["okx_top1_indicative"] = {"source": "okx books (all methods)", "at_utc": now,
                                    "ask": {"mpesa": a, "paybill": a, "bank": a}, "bid": {"mpesa": b, "paybill": b, "bank": b}}
    snap["meta"]["asof_utc"] = now
    snap["meta"]["live_errors"] = errors
    return snap, errors
