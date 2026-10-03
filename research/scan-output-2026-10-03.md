# arbscan results (snapshot 2026-10-03T06:30:00Z, mid USD/KES 129.56)

## Fillable P2P prices by order size (Binance/Bybit, KES per USDT)

| Order size | Binance ask (Paybill) | Binance ask (M-Pesa) | Binance bid (M-Pesa) | Bybit ask | Bybit bid |
|---|---|---|---|---|---|
| $300 (KES 38,868) | 129.12 | 129.50 | 129.06 | 129.60 | 128.76 |
| $1,000 (KES 129,560) | 129.12 | 129.50 | 129.08 | 129.52 | 128.76 |
| $3,000 (KES 388,681) | 129.26 | 129.50 | 129.00 | 129.52 | 128.76 |

## Headline vs fillable (decoy check) at $1,000

| Book | Headline (any size) | Fillable at $1,000 | Gap |
|---|---|---|---|
| bybit:ask_all | 128.40 | 129.52 | +0.87% |
| binance:ask_mpesa | 129.38 | 129.50 | +0.09% |
| binance:bid_mpesa | 129.08 | 129.08 | +0.00% |
| bybit:bid_all | 128.76 | 128.76 | +0.00% |

## KES -> USDT -> KES (all venue pairs; best and worst)

| Size | Best loop | Net % | Net | Worst loop | Net % |
|---|---|---|---|---|---|
| $300 | KES>USDT [binance:ask_paybill] >KES [binance:bid_mpesa] | -0.05% | -18 KES | KES>USDT [binance:ask_mpesa] >KES [bybit:bid_all] | -0.95% |
| $1,000 | KES>USDT [binance:ask_paybill] >KES [binance:bid_mpesa] | -0.03% | -40 KES | KES>USDT [okx_top1_indicative:ask_paybill] >KES [bybit:bid_all] | -0.71% |
| $3,000 | KES>USDT [binance:ask_paybill] >KES [binance:bid_all] | -0.19% | -752 KES | KES>USDT [okx_top1_indicative:ask_paybill] >KES [bybit:bid_all] | -0.69% |

## Raenest loop: KES -> USDT -> Raenest USD -> KES (spread = Raenest margin vs mid, unknown)

| Size | Raenest spread vs mid | Raenest USD->KES rate | KES-start net % | KES-start net | USD-start net % | Break-even rate |
|---|---|---|---|---|---|---|
| $300 | 0.00% | 129.56 | -0.93% | -360 KES | -0.93% | 130.77 |
| $300 | 0.25% | 129.24 | -1.17% | -456 KES | -1.18% | 130.77 |
| $300 | 0.50% | 128.91 | -1.42% | -552 KES | -1.43% | 130.77 |
| $300 | 1.00% | 128.26 | -1.92% | -745 KES | -1.92% | 130.77 |
| $1,000 | 0.00% | 129.56 | -0.16% | -206 KES | -0.16% | 129.77 |
| $1,000 | 0.25% | 129.24 | -0.41% | -529 KES | -0.41% | 129.77 |
| $1,000 | 0.50% | 128.91 | -0.66% | -853 KES | -0.66% | 129.77 |
| $1,000 | 1.00% | 128.26 | -1.16% | -1,500 KES | -1.16% | 129.77 |
| $3,000 | 0.00% | 129.56 | +0.07% | +255 KES | +0.07% | 129.48 |
| $3,000 | 0.25% | 129.24 | -0.18% | -717 KES | -0.18% | 129.48 |
| $3,000 | 0.50% | 128.91 | -0.43% | -1,690 KES | -0.44% | 129.48 |
| $3,000 | 1.00% | 128.26 | -0.94% | -3,634 KES | -0.94% | 129.48 |

## PayPal loop: USD -> M-Pesa (3%) -> USDT -> PayPal buyer

| Size | PayPal bid (USD per USDT) | Net % | Net | Break-even bid |
|---|---|---|---|---|
| $300 | 1.000 | -2.67% | -8.01 $ | 1.0274 |
| $300 | 1.020 | -0.72% | -2.17 $ | 1.0274 |
| $300 | 1.040 | +1.22% | +3.67 $ | 1.0274 |
| $300 | 1.060 | +3.17% | +9.51 $ | 1.0274 |
| $1,000 | 1.000 | -2.67% | -26.69 $ | 1.0274 |
| $1,000 | 1.020 | -0.72% | -7.23 $ | 1.0274 |
| $1,000 | 1.040 | +1.22% | +12.24 $ | 1.0274 |
| $1,000 | 1.060 | +3.17% | +31.71 $ | 1.0274 |
| $3,000 | 1.000 | -2.77% | -83.24 $ | 1.0285 |
| $3,000 | 1.020 | -0.83% | -24.91 $ | 1.0285 |
| $3,000 | 1.040 | +1.11% | +33.43 $ | 1.0285 |
| $3,000 | 1.060 | +3.06% | +91.77 $ | 1.0285 |

