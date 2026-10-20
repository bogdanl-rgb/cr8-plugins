# Sample files

Everything in this folder is synthetic sample data. The companies are fictional: Sample Co 0001 to Sample Co 0999, Outside Co 01 to 05 and Sample Community 01 (the review-group example), all with domains under `.example`. The owners are "Owner A" to "Owner C". The placeholder names ("Stealth AI Startup", "Multiple Companies", "Angel Investor", "Freelancer") are real, though. They're page names that LinkedIn members list as an employer, not companies. No row comes from a real account.

## Month start, 2 Nov 2026: `signal-list-check`

This one uses `month-start/sample-accounts.csv`, `sample-signals.csv` and `sample-crm-accounts.csv`, with today set to 2 Nov 2026. The CRM file has two rows for Sample Co 0005, a won deal and an older lost one, the way a deals export does. It stays a customer.

## Monday, 9 Nov 2026: `placeholder-page-check`, `list-dose-check`, `warm-account-router`

`monday/` has the Companies export, weekly delivery, site visits, leads, public engagement and the Monday CRM. The Monday sample is dense on purpose, so every route fires at least once. At the planned dose of 10 to 13 paid views a company a month, expect far fewer alerts. The written plan of 10 engaged list companies is there to exercise the code, not as a target. Two ad sets serve list AB, also on purpose, so you can see the check catch it: before you act on the dose check's "used up", check the two aren't bidding against each other.

The leads file writes dates the way LinkedIn's Leads export does, month first (11/2/2026). The placeholder check reads `sample-placeholder-names.txt`, which adds Sample Community 01 to the review group. The router and the dose check also read `expected/master.csv` and `expected/exclusions.txt`. Type these in as a user would:

- Window: 10 Oct to 8 Nov 2026.
- Campaign Manager totals for those dates: 13,710 impressions, 400 clicks.
- Written plan: 10 engaged list companies by week 6. Role that owns what you sell: Head of Marketing.
- Plan mode, the dose check before launch: a target audience of 2,200 for the ad set (`--audience`), $35 a day, $80 per 1,000 views.

## Quarter end, 1 Feb 2027: `signal-list-check`, `references/quarter-end.md`

This one reads `quarter-end/sample-crm-deals.csv` with `expected/master.csv` and `month-start/sample-signals.csv`. That master is the carve-day master, the one written the day you carve out the holdout (the companies that get no ads and no messages all quarter). In real use you save it as `master-carve.csv`. The list went live 2 Nov 2026. The comparison is served B against the holdout, both carved from B.

## Expected answers

`expected/` has every output, including `crm-update.csv`, the file you import into your CRM. Each SKILL.md lists the counts under Test.

Without code, paste one SKILL.md and a short file into any AI and check the sums. The full sample files run to hundreds of rows, too many to add up reliably by hand. The placeholder check with typed totals needs only the 6 named rows.

With Python 3, run these from the plugin folder and compare `out/` with `examples/expected/`:

```
S=skills
E=examples
python3 $S/signal-list-check/scripts/signal_list_check.py --accounts $E/month-start/sample-accounts.csv --signals $E/month-start/sample-signals.csv --crm $E/month-start/sample-crm-accounts.csv --today 2026-11-02 --out out
python3 $S/placeholder-page-check/scripts/placeholder_check.py --export $E/monday/sample-companies-export.csv --window "2026-10-10 to 2026-11-08" --total-impressions 13710 --total-clicks 400 --names $E/sample-placeholder-names.txt --out out
python3 $S/list-dose-check/scripts/dose_check.py --delivery $E/monday/sample-weekly-delivery.csv --companies $E/monday/sample-companies-export.csv --master out/master.csv --out out
python3 $S/list-dose-check/scripts/dose_check.py --plan --audience 2200 --daily 35 --price 80 --out out
python3 $S/warm-account-router/scripts/route.py --export $E/monday/sample-companies-export.csv --master out/master.csv --exclusions out/exclusions.txt --crm $E/monday/sample-crm-accounts.csv --visits $E/monday/sample-site-visits.csv --leads $E/monday/sample-leads.csv --public $E/monday/sample-public-engagement.csv --dose out/dose.csv --placeholder out/placeholder-summary.csv --today 2026-11-09 --plan-engaged 10 --owner-role "Head of Marketing" --out out
python3 $S/signal-list-check/scripts/signal_list_check.py --retrain $E/quarter-end/sample-crm-deals.csv --signals $E/month-start/sample-signals.csv --master out/master.csv --since 2026-11-02 --today 2027-02-01 --out out
```

The sample has no company in cooldown and no lost deal without a new signal. One A company, Sample Co 0901, is a lost deal you wrote to in January. It stays on `a-queue.csv` because its signals are newer.
