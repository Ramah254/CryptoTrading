"""Fee models and scenario assumptions.

Every constant records where it came from. All figures checked 2026-10-03.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace

# --- M-Pesa (Safaricom tariff; receiving money is free) -------------------------------
# (upper bound inclusive in KES, fee in KES) for a customer "send money" transaction.
MPESA_SEND_TARIFF = (
    (100, 0.0), (500, 7.0), (1_000, 13.0), (1_500, 23.0), (2_500, 33.0),
    (3_500, 53.0), (5_000, 57.0), (7_500, 78.0), (10_000, 90.0),
    (15_000, 100.0), (20_000, 105.0), (250_000, 108.0),
)
MPESA_TXN_CAP = 250_000.0     # per transaction
MPESA_DAILY_CAP = 500_000.0   # per day; also the wallet balance cap


def mpesa_send_fee(amount: float) -> float:
    """Fee for ONE send-money transaction of ``amount`` KES (must be <= the per-txn cap)."""
    if amount <= 0:
        return 0.0
    if amount > MPESA_TXN_CAP + 1e-9:
        raise ValueError(f"{amount} exceeds the M-Pesa per-transaction cap; use mpesa_total_send_fee")
    for upper, fee in MPESA_SEND_TARIFF:
        if amount <= upper:
            return fee
    raise AssertionError("unreachable")


def mpesa_total_send_fee(amount: float) -> float:
    """Cheapest way to move ``amount`` KES: the fewest, equal-sized transactions."""
    if amount <= 0:
        return 0.0
    n = math.ceil(amount / MPESA_TXN_CAP - 1e-12)
    return n * mpesa_send_fee(amount / n)


def mpesa_sendable(budget: float) -> float:
    """Largest amount S such that S + fees(S) <= budget (fees are paid on top by the sender)."""
    s = budget
    for _ in range(100):
        over = s + mpesa_total_send_fee(s) - budget
        if over <= 1e-9:
            return s
        s -= over
    return s


# --- Raenest (help center, Kenya articles, 2026) ---------------------------------------
def raenest_conversion_fee_usd(usd: float, pct: float = 0.005, lo: float = 0.25, hi: float = 2.70) -> float:
    """ASSUMPTION: 0.5% with $0.25 floor and $2.70 cap, as published for NGN corridors (Jan 2026).
    The USD->KES corridor fee is not published; the app shows it before you confirm."""
    return min(max(usd * pct, lo), hi)


def raenest_gbp_deposit_fee_gbp(gbp: float, pct: float = 0.008, lo: float = 3.0, hi: float = 12.0) -> float:
    """GBP bank-transfer deposit: 0.8%, min GBP 3, max GBP 12 (Kenya fees article)."""
    return min(max(gbp * pct, lo), hi)


@dataclass(frozen=True)
class Assumptions:
    """Scenario knobs. Defaults are today's best estimates; override via ``replace``."""
    mid_usdkes: float = 129.560263      # open.er-api.com 2026-10-03 00:02Z (Wise says 129.75)
    usdgbp: float = 0.756313            # GBP per USD (open.er-api)
    usdt_usd: float = 1.0               # Raenest credits USDT/USDC at USD parity
    exch_withdraw_usdt: float = 0.30    # Binance USDT BEP20 withdrawal fee
    raenest_stable_fee_usd: float = 1.0  # flat; TRON network is $2
    raenest_payout_fee_usd: float = 1.0  # to Kenyan bank or mobile money
    raenest_spread: float = 0.0         # SCENARIO: rate margin vs mid on USD->KES (unknown)
    paypal_to_mpesa: float = 0.03       # conversion fee baked into PayPal's rate
    paypal_bid_premium: float = 1.02    # USD received per USDT when selling to a PayPal buyer
    spot_taker_fee: float = 0.001       # Binance spot taker

    def with_(self, **kw) -> "Assumptions":
        return replace(self, **kw)

    @property
    def gbpkes_mid(self) -> float:
        return self.mid_usdkes / self.usdgbp
