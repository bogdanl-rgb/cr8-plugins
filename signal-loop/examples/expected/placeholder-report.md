# Placeholder page check, window 10 Oct to 8 Nov 2026

Source: sample-companies-export.csv, 901 rows.
Shares are against the totals you typed from the Campaign Manager table for the same dates: 13,710 impressions, 400 clicks.

## Verdict

HIGH: 30.0% of paid clicks and 23.3% of paid impressions came from people listed at 4 placeholder page names.
The top company by paid clicks is a placeholder page: Stealth AI Startup, 84 clicks on 2 page rows.
Exclude 4 names, every page that carries each name. Then read the CTR again.

## By name, exclude group

| name | page rows | paid impressions | share | paid clicks | share |
|---|---|---|---|---|---|
| Stealth AI Startup | 2 | 2,000 | 14.6% | 84 | 21.0% |
| Multiple Companies | 1 | 600 | 4.4% | 18 | 4.5% |
| Angel Investor | 1 | 400 | 2.9% | 12 | 3.0% |
| Freelancer | 1 | 200 | 1.5% | 6 | 1.5% |
| all | 5 | 3,200 | 23.3% | 120 | 30.0% |

## Review group (a judgment call, never excluded by default)

Sample Community 01: 1 page row, 300 impressions (2.2%), 9 clicks (2.2%). Compare its CTR with the ad set's own before you decide.
Not in the flag.

## Top 5 companies by paid clicks (page rows with the same name added up)

1. Stealth AI Startup, 84 clicks (placeholder page)
2. Multiple Companies, 18 clicks (placeholder page)
3. Angel Investor, 12 clicks (placeholder page)
4. Sample Co 0014, 10 clicks
5. Sample Community 01, 9 clicks (review group)

## Exclusions (exclusions.txt)

- Stealth AI Startup
- Multiple Companies
- Angel Investor
- Freelancer

In each ad set, search each name in the company exclusions and add every page with that exact name. Write down how many pages you added: the saved list shows names only.
On the exclude list, with no paid numbers in this file: Stealth Startup, Stealth, Various Companies, Self-employed, Something new, Confidential. Excluding them now as well costs nothing.

## Before you act

- The ads did not send clicks to these pages. The people who clicked list them as their employer.
- This export is account level. It cannot say which ad set leaked. Read each ad set's company breakdown for that.
- The harm is the share of money. The CTR may barely move.

## Limits

- LinkedIn leaves out companies under its reporting minimum, so the placeholder counts are floors.
- This file's own sums are 14,449 paid impressions and 180 paid clicks. They are not your account totals: the file drops companies under the minimum and can list one person under two employers.
- Nothing was changed in the account. A person makes every exclusion.

## Rules used

- Bands, proposed from my own account, not measured across accounts: HIGH at 25% or more, MEDIUM from 10% to under 25%, LOW under 10%. With typed totals the flag reads the larger of the click and impression share. Without them, the impression share only.
- Any single exclude name above 5% of impressions is named, even at LOW.
- Exact names only, after lowercasing, dropping text in brackets and turning punctuation into spaces. Never close matches.

Checks by Bogdan Liutic, CR8 (cr8.eco). Want the loop run for you? [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)
