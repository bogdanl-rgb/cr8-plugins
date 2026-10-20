---
name: signal-list-check
description: Sorts a target company list into A, B and C lists by how many different dated, public buying signals each company has, carves a holdout that never sees ads, writes upload and exclusion files in LinkedIn's company-list template and checks LinkedIn's 300-member serving minimum. Use when someone asks whether their list is warm or only a fit list, which target companies have a reason to buy now, before uploading a company list, at a monthly list refresh, or at quarter end to see which signals sat on won deals. Needs a company list and one row per signal with an evidence link.
license: CC-BY-4.0 (text), MIT (script). Credit Bogdan Liutic, CR8 (cr8.eco).
compatibility: Any AI with a code tool, on a full export. With no code tool, paste a short file (about 100 rows) and check the sums. Python 3 script in scripts/ for any size.
metadata:
  author: Bogdan Liutic, cr8.eco
  version: "1.0.0"
---

# Signal list check

Built by Bogdan Liutic, CR8 (cr8.eco). Version 1.0.0, 21 Oct 2026. The rules it checks: a company with a dated signal runs warm (my ABM list line on "Penetration and saturation"), and "Audience size".

## What this answers

Is your list warm, or only a fit list? A signal is something a company did in public that says why now. A company with 2 or more different fresh signals goes on the A list. Exactly 1 puts it on B. With none, it stays on C. That's fit only, a company that matches your buyer profile and has no signal yet. A and B run the warm band, so their people see your ads more often. C runs the cold band.

At quarter end it also reads which signals sat on won deals. That part lives in `references/quarter-end.md`.

## What you need

1. `accounts.csv`, one row a company: `company, domain, linkedin_company_url, country, employees, fit_ok, exclude_reason`. `fit_ok` is true when the company fits your buyer profile. `exclude_reason` is `competitor`, `employee` or empty.
2. `signals.csv`, one row a signal: `domain, signal_key, signal_date, evidence_url`. Only rows you are allowed to use: `references/signal-menu-starter.md`. This check never fetches signals.
3. `crm-accounts.csv`: `company, domain, deal_stage, owner, stage_date, last_outbound_date`, your stages mapped to `won`, `open`, `lost`, `none`. `stage_date` is the day the deal reached that stage. One row a company: a deals export has one row a deal, so keep the strongest stage per company, won, then open, then lost, then none.
4. Today's date, and at a refresh inside the quarter, this quarter's `holdout.csv`.

Write dates as 2026-11-02. A date like 3/4/2026 can mean 3 April or 4 March, so the script reads it only with `--month-first`. It stops on a CRM date it can't read.

If a column is missing, ask. Do not guess.

## Rules it applies

| rule | value | source | when it changes |
|---|---|---|---|
| A, B, C | A: 2 or more different signal keys. B: exactly 1. C: fit only. One key twice is one signal | my method | Never inside a quarter |
| No evidence, no signal | An empty `evidence_url` drops the row | my rule | Never |
| Windows | `new_leader` 90 days, `job_post_names_tool` 45, `hiring_for_role` 45, `funding` 90, `product_launch` 60, `ad_alert` 30, any other key 60 | my defaults, not measured | Your own measured window |
| Holdout | 10% of the list or 100 companies, whichever is larger, from B only. No ads and no messages for the quarter. Never over half of B, and never so large that A plus served B falls under 300 rows. A holdout under 50 companies: none this quarter | my method. The 50: my default | A new quarter |
| Upload and serving | 300 rows to upload. Serves once 300 members match, not 300 companies. 1,000 or more companies recommended. Matching up to 48 hours, on rare occasions longer | LinkedIn help a423102, read 17 Oct 2026 | LinkedIn changes it |
| EEA and Switzerland | Only members who opted in are matched, so lists can come out smaller | LinkedIn help a424450, read 17 Oct 2026 | LinkedIn changes it |
| Size I build | 1,000 companies or more a list, 10,000 better | my default | Your market |

## Steps

