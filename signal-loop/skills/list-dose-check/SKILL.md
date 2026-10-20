---
name: list-dose-check
description: Checks whether each LinkedIn Ads ad set on a company list is still buying new people or showing the same ones again. It reads views a person a month, share of the list reached, new people a week and price per 1,000 views, against a warm band for signal lists and the cold band for fit-only lists. It also plans the monthly spend a list can hold and how many ads an ad set can feed. Use when someone asks if their list is too small for their budget, whether to add budget, whether frequency is OK on an ABM list, or how much a list can absorb. Reach is typed from the Delivery columns.
license: CC-BY-4.0 (text), MIT (script). Credit Bogdan Liutic, CR8 (cr8.eco).
compatibility: Any AI with a code tool, on a full export. With no code tool, paste a short file (about 100 rows) and check the sums. Python 3 script in scripts/ for any size.
metadata:
  author: Bogdan Liutic, cr8.eco
  version: "1.0.0"
---

# List dose check

Built by Bogdan Liutic, CR8 (cr8.eco). Version 1.0.0, 21 Oct 2026. The rules it checks: a signal list runs warm, about 5 views a person a month (my ABM list line on "Penetration and saturation"), and "Audience size" in plan mode.

## What this answers

How much budget can your list hold? Once a list runs out of new people, extra money buys the same people again. This check tells you, ad set by ad set, whether the dose is on plan and when the list is used up. The dose is how many times each person sees your ads in a month. It's also the test that can prove my own dose wrong for your account. Good. I'd rather know.

## What you need

1. `weekly-delivery.csv`, one row per ad set per week, typed each Monday from the reporting table, Columns, Delivery: `week_start, list, ad_set_name, spend_week, impressions_week, impressions_30d, reach_30d, reach_cumulative, audience_size`. Optional: `frequency_90d`, and `budget_week` for an ad set on a manual bid.
   - `impressions_30d`, `reach_30d`: the last 30 days. `reach_cumulative`: since the ad set's first day, or the last 92 days once it is older (Campaign Manager shows audience penetration for at most 92 days at a time, so keep reach to the same span). `spend_week`, `impressions_week`: last Monday to Sunday. `frequency_90d`: Average frequency over the last 90 days. `budget_week`: the daily budget x 7.
   - `audience_size`: the target audience size Campaign Manager shows for that ad set (your list plus job titles plus location). Not the matched count on the Audiences page: on a company list that count holds everyone LinkedIn finds at those companies.
   - `list`: A, B, AB or C. Split an ad set that mixes C with A or B. Never start with a part week.
2. Optional, for a hand-off list: the Companies export from the ad set's first day, and `master.csv` from `signal-list-check`.
3. Plan mode: the ad set's target audience size, the daily budget and your own price per 1,000 views. Never a benchmark price.

If a value is missing, ask. Do not guess.

## Rules it applies

| rule | value | source | when it changes |
|---|---|---|---|
| Warm band (A, B, AB) | About 5 views a person a month. Under 4: under dose. 8 or more: look at CTR and price first. Over 90 days that reads as up to 15 if the same people are reached every month, about 7 to 8 when each month mostly reaches different people | my plan, not measured. Band edges: my defaults. The 90-day reading: arithmetic on the plan | Your numbers at day 14 |
| Cold band (C) | Under 3 to 5 views a person in 90 days | my default for fit-only lists, the same as the Standard's example cold line, read 17 Oct 2026 | Your own 90-day numbers |
| Used up | New people under half of the week before, two weeks running, while one holds: the price per 1,000 views is 2 times the first week's or more (automated bid), this week's spend is under 70% of `budget_week` (manual bid), or 70% or more of the list is reached | my proposal, not yet tested across accounts | More accounts read |
| Dose budget | Target audience x 40% to 50% reachable in a month x 5 / 1,000 x your price | my plan, not measured | Your numbers at day 14 |
| One list, one dose | Two ad sets on one list share one dose. Rotate the offer in as an ad, not as a second ad set. A gets its own ad set only once A and the served B each have 300 rows | my plan | Your numbers at day 14 |
| Daily minimum | $10 a day per ad set | LinkedIn's budget page, which is no longer in the help center, so unconfirmed. Seen on my own account, 10 a day in euros, Sep 2026 | LinkedIn changes it |
| Ad cap | Daily spend x 14 / price per 1,000 views, rounded down: about 1,000 views an ad in 14 days, my point for reading an ad. Under 2: merge ad sets or add budget | my default, not measured | When your own ads' numbers settle |
| Frequency cap | For now, 3 to 30 views a member in 7 days, currently offered only on brand awareness ad sets, and not on every account yet | LinkedIn help a6514218, read 17 Oct 2026 | LinkedIn changes it |

