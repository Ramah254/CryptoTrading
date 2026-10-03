# Triangular arbitrage scan: M-Pesa KES, Raenest USD/GBP, PayPal USD

Snapshot of 3 Oct 2026, 05:20 to 06:45 UTC. P2P prices drift about 0.05% per 30 minutes, so read every figure as plus or minus that.
Tool for your own numbers: https://claude.ai/artifact/FvHpTpMNqQ92XspWzbmyRm (private; source in `tools/loop-check.html`).

## Bottom line

1. **No profitable, repeatable loop exists today.** The best P2P-only loop (Binance Paybill ask 129.12, then Binance bid 129.08) loses 0.03% at $1,000 and 0.19% at $3,000.
2. **One loop can turn positive, only at size, and only if Raenest quotes close to mid:** M-Pesa → USDT → Raenest USD → KES. Break-even Raenest quote is **129.48 KES per USD at $3,000** (129.77 at $1,000, 130.77 at $300). With a perfect mid quote it nets $2 to $6 on $3,000, and every 0.1% of Raenest margin removes about $3.
3. **PayPal loops lose money at today's prices.** At the visible PayPal bid (about 1.02 USD per USDT) they lose 0.7% to 0.8%, and 2.7% at parity. They need a buyer paying at least 1.027 to 1.037 depending on which reference rate is right. The loop also breaches PayPal's policy and leaves you holding chargeback risk.
4. **GBP and BTC detours lose 0.7% to 4.7%.** Spot-crypto triangles lose at best 29 bps (Binance) and 114 bps (Kraken) after fees.
5. **Every "opportunity" the aggregator sites showed was a decoy:** Bybit asks at 128.4 (orders capped at KES 150 to 400), an Airtel bid at 130.0, a Binance bid at 131.5, a GBP bid at 0.811 (60% completion, 3 orders). None fills at real size.
6. **The 2026 risks outweigh margins this thin:** Kenya's DCI froze Binance accounts in April, Raenest can quarantine incoming stablecoins, PayPal restricts currency-exchange activity, and exchanges now report users to KRA.

## Scoreboard (net result of the full loop, in the start currency)

| Loop | $300 | $1,000 | $3,000 | Break-even or trigger |
|---|---|---|---|---|
| KES → USDT → KES, best venue pair (Binance Paybill ask, Binance bid) | -0.05% | -0.03% | -0.19% | best bid reaches best ask |
| same, worst venue pair | -0.95% | -0.71% | -0.69% | |
| Raenest loop, Raenest quotes mid (129.56) | -0.93% | -0.16% | **+0.07%** | Raenest at least 130.77 / 129.77 / 129.48 |
| Raenest loop, Raenest margin 0.25% | -1.17% | -0.41% | -0.18% | |
| Raenest loop, Raenest margin 0.5% | -1.42% | -0.66% | -0.43% | |
| Raenest loop at Wise mid (129.75), margin 0% | n/a | -0.01% | **+0.21%** | |
| PayPal loop, buyer pays 1.02 | -0.72% | -0.72% | -0.83% | buyer at least 1.027 / 1.027 / 1.029 |
| PayPal loop, buyer pays 1.04 | +1.22% | +1.22% | +1.11% | |
| GBP via Faster Payments (bid 0.754) | -2.11% | -1.14% | -0.73% | indicative: the ads cap at £1,500 to 1,960 |
| BTC detour (P2P BTC and Binance spot) | -0.96% to -1.80% | -0.96% to -4.66% | -1.07% to -4.70% | |
| Binance spot triangles, 0.10% fee per leg | | | | best gross +1.1 bps, net -28.9 bps |
| Kraken spot triangles, 0.40% fee per leg | | | | best gross +5.5 bps, net -114 bps |
| Binance vs Kraken, same pair | | | | best gross +0.9 bps, net -49 bps |