## GBP and BTC detours

| Size | Loop | Net % |
|---|---|---|
| $300 | KES>USDT>GBP(Faster Payments)>Raenest GBP>KES | -2.11% |
| $300 | KES>BTC(P2P ask)>USDT(spot)>KES(P2P bid) | -1.80% |
| $300 | KES>USDT(P2P ask)>BTC(spot)>KES(P2P bid) | -0.96% |
| $1,000 | KES>USDT>GBP(Faster Payments)>Raenest GBP>KES | -1.14% |
| $1,000 | KES>BTC(P2P ask)>USDT(spot)>KES(P2P bid) | -4.66% |
| $1,000 | KES>USDT(P2P ask)>BTC(spot)>KES(P2P bid) | -0.96% |
| $3,000 | KES>USDT>GBP(Faster Payments)>Raenest GBP>KES | -0.73% |
| $3,000 | KES>BTC(P2P ask)>USDT(spot)>KES(P2P bid) | -4.70% |
| $3,000 | KES>USDT(P2P ask)>BTC(spot)>KES(P2P bid) | -1.07% |

## Spot crypto

**binance triangles** (taker fee 0.10% per leg)

| Cycle | Gross (bps) | Net (bps) |
|---|---|---|
| BNB>ETH>USDT>BNB | +1.07 | -28.9 |
| BTC>USDC>ETH>BTC | +0.79 | -29.2 |
| BTC>SOL>USDT>BTC | +0.79 | -29.2 |

**kraken triangles** (taker fee 0.40% per leg)

| Cycle | Gross (bps) | Net (bps) |
|---|---|---|
| BTC>LTC>USD>BTC | +5.49 | -114.1 |
| BTC>USD>USDT>BTC | +0.37 | -119.2 |
| ETH>USDT>USD>ETH | +0.22 | -119.3 |

**Cross-exchange (buy at one ask, sell at the other bid; transfer cost ignored)**

| Pair | Buy | Sell | Gross (bps) | Net after taker fees (bps) |
|---|---|---|---|---|
| ETH/USDT | binance | kraken | +0.93 | -49.0 |
| BTC/USDT | binance | kraken | +0.63 | -49.3 |
| LTC/BTC | kraken | binance | +0.00 | -49.8 |
| SOL/BTC | kraken | binance | +0.00 | -49.8 |
| XRP/BTC | binance | kraken | +0.00 | -50.0 |
| USDC/USDT | binance | kraken | -0.30 | -50.2 |

## Inbound remitters (relevant if the sender is abroad)

**USD 1,000 -> KES (mid 129.56)**

| Provider | Rate | Fee (USD) | KES received | vs mid | Note |
|---|---|---|---|---|---|
| MoneyGram | 132.0990 | 0.00 | 132,100 | +1.96% | first-transfer promo |
| WorldRemit | 130.8440 | 0.99 | 130,715 | +0.89% | first-transfer promo |
| Remitly | 129.9000 | 0.00 | 129,900 | +0.26% | first-transfer promo |
| Western Union (first transfer) | 129.1160 | 0.00 | 129,116 | -0.34% | first-transfer promo |
| Instarem | 128.7424 | 0.00 | 128,742 | -0.63% |  |
| Taptap Send | 128.3000 | 0.00 | 128,300 | -0.97% |  |
| XE Money Transfer | 128.8630 | 8.00 | 127,832 | -1.33% |  |
| Wise | 129.7500 | 17.79 | 127,442 | -1.63% |  |
| Western Union | 127.1697 | 1.99 | 126,917 | -2.04% |  |

**GBP 1,000 -> KES (mid 171.31)**

| Provider | Rate | Fee (GBP) | KES received | vs mid | Note |
|---|---|---|---|---|---|
| MoneyGram | 171.5908 | 0.00 | 171,591 | +0.17% | first-transfer promo |
| Instarem | 170.7254 | 0.00 | 170,725 | -0.34% |  |
| WorldRemit | 170.8204 | 0.99 | 170,651 | -0.38% | first-transfer promo |
| Taptap Send | 170.3000 | 0.00 | 170,300 | -0.59% |  |
| XE Money Transfer | 170.4075 | 3.00 | 169,896 | -0.82% |  |
| Wise | 171.7760 | 11.48 | 169,804 | -0.88% |  |
| Remitly | 169.2900 | 0.00 | 169,290 | -1.18% | first-transfer promo |
| HSBC | 168.1659 | 0.00 | 168,166 | -1.83% |  |
| Barclays | 167.0684 | 0.00 | 167,068 | -2.47% |  |
| Western Union | 167.0509 | 2.99 | 166,551 | -2.77% |  |
