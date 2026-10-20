# Signal list check, 2 Nov 2026

Files read: sample-accounts.csv (1,000 rows), sample-signals.csv (519 rows), sample-crm-accounts.csv (16 rows).

## Verdict

460 of 988 companies (46.6%) have a dated reason to buy now (A and B): warm.
528 are fit only (C): cold until a signal moves them in.
100 warm companies held back as the test, no ads and no messages.

988 companies: 40 A, 420 B, 528 C. A rides with B: 360 rows, over 300.

## Removed before the split (names never shown)

customer 5, open deal 4, competitor 2, placeholder page 1. Total 12.

## Signal rows

Read 519. Kept 512. Dropped: no evidence link 1, expired 2, company not on the list, or removed 4.
One signal firing twice is still one signal: each company counts different signal keys.

## Holdout

Size: 100. Rule: 10% of the list or 100 companies, whichever is larger, from B only, never over half of B, and never so large that A plus served B falls under 300 rows. 10% of 988 is 98.8. Picked: sort B by domain, A to Z, and take row 1 + floor(i x 420 / 100) for i = 0 to 99.
Take an example rate, not a forecast: if 1 company in 200 books a meeting in a quarter, a holdout of 100 expects half a meeting. Read it only at quarter end, as two counts with both list sizes, never as a lift.
Keep holdout.csv all quarter. At each monthly refresh, pass it back in with --holdout-in. Also save this master.csv as master-carve.csv: the quarter-end count compares the groups of this day.

## Upload files (LinkedIn's company template, holdout removed)

upload-ab.csv: 360 rows (A 40 + B 320 served).
upload-c.csv: 528 rows.
exclude-holdout.csv: 100 rows. exclude-crm.csv: 9 rows (customers and open deals). Upload each once and add both as excluded company lists on every other ad set in the account.

LinkedIn takes a company list from 300 rows and serves it once 300 members match, not 300 companies. It recommends 1,000 or more companies. Matching can take up to 48 hours, on rare occasions longer. In the EEA and Switzerland only members who opted in are matched, so those lists come out smaller.
Upload in Campaign Manager: Plan, Audiences, Create audience, Matched Audience, Company / Contact. You upload. This check does not.
Next: 48 hours after upload, type the matched member count of each list. Under 300, it does not serve.

## For the person

a-list-queue.csv: 40 A companies in signal order (new leader, then a job ad that names the tools, then funding, then the rest, newest first).

## Next dates

First drop: 3 Nov 2026, when 12 companies leave their list.
Drops in the next 30 days: 232. Each row's date sits in master.csv, drops_list_on.
Drops take effect at the next monthly refresh. A replaced list takes up to 48 hours to match again.

## Freshness windows used (my defaults, not measured)

new_leader 90 days, job_post_names_tool 45 days, funding 90 days, hiring_for_role 45 days, product_launch 60 days, ad_alert 30 days, any other key 60 days.
A signal counts while it is younger than its window. On signal date + window it expires.