Assumptions: Paybill purchases carry no M-Pesa fee (Safaricom's tariff page, updated 4 Aug 2026, lists no customer charge for Pay Bill); send-money purchases pay the tariff (KES 108 for any single transaction from KES 20,001 to 250,000). Exchange withdrawal 0.30 USDT (BEP20). Raenest stablecoin fee $1, Kenya payout $1, conversion 0.5% with a $0.25 floor and $2.70 cap. That conversion fee is published for Nigerian corridors only, so the KES corridor is an assumption. PayPal to M-Pesa costs 3% on PayPal's rate.

## Prices that were fillable in one order (KES per USDT)

| Order | Binance ask (Paybill) | Binance ask (M-Pesa) | Binance bid | Bybit ask | Bybit bid |
|---|---|---|---|---|---|
| $300 | 129.12 | 129.50 | 129.06 | 129.60 | 128.76 |
| $1,000 | 129.12 | 129.50 | 129.08 | 129.52 | 128.76 |
| $3,000 | 129.26 | 129.50 | 129.00 | 129.52 | 128.76 |

An ad counts only if your order fits its limits and liquidity and the advertiser has at least 95% completion and 100 orders. At $1,000 the Bybit headline ask (128.40) is 0.87% below the cheapest ask that fills. The reference rate itself disagrees by 1%: 128.4 (Monito, XE), 129.56 (open.er-api), 129.75 (Wise). Judge loops by executable quotes, not by "mid".

## Sites checked

| Site | Role | What I saw |
|---|---|---|
| Binance P2P | KES to USDT through M-Pesa or Paybill, 0% fee | Tightest book. Paybill ask 129.12 to 129.26, M-Pesa bid 129.00 to 129.08. |
| Bybit P2P | same | Real ask 129.52, bid 128.76 (0.6% spread). |
| OKX P2P | same | Top-1 only: ask 129.64 to 129.79, bid 128.95 to 129.00. Limits unchecked. |
| KuCoin, HTX, Bitget P2P | same | Asks 132 to 133.6 and thin. Unusable. |
| Raenest | USD/GBP/EUR accounts; accepts USDT and USDC with instant conversion to USD ($1 fee, Tron $2); KES payout $1 | USD→KES rate is not public. Break-even above. |
| PayPal | USD; M-Pesa withdrawal 3%, M-Pesa top-up 4% | A round trip through M-Pesa costs 7%. |
| Instarem, Taptap Send, XE, Wise, Western Union | Remitters into Kenya (sender abroad) | KES per $1,000: 128,742 / 128,300 / 127,832 / 127,442 / 126,917 |
| MoneyGram, WorldRemit, Remitly | First-transfer promos (new customers, sender abroad) | KES per $1,000: 132,100 / 130,715 / 129,900 |
| Binance and Kraken spot | USDT, BTC, ETH, SOL, XRP, LTC, USDC triangles | Gross edges of 1 to 5 bps against fees of 10 to 40 bps. |

Not checked: Noones, Paxful, Yellow Card, AirTM, Payoneer, Skrill, Neteller, and depth on MEXC and Gate P2P.

## What would make a loop worth running

Alert only when all of these hold, and the edge still has to beat about 5 bps of drift over a 20 to 40 minute P2P settlement:

- Binance best sized bid is at or above the best sized ask (Paybill in, M-Pesa out). Today the gap is 0.03% to 0.2%.
- Raenest shows at least 129.48 KES per USD for $3,000 (129.77 for $1,000).
- A PayPal buyer pays at least 1.03 USD per USDT.
- A Binance spot triangle shows at least 30 bps gross.

## Cheapest routes today (no loop needed)

- **KES into Raenest dollars:** buy USDT on Binance Paybill (129.12 to 129.26), send by BEP20 (0.30 USDT), Raenest charges $1. That is 0.2% to 0.5% under the public reference rates plus $1.30 fixed, and beats any bank route I found.
- **Raenest USD into KES:** Raenest cannot send USDT out, so its own quote is the route. Compare it with the 129.48 break-even and with PayPal's 3%.
- **PayPal USD into KES:** 3% on PayPal's rate. The Equity-PayPal alternative is reported at 1.5% plus an FX margin, so it is no better.
- **If the sender is abroad:** Instarem is the best non-promo rate (0.78% markup). Wise's own quote costs 1.8% on $1,000.

## Rules and risk

- **Kenya tax.** Deloitte Kenya (Oct 2025) says the Finance Act 2025 repealed the 3% Digital Asset Tax and added a 10% excise on VASP fees. One generic aggregator still lists the 3% tax, so confirm with an adviser. The Finance Act 2026 (assent 23 Jun 2026, effective 1 Jul 2026) keeps the 10% excise and requires VASPs to file annual user reports with KRA, with cross-border information exchange. Trading profit may count as taxable income.
- **Enforcement.** Around 20 to 21 Apr 2026 the DCI had Binance accounts frozen in Kenya, and users reported P2P funds stuck (TechCabal, Business Daily). Later press reports I found through search but did not open say some users stayed locked out for more than two months with no court order shown. A Binance P2P trader was detained in Nairobi for seven days in May 2026 in an investment-scam case (CoinAlertNews).
- **Raenest.** Terms (Feb 2025) convert received stablecoins to USD automatically and let Raenest place a "Quarantine" hold on incoming transfers it suspects, so funds can sit unconverted until cleared.
- **PayPal.** The Acceptable Use Policy bars currency-exchange activity and lets PayPal reverse transactions, hold funds and limit accounts.
- **M-Pesa.** Safaricom's limits are KES 250,000 per transaction (PayPal's service is quoted at KES 150,000 to 250,000), KES 500,000 per day and KES 500,000 wallet balance. Pay Bill shows no customer charge; send-money does.
- **Pattern risk.** Fast round trips across different counterparties look like layering to an AML team. That matters more during an active crackdown.

## Method and limits

- The sandbox network policy blocked every exchange and FX host, so I read public pages and JSON through Firecrawl, Exa and WebSearch. Nothing here came from an authenticated account.
- Asks and bids come from different minutes (bids 05:36 and 06:15, asks 05:35 and 06:20), so the best-case -0.03% is good to about plus or minus 0.05%.
- Raenest's KES conversion fee and rate, the PayPal buyer bid (aggregator top-1, rounded to cents) and OKX depth are the weakest inputs.
- Live mode: the FX, Wise, Binance spot and Kraken parsers are tested on real responses. The Binance, Bybit and OKX P2P calls are unverified because those hosts are blocked here.