## Steps

Show the arithmetic.

1. Per ad set, sort rows by `week_start`. The latest row is this week.
2. Views a person a month = `impressions_30d` / `reach_30d`. It equals Average frequency for those 30 days. Print one decimal, but compare the unrounded number with the bands.
3. Share reached = `reach_cumulative` / `audience_size` x 100.
4. New people each week = that week's `reach_cumulative` minus the week before. The first row's = its `reach_cumulative`. If LinkedIn restated reach downward, set that week to 0 and say so.
5. Price per 1,000 views each week = `spend_week` / `impressions_week` x 1,000.
6. Used up when there are 3 or more rows, this week's new people are under half of last week's, last week's are under half of the week before, and one of these holds: this week's price is at least 2 times the first row's, this week's spend is under 70% of `budget_week`, or the share reached is 70% or more.
7. Verdict, first match wins:
   - Used up: add no budget. Hand the unreached companies to a person, or start a second signal list from the same market. Two ad sets on one list share one dose. If another ad set targets the same list, check they aren't bidding against each other before you call the list used up, and move the second one into the first as an ad. The script doesn't group ad sets by list yet, so read the `list` column yourself.
   - Warm, under 4: under dose. Raise the budget or the bid.
   - Warm, 4 to under 8: on plan. Hold.
   - Warm, 8 or more: look at CTR and price before adding anything.
   - Cold: views in 90 days = `frequency_90d`. When it is empty, use views a month x 3 and label it an upper bound: it assumes the same people are reached every month. Type `frequency_90d` for the real reading. Under 5: on plan, hold. 5 or more: widen reach and add no frequency, but on the upper bound get `frequency_90d` first. Print the share reached next to every cold verdict: on the cold band, low reach is the usual problem.
8. Hand-off list, only when an ad set is used up and both optional files are given. Take the companies on its lists in `master.csv`, holdout out. Find each one's export row by page URL, or else by exact name. Keep those whose `Paid impressions` is blank or zero, or that have no row. Order A, B, C, then domain. Write `unreached.csv`. Export Companies from the ad set's first day for this step: a 30-day export calls a company reached 6 weeks ago unreached.
9. Write `dose-report.md` and `dose.csv`.

Plan mode, before launch:

10. Dose budget = target audience x 0.40 to 0.50 x 5 / 1,000 x price, a monthly range. Planned spend = daily x 30.4. Above the range, the list will be used up within weeks: lower the budget, or move the rest of the budget to the C list or a second signal list from the same market. Below it: a smaller list or a lower dose, said before any spend. For a split, by seniority or anything else, run plan mode once per part: each part's ad set needs a target audience of 300 or more, and its own budget must hold the dose. Two or more ad sets on one list split one dose budget between them.
11. Ad cap = daily x 14 / price, rounded down. Example: $50 a day at $100 per 1,000 views feeds 7 live ads. Use what the ad set really spends, not the budget field.
12. Ad sets the dose holds = the low end of the monthly range / 30.4 / 10, rounded down. Say: "At LinkedIn's $10 a day minimum, your dose budget holds {n} ad sets." At 1, run one ad set on the list and rotate the offer in as an ad. At 0, even one ad set at the minimum runs over the dose: add companies as fresh signals come in, or say the higher dose out loud before any spend. The script doesn't print this line yet, so work it out from its monthly range.

