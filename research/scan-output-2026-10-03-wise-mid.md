# arbscan results (snapshot 2026-10-03T06:30:00Z, mid USD/KES 129.75)

## Fillable P2P prices by order size (Binance/Bybit, KES per USDT)

| Order size | Binance ask (Paybill) | Binance ask (M-Pesa) | Binance bid (M-Pesa) | Bybit ask | Bybit bid |
|---|---|---|---|---|---|
| $1,000 (KES 129,750) | 129.12 | 129.50 | 129.08 | 129.52 | 128.76 |
| $3,000 (KES 389,250) | 129.26 | 129.50 | 129.00 | 129.52 | 128.76 |

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
| $1,000 | KES>USDT [binance:ask_paybill] >KES [binance:bid_mpesa] | -0.03% | -40 KES | KES>USDT [okx_top1_indicative:ask_paybill] >KES [bybit:bid_all] | -0.71% |
| $3,000 | KES>USDT [binance:ask_paybill] >KES [binance:bid_all] | -0.19% | -753 KES | KES>USDT [okx_top1_indicative:ask_paybill] >KES [bybit:bid_all] | -0.69% |

## Raenest loop: KES -> USDT -> Raenest USD -> KES (spread = Raenest margin vs mid, unknown)

| Size | Raenest spread vs mid | Raenest USD->KES rate | KES-start net % | KES-start net | USD-start net % | Break-even rate |
|---|---|---|---|---|---|---|
| $1,000 | 0.00% | 129.75 | -0.01% | -16 KES | -0.01% | 129.77 |
| $1,000 | 0.25% | 129.43 | -0.26% | -340 KES | -0.26% | 129.77 |
| $1,000 | 0.50% | 129.10 | -0.51% | -664 KES | -0.51% | 129.77 |
| $1,000 | 1.00% | 128.45 | -1.01% | -1,313 KES | -1.02% | 129.77 |
| $3,000 | 0.00% | 129.75 | +0.21% | +827 KES | +0.21% | 129.47 |
| $3,000 | 0.25% | 129.43 | -0.04% | -148 KES | -0.04% | 129.47 |
| $3,000 | 0.50% | 129.10 | -0.29% | -1,124 KES | -0.29% | 129.47 |
| $3,000 | 1.00% | 128.45 | -0.79% | -3,074 KES | -0.79% | 129.47 |

## PayPal loop: USD -> M-Pesa (3%) -> USDT -> PayPal buyer

| Size | PayPal bid (USD per USDT) | Net % | Net | Break-even bid |
|---|---|---|---|---|
| $1,000 | 1.000 | -2.53% | -25.27 $ | 1.0259 |
| $1,000 | 1.020 | -0.58% | -5.77 $ | 1.0259 |
| $1,000 | 1.040 | +1.37% | +13.72 $ | 1.0259 |
| $1,000 | 1.060 | +3.32% | +33.22 $ | 1.0259 |
| $3,000 | 1.000 | -2.63% | -78.97 $ | 1.0270 |
| $3,000 | 1.020 | -0.68% | -20.55 $ | 1.0270 |
| $3,000 | 1.040 | +1.26% | +37.87 $ | 1.0270 |
| $3,000 | 1.060 | +3.21% | +96.29 $ | 1.0270 |

## GBP and BTC detours

| Size | Loop | Net % |
|---|---|---|
| $1,000 | KES>USDT>GBP(Faster Payments)>Raenest GBP>KES | -0.99% |
| $1,000 | KES>BTC(P2P ask)>USDT(spot)>KES(P2P bid) | -4.66% |
| $1,000 | KES>USDT(P2P ask)>BTC(spot)>KES(P2P bid) | -0.96% |
| $3,000 | KES>USDT>GBP(Faster Payments)>Raenest GBP>KES | -0.58% |
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

**USD 1,000 -> KES (mid 129.75)**

| Provider | Rate | Fee (USD) | KES received | vs mid | Note |
|---|---|---|---|---|---|
| MoneyGram | 132.0990 | 0.00 | 132,100 | +1.81% | first-transfer promo |
| WorldRemit | 130.8440 | 0.99 | 130,715 | +0.74% | first-transfer promo |
| Remitly | 129.9000 | 0.00 | 129,900 | +0.12% | first-transfer promo |
| Western Union (first transfer) | 129.1160 | 0.00 | 129,116 | -0.49% | first-transfer promo |
| Instarem | 128.7424 | 0.00 | 128,742 | -0.78% |  |
| Taptap Send | 128.3000 | 0.00 | 128,300 | -1.12% |  |
| XE Money Transfer | 128.8630 | 8.00 | 127,832 | -1.48% |  |
| Wise | 129.7500 | 17.79 | 127,442 | -1.78% |  |
| Western Union | 127.1697 | 1.99 | 126,917 | -2.18% |  |

**GBP 1,000 -> KES (mid 171.56)**

| Provider | Rate | Fee (GBP) | KES received | vs mid | Note |
|---|---|---|---|---|---|
| MoneyGram | 171.5908 | 0.00 | 171,591 | +0.02% | first-transfer promo |
| Instarem | 170.7254 | 0.00 | 170,725 | -0.48% |  |
| WorldRemit | 170.8204 | 0.99 | 170,651 | -0.53% | first-transfer promo |
| Taptap Send | 170.3000 | 0.00 | 170,300 | -0.73% |  |
| XE Money Transfer | 170.4075 | 3.00 | 169,896 | -0.97% |  |
| Wise | 171.7760 | 11.48 | 169,804 | -1.02% |  |
| Remitly | 169.2900 | 0.00 | 169,290 | -1.32% | first-transfer promo |
| HSBC | 168.1659 | 0.00 | 168,166 | -1.98% |  |
| Barclays | 167.0684 | 0.00 | 167,068 | -2.62% |  |
| Western Union | 167.0509 | 2.99 | 166,551 | -2.92% |  |
