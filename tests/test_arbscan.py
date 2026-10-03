import json
import math
import os
import unittest

from arbscan import book, cycles, fees, spot
from arbscan.cycles import Snapshot
from arbscan.fees import Assumptions

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP = Snapshot.load(os.path.join(ROOT, "data", "snapshot_2026-10-03.json"))
A = Assumptions()


class TestMpesaFees(unittest.TestCase):
    def test_tariff_boundaries(self):
        self.assertEqual(fees.mpesa_send_fee(100), 0)
        self.assertEqual(fees.mpesa_send_fee(101), 7)
        self.assertEqual(fees.mpesa_send_fee(20_000), 105)
        self.assertEqual(fees.mpesa_send_fee(20_001), 108)
        self.assertEqual(fees.mpesa_send_fee(250_000), 108)

    def test_over_cap_raises_but_total_chunks(self):
        with self.assertRaises(ValueError):
            fees.mpesa_send_fee(250_001)
        self.assertEqual(fees.mpesa_total_send_fee(250_000), 108)
        self.assertEqual(fees.mpesa_total_send_fee(400_000), 216)   # two txns of 200k
        self.assertEqual(fees.mpesa_total_send_fee(0), 0)

    def test_sendable_pays_fee_on_top(self):
        for budget in (500, 5_000, 129_560, 249_000, 388_680):
            s = fees.mpesa_sendable(budget)
            self.assertLessEqual(s + fees.mpesa_total_send_fee(s), budget + 1e-6)
            self.assertGreater(s + fees.mpesa_total_send_fee(s), budget - 120)  # not wasteful


class TestBook(unittest.TestCase):
    def test_decoys_rejected(self):
        ads = SNAP.ads("bybit", "ask_all")
        self.assertAlmostEqual(book.headline(ads, "ask"), 128.40)           # decoy headline
        best = book.best_ask(ads, 129_560)
        self.assertGreaterEqual(best["price"], 129.5)                      # sized price is real

    def test_limits_and_liquidity_enforced(self):
        ads = [{"price": 100, "min_kes": 1000, "max_kes": 5000, "avail_usdt": 1000, "completion": 1, "orders": 500}]
        self.assertIsNone(book.best_ask(ads, 500))
        self.assertIsNone(book.best_ask(ads, 6000))
        self.assertIsNotNone(book.best_ask(ads, 3000))
        ads[0]["avail_usdt"] = 1                                           # only KES 100 of liquidity
        self.assertIsNone(book.best_ask(ads, 3000))

    def test_track_record_enforced(self):
        ads = [{"price": 100, "min_kes": 0, "max_kes": 1e9, "avail_usdt": 1e9, "completion": 0.5, "orders": 500},
               {"price": 101, "min_kes": 0, "max_kes": 1e9, "avail_usdt": 1e9, "completion": 1.0, "orders": 3}]
        self.assertIsNone(book.best_ask(ads, 1000))


class TestCycles(unittest.TestCase):
    def test_zero_spread_locked_market_costs_only_fees(self):
        snap = Snapshot({"p2p_kes_usdt": {"v": {
            "ask_paybill": {"ads": [{"adv": "a", "price": 130.0, "min_kes": 0, "max_kes": 1e9, "avail_usdt": 1e9, "completion": 1, "orders": 999}]},
            "bid_mpesa": {"ads": [{"adv": "b", "price": 130.0, "min_kes": 0, "max_kes": 1e9, "avail_usdt": 1e9, "completion": 1, "orders": 999}]}}}})
        r = cycles.kes_usdt_kes(snap, A, 1000, ("v", "ask_paybill"), ("v", "bid_mpesa"))
        self.assertAlmostEqual(r.pnl_pct, 0.0, places=9)                    # Paybill: free, same venue

    def test_best_kes_loop_is_negative_today(self):
        for s in (300, 1000, 3000):
            res = [r for r in cycles.kes_matrix(SNAP, A, s) if r.feasible]
            self.assertTrue(res)
            self.assertLess(max(r.pnl_pct for r in res), 0.0, f"size {s}")

    def test_raenest_breakeven_rate_gives_zero_pnl(self):
        for s in (300, 1000, 3000):
            r = cycles.kes_usdt_raenest_kes(SNAP, A, s)
            be = r.extra["breakeven_rate"]
            r2 = cycles.kes_usdt_raenest_kes(SNAP, A, s, rate=be)
            self.assertAlmostEqual(r2.pnl_pct, 0.0, places=7)

    def test_usd_start_breakeven_matches_closed_form(self):
        for s in (300, 1000, 3000):
            r = cycles.usd_raenest_loop(SNAP, A, s)
            be = r.extra["breakeven_rate"]
            r2 = cycles.usd_raenest_loop(SNAP, A, s, rate=be)
            self.assertAlmostEqual(r2.pnl_pct, 0.0, places=7)

    def test_raenest_loop_needs_size_to_clear_fixed_fees(self):
        be_small = cycles.kes_usdt_raenest_kes(SNAP, A, 300).extra["breakeven_rate"]
        be_big = cycles.kes_usdt_raenest_kes(SNAP, A, 3000).extra["breakeven_rate"]
        self.assertGreater(be_small, be_big)                                # fixed fees amortise

    def test_paypal_breakeven_premium(self):
        for s in (300, 1000, 3000):
            r = cycles.paypal_loop(SNAP, A, s)
            p = r.extra["breakeven_premium"]
            r2 = cycles.paypal_loop(SNAP, A, s, premium=p)
            self.assertAlmostEqual(r2.pnl_pct, 0.0, places=7)
            self.assertGreater(p, 1.02)                                     # more than the ~2% premium seen today

    def test_btc_triangles_negative(self):
        for s in (300, 1000, 3000):
            for r in cycles.btc_triangles(SNAP, A, s):
                if r.feasible:
                    self.assertLess(r.pnl_pct, 0.0)

    def test_infeasible_when_no_ad_fits(self):
        r = cycles.kes_usdt_kes(SNAP, A, 100_000)                           # KES 13m: no single ad
        self.assertFalse(r.feasible)