1. Remove companies in this order, counting each reason: a repeated domain (keep the first row), `won`, `open`, any `exclude_reason`, `fit_ok` not true. Then any company whose name, after lowercasing, deleting text in brackets and turning anything not a letter or digit into a space, is one of: Stealth AI Startup, Stealth Startup, Stealth, Multiple Companies, Various Companies, Angel Investor, Freelancer, Self-employed, Something new, Confidential. These are the exclude group of `placeholder-page-check`. Removed names never appear in any output.
2. Compare domains in lowercase, without `https://`, `www.` or a path. Keep signal rows whose domain is still on the list. Drop a row with an empty `evidence_url`, a date after today, or a date you cannot read.
3. Age = today minus `signal_date`, in days. A signal counts while its age is less than its window. On `signal_date` + window it expires.
4. Per company, count the different `signal_key` values left, in lowercase. A key seen twice keeps its newest date and that row's evidence link.
5. Split: A at 2 or more, B at exactly 1, C at 0.
6. Holdout. With this quarter's `holdout.csv`, keep those companies held out wherever they sit now, and carve nothing new. Without it: N = 10% of the companies left after step 1, rounded down, or 100 if that is larger. Then N = the smallest of N, half the B count (rounded down), and A + B minus 300. If N is under 50, carve none and say: "No holdout this quarter: the warm list can't spare 50 companies and still serve." Otherwise sort the B companies by domain, A to Z, and number them from 1. Take row 1 + floor(i x B count / N) for i = 0, 1, 2 and on to N minus 1. Save that day's `master.csv` as `master-carve.csv` and keep it all quarter.
7. Uploads in LinkedIn's 10-column template: `companyname, companywebsite, companyemaildomain, linkedincompanypageurl, stocksymbol, industry, city, state, companycountry, zipcode`. Fill the name, the domain (as website and email domain), the page URL and the country. Leave the rest empty. Leave the holdout out. If A and served B each reach 300 rows, write `upload-a.csv` and `upload-b.csv`. If not, A rides with B in `upload-ab.csv`. Under 300 rows, say so: widen the signal set, or run the whole list cold, as a fit list. Never add C companies to it, which would put them on the warm dose. Write `upload-c.csv` and flag it under 300.
8. Exclusions in the same template: `exclude-holdout.csv` (the holdout) and `exclude-crm.csv` (customers and open deals). Upload each once and add both as excluded company lists on every other ad set in the account, so the holdout sees no ad from any of them.
9. Warm share = (A + B) / all companies, one decimal. Verdict: when A plus served B holds 300 rows or more, the list is warm. Under 300 rows there is no warm list yet: widen the signal set, or run the whole list cold, as a fit list (my line on "Audience size").
10. Drop date. Per key, its expiry = newest date + window. B drops to C on its one expiry. A drops to B on the second-latest of its expiries, when one signal is left.
11. `a-list-queue.csv`, the A list for the person. Rank each company by its best signal: `new_leader`, `job_post_names_tool`, `funding`, `hiring_for_role`, `product_launch`, then other keys A to Z. Ties: that signal's newest date first, then domain.
12. Write `master.csv`: `company, domain, linkedin_company_url, employees, list, signals, signal_dates, evidence_urls, holdout, drops_list_on`. Signals in the step 11 order, joined with " | ". Sort by list, then domain. Write `holdout.csv` (`company, domain, list`) and `list-report.md`.
13. Ask for each list's matched member count 48 hours after upload. Under 300, it does not serve.

## Answer

```
460 of 988 have a dated signal: warm
528 fit only: cold until a signal
100 held back from B as the test
Rule: Penetration and saturation, ABM list line. Lists and holdout: Bogdan Liutic, CR8 (cr8.eco). Floors: LinkedIn help a423102, read 17 Oct 2026.
```

Then `list-report.md`, with the A, B and C counts and the upload files.

## Say this out loud

- C is a fit list, so it runs the cold band like any fit audience.
- A made-up example: if 1 company in 200 books a meeting in a quarter, a holdout of 100 expects half a meeting. So only read it at quarter end, served B against the holdout, both carved from B.
- At 1,000 companies, 3 in 10 need a dated signal before the list runs warm, and 7 in 20 before it can spare a holdout.
- A company moves down a list at the next monthly refresh. And a replaced list takes up to 48 hours to match again.

## Limits

- LinkedIn doesn't publish a typical match rate, so type in your matched count.
- Watch for false positives: a sector or regulation tag on its own, duplicate rows, namesakes, a head office outside your country, a job post placed by a recruiting firm.
- This check doesn't fetch, enrich or upload anything. You do the upload yourself in Campaign Manager: Plan, Audiences, Create audience, Matched Audience, Company / Contact.

## Do not

- Show a removed company anywhere, not even greyed out.
- Serve the holdout, write to it, or carve a new one inside the quarter.

## Test

`examples/month-start/`, today 2 Nov 2026, synthetic. Expected: 12 removed (customer 5, open deal 4, competitor 2, placeholder page 1). Sample Co 0005 has a won row and an older lost row, and stays a customer. 988 companies: 40 A, 420 B, 528 C. Of 519 signal rows, 512 kept (no evidence link 1, expired 2, off the list 4). Holdout 100, as 10% of 988 is 98.8. `upload-ab.csv` 360 rows, `upload-c.csv` 528. `exclude-holdout.csv` 100 rows, `exclude-crm.csv` 9. Warm share 460 of 988 (46.6%), and A plus served B is 360 rows, so the verdict is warm. Edge cases: sample0120 one key twice (B), sample0130 one expired key (B), sample0140 no evidence (C), sample0150 expires on the day (C). Sample Co 0400 is held out. See `examples/expected/`. Script: `python3 scripts/signal_list_check.py --help`.

## Provenance

- A, B and C, the holdout, the signal order: my method. Windows, the list size and the 50-company holdout floor: my defaults, not measured.
- LinkedIn's floors and the EEA rule: help a423102 and a424450, read 17 Oct 2026.
- Test numbers: synthetic sample files.
