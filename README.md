# CryptoTrading

Research and tooling for loop ("triangular") arbitrage that starts and ends in M-Pesa KES, Raenest USD/GBP or PayPal USD.

**Read first:** [`research/triangular-arbitrage-report-2026-10-03.md`](research/triangular-arbitrage-report-2026-10-03.md). Finding of 3 Oct 2026: no profitable, repeatable loop at retail size. One conditional loop (M-Pesa to USDT to Raenest USD to KES) needs a Raenest quote of at least 129.48 KES per USD at $3,000.

| Path | What it is |
|---|---|
| `research/` | Report, raw working notes, and the scanner's saved outputs |
| `arbscan/` | Net-of-fee loop scanner, standard library only |
| `data/snapshot_2026-10-03.json` | Prices and fees the report is based on |
| `tools/loop-check.html` | Calculator for the numbers only your apps show (Raenest rate, PayPal bid) |
| `tests/` | 24 tests, including parsers checked against real API responses |

## Run

```
python3 -m unittest discover -s tests
python3 -m arbscan --snapshot data/snapshot_2026-10-03.json --sizes 300 1000 3000
python3 -m arbscan --snapshot data/snapshot_2026-10-03.json --live --write-snapshot data/live.json
```

`--live` refreshes the snapshot from public endpoints and prints a STALE DATA banner for anything it could not fetch.
Hosts needed: `open.er-api.com, api.wise.com, data-api.binance.vision, api.kraken.com, p2p.binance.com, api2.bybit.com, www.okx.com`.
The FX, Wise, Binance spot and Kraken parsers are tested on real responses. The Binance, Bybit and OKX P2P calls are unverified.

## How the scanner avoids false positives

P2P "top-1" prices on aggregator sites are dominated by decoy ads (orders capped at KES 150 to 400, zero history). `arbscan/book.py` accepts an ad only if one order of your size fits its limits and liquidity and the advertiser has at least 95% completion and 100 orders.