class TestSpot(unittest.TestCase):
    def test_detects_synthetic_triangle(self):
        book_ = {"A/USDT": [10.0, 10.0], "B/USDT": [20.0, 20.0], "B/A": [2.2, 2.2]}   # A>B>... mispriced
        rows = spot.triangles(book_, fee=0.0, top=1)
        self.assertGreater(rows[0]["gross_bps"], 0)

    def test_no_arbitrage_in_efficient_book(self):
        book_ = {"A/USDT": [10.0, 10.0], "B/USDT": [20.0, 20.0], "B/A": [2.0, 2.0]}
        rows = spot.triangles(book_, fee=0.0, top=1)
        self.assertAlmostEqual(rows[0]["gross_bps"], 0.0, places=6)

    def test_real_snapshot_has_no_net_positive_triangle(self):
        for ex in SNAP.d["spot"].values():
            rows = spot.triangles(ex["book"], ex["taker_fee"], top=1)
            self.assertLess(rows[0]["net_bps"], 0)

    def test_cross_exchange_net_negative(self):
        b, k = SNAP.d["spot"]["binance"], SNAP.d["spot"]["kraken"]
        rows = spot.cross_exchange("binance", b["book"], b["taker_fee"], "kraken", k["book"], k["taker_fee"], top=50)
        self.assertTrue(rows)
        for r in rows:
            self.assertLess(r["net_bps"], 0)


class TestRender(unittest.TestCase):
    def test_report_renders(self):
        from arbscan import report
        out = report.render(SNAP, A, [300, 1000, 3000])
        self.assertIn("Raenest loop", out)
        self.assertNotIn("nan%", out)


if __name__ == "__main__":
    unittest.main()


FIX = os.path.join(ROOT, "tests", "fixtures")


def _fx(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


class TestLiveParsersOnRealPayloads(unittest.TestCase):
    """Fixtures are real responses captured on 2026-10-03."""

    def test_er_api(self):
        from arbscan import live
        fx = live.parse_er_api(_fx("er_api.json"))
        self.assertAlmostEqual(fx["usdkes_mid_erapi"], 129.560263)
        self.assertAlmostEqual(fx["usdgbp_erapi"], 0.756313)

    def test_wise_comparison(self):
        from arbscan import live
        rows = live.parse_wise_comparison(_fx("wise_usd_kes.json"))
        by = {r["provider"]: r for r in rows}
        self.assertEqual(len(rows), 3)
        self.assertAlmostEqual(by["Instarem"]["received"], 128742.4)
        self.assertTrue(by["Wise"]["mid"])
        self.assertAlmostEqual(by["Wise"]["fee"], 17.79)

    def test_binance_book_maps_and_skips_unknown(self):
        from arbscan import live
        bk = live.parse_binance_book(_fx("binance_book.json"))
        self.assertEqual(bk["BTC/USDT"], [84637.50, 84637.51])
        self.assertNotIn("NOTMAPPED", bk)
        self.assertEqual(len(bk), 5)

    def test_kraken_maps_legacy_keys(self):
        from arbscan import live
        bk = live.parse_kraken(_fx("kraken_ticker.json"))
        self.assertEqual(bk["BTC/USD"], [84629.10, 84629.20])
        self.assertEqual(bk["ETH/BTC"], [0.031639, 0.031641])
        self.assertEqual(bk["USDT/USD"], [0.99979, 0.99980])


class TestLiveFailureIsLoud(unittest.TestCase):
    def test_blocked_network_keeps_old_values_and_reports(self):
        import urllib.error
        from unittest import mock
        from arbscan import live
        with mock.patch.object(live, "_request", side_effect=urllib.error.URLError("403 blocked")):
            snap, errors = live.build_snapshot(SNAP.d)
        self.assertGreaterEqual(len(errors), 10)                            # every fetch reported
        self.assertEqual(snap["fx"]["usdkes_mid_erapi"], SNAP.d["fx"]["usdkes_mid_erapi"])
        self.assertEqual(snap["p2p_kes_usdt"]["binance"]["ask_paybill"], SNAP.d["p2p_kes_usdt"]["binance"]["ask_paybill"])
        self.assertIn("live_errors", snap["meta"])
