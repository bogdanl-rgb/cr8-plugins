# Quarter end: which signals sat on won deals

This is part of `signal-list-check`. Run it at quarter end, and again every time a deal closes.

## What you need

- `crm-deals.csv`: `company, domain, deal_stage, first_call_date`, stages mapped to `won`, `lost`, `open`.
- The date the list went live.
- The `master.csv` written the day the holdout was carved (`master-carve.csv`), and `signals.csv`. Not a later refresh. Ad alerts and new signals move companies into B after the carve, and only the carve-day groups compare fairly.

## Steps

1. Count first calls dated from the day the list went live to today. Put each company in one group: A, B served, holdout or C. Calls with companies off the list, calls before the list went live and calls with no date, or a date after today, are counted apart and kept out of the comparison.
2. Print B served against the holdout, both carved from B, as two counts with both sizes. Then the holdout count you would expect at the served B rate: B served calls x holdout size / B served size, one decimal. Never a percentage gain.
3. Print A and C for reference only. They differed from B before the first ad, so neither is compared with the holdout.
4. For each company with a call, list the signal keys dated before its first call and still inside their window on that day. Count companies, not rows, per key and deal stage.
5. For every other list company outside the holdout, count its keys as "on the list, no call".
6. Under 5 won deals, propose no change. From 5, propose the table order: most won first, then fewest lost. A person decides.

## Say this out loud

- A made-up example: if 1 company in 200 books a meeting in a quarter, a holdout of 100 expects half a meeting. So only a gap of several meetings means anything.
- At that rate, with the sample's 320 served B companies against 100 held out, the holdout catches a 5x gap within a year. A 2x gap can take three years or more. It guards against a big false belief. It doesn't measure lift.
- Don't compare engaged companies with unengaged ones. The engaged ones were already warmer before the first ad.
- A won company had other reasons to buy too. The table shows what was there, not what caused it.

## Test

`examples/quarter-end/sample-crm-deals.csv` with `examples/expected/master.csv` and `examples/month-start/sample-signals.csv`. Live 2 Nov 2026, today 1 Feb 2027. Expected: B served 2 of 320, holdout 0 of 100, expected 2 x 100 / 320 = 0.6. A 2 of 40, C 1 of 528. 1 call before the list went live. 2 won deals, so no change. See `examples/expected/retrain-report.md`.

Script: `python3 scripts/signal_list_check.py --retrain crm-deals.csv --signals signals.csv --master master-carve.csv --since 2026-11-02 --today 2027-02-01 --out out`. Write dates as 2027-02-01. A date the script cannot read safely stops the run.