## Questions for you

1. Do you live and bank in Kenya or abroad? Abroad opens the remitter promos and closes some P2P options.
2. What size per month? The Raenest loop clears its fixed fees only above about $2,200 at the er-api mid.
3. Is the goal profit from loops or the lowest-cost conversion? For the second, the route list above is the answer.
4. What does Raenest show for USD to KES at your usual amount? That one number decides the only conditional loop.
5. Which of Binance, Bybit and OKX are verified for you, and did the April freezes touch your account?
6. Should I wire the scanner to alerts? It needs these hosts allowed: `api.wise.com, open.er-api.com, p2p.binance.com, data-api.binance.vision, api2.bybit.com, www.okx.com, api.kraken.com`.

## Reproduce

```
python3 -m unittest discover -s tests
python3 -m arbscan --snapshot data/snapshot_2026-10-03.json --sizes 300 1000 3000
python3 -m arbscan --snapshot data/snapshot_2026-10-03.json --mid wise --sizes 1000 3000
python3 -m arbscan --snapshot data/snapshot_2026-10-03.json --live --write-snapshot data/live.json   # after allowing the hosts
```

Raw outputs: `research/scan-output-2026-10-03.md`, `research/scan-output-2026-10-03-wise-mid.md`. Raw notes: `research/raw-notes-2026-10-03.md`.

## Sources

- Rates: [open.er-api.com USD](https://open.er-api.com/v6/latest/USD), Wise comparison API ([USD to KES](https://api.wise.com/v4/comparisons/?sourceCurrency=USD&targetCurrency=KES&sendAmount=1000), [GBP to KES](https://api.wise.com/v4/comparisons/?sourceCurrency=GBP&targetCurrency=KES&sendAmount=1000)), Monito ([USD](https://www.monito.com/en/compare/transfer/us/ke/usd/kes/1000), [GBP](https://www.monito.com/en/compare/transfer/gb/ke/gbp/kes/1000))
- P2P books: [Binance KES M-Pesa](https://p2p.binance.com/en/trade/MPesaKenya/USDT?fiat=KES), [Binance Paybill](https://p2p.binance.com/en/trade/buy/USDT?fiat=KES&payment=MpesaPaybill), [Bybit KES](https://www.bybit.com/en/p2p/buy/USDT/KES), [P2P.Army KES](https://p2p.army/en/p2p/prices/binance/KES/USDT), [OpenRate KES](https://openrate.live/p2p/markets/kes)
- Spot: [Binance market data](https://data-api.binance.vision/api/v3/ticker/bookTicker), [Kraken ticker](https://api.kraken.com/0/public/Ticker?pair=XBTUSD)
- Raenest: [Kenya fees](https://help.raenest.com/en/articles/16170422-kenya-fees-for-receiving-sending-money), [payout fees](https://help.raenest.com/en/articles/9229531-our-supported-payout-countries-currency-and-fees), [deposit charges](https://help.raenest.com/en/articles/6382330-bank-accounts-deposit-charges-on-raenest), [conversion fees](https://help.raenest.com/en/articles/13285320-conversion-fees-on-raenest), [Nigeria pricing update](https://www.raenest.com/blog/raenest-pricing-update-for-nigeria-weve-reduced-our-deposit-and-conversion-fees----now-the-best-in-the-market), [terms](https://www.raenest.com/terms-of-service)
- PayPal and M-Pesa: [Techweez](https://techweez.com/2025/05/12/how-to-withdraw-funds-from-paypal-to-m-pesa-in-kenya/), [Nash Thuo](https://nashthuo.com/paypal-mpesa-charges/), [paybillke](https://paybillke.com/guides/paypal-fees-kenya), [PayPal Acceptable Use Policy](https://www.paypal.com/us/legalhub/paypal/acceptableuse-full), [Safaricom charges](https://www.safaricom.co.ke/personal/m-pesa/mpesa-charges)
- Kenya law and enforcement: [EY on the Finance Act 2026](https://www.ey.com/en_gl/technical/tax-alerts/kenya-enacts-finance-act-2026), [Deloitte Kenya](https://www.deloitte.com/ke/en/services/tax/analysis/excise-duty-meets-crypto-the-legislative-gaps-kenya-must-close.html), [TechCabal on the freezes](https://techcabal.com/2026/04/21/why-kenyan-authorities-froze-binance-user-accounts/), [Business Daily](https://www.businessdailyafrica.com/bd/markets/currencies/kenya-freezes-binance-accounts-in-money-laundering-purge-5432978), [CoinAlertNews on the detained trader](https://coinalertnews.com/news/2026/05/07/crypto-fraud-crackdown-kenya-uk)
- Fees: Binance USDT withdrawal fees by network ([withdrawalfees.com](https://withdrawalfees.com/exchanges/binance))