## Answer

```
2 ad sets share one list's dose
AB offer: used up, fold it into consideration
AB consideration: on plan, hold
C awareness: on plan, hold
Rule: Penetration and saturation, ABM list line. Warm band: Bogdan Liutic, CR8 (cr8.eco), a plan, not measured. Cold band: my default, the same as the Standard's example, read 17 Oct 2026.
```

## Say this out loud

- The 5 a month is my plan. I haven't measured it. Over 90 days it reads as up to 15, and about 7 to 8 when each month mostly reaches different people.
- Two ad sets on one list share one dose. If another ad set targets the same list, check they aren't bidding against each other before you call the list used up.
- Once a list runs out of new people, the price per 1,000 views climbs as the same people see your ads again. Read it at day 14.
- The dose caps what one list can absorb. If your lists together hold less than you need, add a second signal list, or let the C list carry the rest. I'd never buy more views for the same people.
- If new people fall while the price climbs, or the budget stops spending, the list is used up. Then this check tells you I was wrong for your budget.

## Limits

- Reach, frequency and penetration (the share of your audience reached) are LinkedIn's estimates. LinkedIn says to read them only as a direction.
- Delivery numbers take 24 to 36 hours to settle. So last week's numbers, typed on Monday, run a little short on Sunday. Type them on the same day every week.
- A pause and restart looks like a fall in new people. LinkedIn can also restate spend and reach.
- Ad sets with an industry or title filter have smaller pools, so they use them up sooner.
- The Companies export is account level, so a company reached by any ad set counts as reached.

## Do not

- Add budget to a used-up ad set, read the dose on one week, or change anything in the account.

## Test

`examples/monday/sample-weekly-delivery.csv`, with `sample-companies-export.csv` and `examples/expected/master.csv`, synthetic. Expected:

- AB · offer: used up. New people 410, 190, 85. Price $70, $100, $150, 2.1 times the first week.
- AB · consideration: 6,800 / 1,330 = 5.1 a month. On plan.
- C · awareness: 3,850 / 2,750 = 1.4 a month, x 3 = 4.2 in 90 days at most, an upper bound with no `frequency_90d` typed. On plan. 80.9% of the list reached.
- `unreached.csv`: 48 AB companies (A 3, B 45).
- Both AB ad sets target the same 2,200 people. The sample runs two ad sets on one list on purpose, so you can see the check catch it: before you act on "used up", check the two aren't bidding against each other.
- Plan mode, a target audience of 2,200, $35 a day, $80: the dose holds at $352 to $440 a month. $35 x 30.4 = $1,064 is over it. Ad cap 6. By hand, not in the script's file: $352 / 30.4 = $11.58 a day, so at the $10 a day minimum the dose holds 1 ad set.

See `examples/expected/dose-report.md`, `dose.csv`, `unreached.csv` and `dose-plan.md`. Script: `python3 scripts/dose_check.py --help`. Plan mode takes `--audience` (the ad set's target audience size).

## Provenance

- The 5 a month, the 40% to 50%, the band edges, the used-up flag and the ad cap: my plan and defaults, not measured.
- Cold band: my default for fit-only lists, the same as the Standard's example cold line, read 17 Oct 2026.
- The 90-day reading of 5 a month: arithmetic on the plan. If each month reaches 45% of the list at random, 90 days reach about 83% of it at about 8 views each. As many new people as possible each month gives about 7. The same people every month gives 15.
- $10 a day minimum per ad set: LinkedIn's budget page, which is no longer in the help center, so unconfirmed. Seen on my own account, 10 a day in euros, Sep 2026.
- Frequency cap, Delivery columns modeled and slow to settle, a 92-day range for audience penetration: LinkedIn help a6514218 and a426154, read 17 Oct 2026.
- Test numbers: synthetic sample files.
