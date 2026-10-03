"""Spot-exchange scans: single-exchange triangles and cross-exchange spreads.

``book`` maps "BASE/QUOTE" -> [bid, ask]. Selling BASE earns ``bid`` QUOTE; buying BASE costs ``ask`` QUOTE.
"""
from __future__ import annotations

from itertools import permutations


def _edges(book: dict) -> dict:
    """(from, to) -> units of `to` per unit of `from`."""
    e = {}
    for pair, (bid, ask) in book.items():
        base, quote = pair.split("/")
        e[(base, quote)] = bid          # sell base
        e[(quote, base)] = 1.0 / ask    # buy base
    return e


def triangles(book: dict, fee: float, top: int = 5) -> list[dict]:
    """All 3-leg cycles; returns best by net result, each with gross and net multiples."""
    e = _edges(book)
    nodes = sorted({n for pair in e for n in pair})
    seen, rows = set(), []
    for a, b, c in permutations(nodes, 3):
        if not all(k in e for k in ((a, b), (b, c), (c, a))):
            continue
        canon = min((a, b, c), (b, c, a), (c, a, b))
        if canon in seen:
            continue
        seen.add(canon)
        gross = e[(a, b)] * e[(b, c)] * e[(c, a)]
        rows.append({"cycle": f"{a}>{b}>{c}>{a}", "gross_bps": (gross - 1) * 1e4,
                     "net_bps": (gross * (1 - fee) ** 3 - 1) * 1e4})
    rows.sort(key=lambda r: r["net_bps"], reverse=True)
    return rows[:top]


def cross_exchange(a_name: str, a_book: dict, a_fee: float,
                   b_name: str, b_book: dict, b_fee: float, top: int = 8) -> list[dict]:
    """Buy at one venue's ask, sell at the other's bid, for every pair quoted on both (ignores transfer cost)."""
    rows = []
    for pair in sorted(set(a_book) & set(b_book)):
        for buy_n, buy_b, buy_f, sell_n, sell_b, sell_f in (
            (a_name, a_book, a_fee, b_name, b_book, b_fee),
            (b_name, b_book, b_fee, a_name, a_book, a_fee),
        ):
            ask = buy_b[pair][1]
            bid = sell_b[pair][0]
            gross = bid / ask - 1
            rows.append({"pair": pair, "buy": buy_n, "sell": sell_n, "gross_bps": gross * 1e4,
                         "net_bps": ((bid * (1 - sell_f)) / (ask * (1 + buy_f)) - 1) * 1e4})
    rows.sort(key=lambda r: r["gross_bps"], reverse=True)
    return rows[:top]
