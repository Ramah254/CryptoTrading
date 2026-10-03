"""P2P ad selection: pick the best price that you could actually fill, not the best headline.

Headline "top-1" prices on aggregator sites are dominated by decoys: ads capped at KES 150-400,
promoted placeholders, zero-history accounts. We only accept an ad if one order of the target
size fits its limits and the advertiser has a real track record.
"""
from __future__ import annotations

from typing import Iterable, Optional

Ad = dict


def qualified(ads: Iterable[Ad], size_kes: float, *, min_completion: float = 0.95,
              min_orders: int = 100) -> list[Ad]:
    out = []
    for a in ads:
        if a.get("promoted") or a.get("decoy"):
            continue
        if not (a["min_kes"] <= size_kes <= a["max_kes"]):
            continue
        avail = a.get("avail_usdt")
        if avail is not None and avail * a["price"] < size_kes:
            continue
        if a.get("completion", 0.0) < min_completion or a.get("orders", 0) < min_orders:
            continue
        out.append(a)
    return out


def best_ask(ads: Iterable[Ad], size_kes: float, **kw) -> Optional[Ad]:
    """Cheapest ad selling to us (we pay KES) that can fill ``size_kes`` in one order."""
    q = qualified(ads, size_kes, **kw)
    return min(q, key=lambda a: a["price"]) if q else None


def best_bid(ads: Iterable[Ad], size_kes: float, **kw) -> Optional[Ad]:
    """Highest-paying ad buying from us (we receive KES) that can fill ``size_kes`` in one order."""
    q = qualified(ads, size_kes, **kw)
    return max(q, key=lambda a: a["price"]) if q else None


def headline(ads: Iterable[Ad], side: str) -> float:
    """Best price ignoring size/limits (what an aggregator would show), excluding flagged ads."""
    prices = [a["price"] for a in ads if not a.get("promoted") and not a.get("decoy")]
    return min(prices) if side == "ask" else max(prices)
