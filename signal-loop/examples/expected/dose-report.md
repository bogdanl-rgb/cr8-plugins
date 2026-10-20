# List dose check, week of 2 Nov 2026

Source: sample-weekly-delivery.csv, 3 ad sets, 11 weekly rows typed from the Delivery columns.

## Verdict

1 of 3 ad sets is used up.
AB · offer (AB list, warm band): used up. Add no budget. Hand the unreached companies to a person, or start a second signal list from the same market.
AB · consideration (AB list, warm band): on plan. Hold.
C · awareness (C list, cold band): on plan. Hold.

## The numbers

| ad set | list | weeks | views a person a month | share of list reached | new people this week | price per 1,000 views this week | first week |
|---|---|---|---|---|---|---|---|
| AB · offer | AB | 3 | 4.5 | 31.1% | 85 | $150 | $70 |
| AB · consideration | AB | 4 | 5.1 | 60.5% | 90 | $88 | $80 |
| C · awareness | C | 4 | 1.4 | 80.9% | 450 | $63 | $60 |

## How each verdict was reached

AB · offer: new people a week 410, 190, 85. Price per 1,000 views $70, $100, $150.
  Used up: new people fell under half of the week before, two weeks running, and this week's price is 2.1 times the first week's (2 times or more).
AB · consideration: new people a week 900, 220, 120, 90. Price per 1,000 views $80, $82, $85, $88.
  Warm band: about 5 views a person a month planned. 5.1 is between 4 and 8.
C · awareness: new people a week 900, 800, 600, 450. Price per 1,000 views $60, $63, $63, $63.
  Cold band: 1.4 a month x 3 = 4.2 in 90 days at most, an upper bound, under 5. Share of the list reached: 80.9%.

## Unreached companies (unreached.csv)

48 companies on the used-up list show no paid impressions in the Companies export. Hand them to a person, in list order, A first. The export is account level, so a company reached by any ad set counts as reached.
By list: A 3, B 45.

## Before you act

- The 5 a month is my plan, not a measurement. When a list runs out of new people, the price per 1,000 views climbs as the same people see the ads again: read it at day 14.
- On the cold band, low reach is the usual problem, not high frequency. Read the share reached before the views.
- If the price climbs while new people fall, the list is used up, and this check will tell you I was wrong for your budget.

## Limits

- LinkedIn models reach, frequency and audience penetration and says to read them only as a direction. Treat them as estimates.
- A pause and restart looks like a collapse in new people. Check the ad set's history before you act.
- LinkedIn can restate spend after the fact. Use the latest read of each week.
- Ad sets with an industry or title filter have small pools and use them up sooner.
- Without a frequency_90d column, the cold band is read as views a month x 3. Average frequency over the last 90 days, typed from the Delivery columns, gives the 90-day number directly.
- Delivery numbers take 24 to 36 hours to settle, so last week's numbers typed on Monday run a little short on Sunday. Type them on the same day every week.

## Rules used

- Warm band (A, B, AB): about 5 views a person a month, my plan, not measured. Under 4: under dose. 8 or more: look at CTR and price before adding anything. These edges are my defaults.
- Cold band (C): under 3 to 5 views in 90 days, my default for fit-only lists, the same as the Standard's example cold line, read 17 Oct 2026.
- Used up: new people this week under half of last week's, two weeks running, while one of these holds: this week's price per 1,000 views is 2 times the first week's or more (automated bid), this week's spend is under 70% of the weekly budget (manual bid), or 70% or more of the list is reached. Proposed, not yet tested across accounts.
- For now LinkedIn offers a frequency cap (3 to 30 views a member in 7 days) only on brand awareness ad sets, and not every account has it. On every other objective there is no cap you can set: your budget, your bid and the size of your list set the dose.
