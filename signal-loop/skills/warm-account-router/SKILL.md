---
name: warm-account-router
description: Hands a person the week's short list from a LinkedIn Ads signal list, meaning the A companies to write to in signal order plus one card for any company that engaged far more than the ads explain. Joins ad engagement by company to site visits by company, form fills and your CRM, drafts each card for a person to approve, and writes a file to import into the CRM. Runs the Monday order, placeholder pages first, then the dose, then the ranking. Use on Mondays, or when someone asks which target accounts saw the ads and came back, which ones match open deals, which accounts are hot, or who to write to this week. It never sends anything.
license: CC-BY-4.0 (text), MIT (script). Credit Bogdan Liutic, CR8 (cr8.eco).
compatibility: Any AI with a code tool, on a full export. With no code tool, paste a short file (about 100 rows) and check the sums. Python 3 script in scripts/ for any size.
metadata:
  author: Bogdan Liutic, cr8.eco
  version: "1.0.0"
---

# Warm account router

Built by Bogdan Liutic, CR8 (cr8.eco). Version 1.0.0, 21 Oct 2026. The rule it checks: Hot accounts.

## What this answers

Which companies on your list should a person write to this week, and which ones belong to a deal owner? Count companies on your list, not clicks or people, because LinkedIn reports companies.

## The Monday order

`placeholder-page-check` first: without its `exclusions.txt`, stop. Then `list-dose-check`, optional. Then this skill. Then stop and ask for a yes or a no on each card. On a month's first Monday, run `signal-list-check` before all of it.

## What you need

1. The Companies export, last 30 days (14 days with `--profile small-list`), the same window as the placeholder check (Plan, Companies, Export). Companies Hub needs a Company Page linked to your ad account. Columns used: `Company name, Company page URL, Organic engagements, Paid impressions, Paid clicks, Paid engagements`. Any tool's export with these columns works too.
2. `master.csv` from `signal-list-check`, and `exclusions.txt`.
3. `crm-accounts.csv`: `company, domain, deal_stage, owner, stage_date, last_outbound_date`, stages mapped to `won`, `open`, `lost`, `none`. One row a company: a deals export has one row a deal, so keep the strongest stage per company (won, then open, then lost, then none) and the latest `last_outbound_date` across its rows.
4. Optional, each with dated rows: `site-visits.csv` (`domain, visit_date, page`, company level only). `leads.csv` (`lead_id, created_date, form_id, test_lead, email_domain`). `public-engagement.csv` (`domain, date, what`), typed by a person from their own post notifications, only for people in your target roles and only for posts that are not running as ads.
5. Optional: last week's `router_output.csv`, the plan you wrote before launch (engaged list companies by week 6), replies, meetings, the role that owns what you sell, and the economic buyer at companies of 50 staff or more.

For `leads.csv`, copy the part of `Email address` after the @ into `email_domain`. Then delete every personal column before a cloud AI sees it. The window runs from today minus 30 days to yesterday.

About dates. LinkedIn's Leads export writes `created_date` as 10/2/2026, month first, and the script reads that fine. In every other file, write 2026-10-02. A date like 3/4/2026 can mean 3 April or 4 March, so it stops the run unless you pass `--month-first`. A date that can't be read stops the run too, so no form fill or cooldown gets lost without you noticing.

## Rules it applies

| rule | value | source | when it changes |
|---|---|---|---|
| Alert | 10 or more paid engagements in the window on its own, or 3 or more plus a second signal in the same window | my default, not measured | A list of companies under 50 staff: 4 or more paid clicks in 14 days, my older line (`--profile small-list`, with a 14-day Companies export). The 50 is a proposed cut |
| Paid engagements | Social actions plus clicks to your landing page or LinkedIn Page, on your ads, whether LinkedIn charged for them or not | LinkedIn help a7109308, read 17 Oct 2026 | LinkedIn changes it |
| Second signal | Visits on 2 or more different days (pages under /career, /careers, /job or /jobs do not count), a form fill from the company's domain that is not a test lead, a public engagement row on a post that is not running as an ad. Engagement on a promoted post is ad data: it counts only through the Companies export, never by name | my default | Never without a dated row |
| Watch | 3 to 9 paid engagements, no second signal | my default | With the alert line |
| Smallest count | 3 is also the smallest number the Companies export shows. Below it, the cell is blank | my own Companies export of 5 Sep 2026: no value under 3 in any column | LinkedIn changes its reporting minimum |
| Organic | No paid engagement shown, organic engagements shown: labeled, no alert | my rule | Never |
| Engagement, not impression | An impression is a bid outcome. A click is a decision | my rule | Never |
| Cooldown, cap | 14 days after you last wrote to the company. 5 cards a run | my defaults | Your team's capacity |

## Steps

1. Normalize every company name: lowercase, delete text in brackets, turn anything not a letter or digit into a space, collapse spaces. Drop export rows whose normalized name is in `exclusions.txt`, and count them. Skip rows where all four of `Paid impressions`, `Paid clicks`, `Paid engagements` and `Organic engagements` are blank.
2. Match each row to `master.csv`: `Company page URL` against `linkedin_company_url`, both lowercased, without `https://`, `www.`, a `?` part or the last `/`. Else the exact normalized name. Never a close match. Two pages of one company add up. Then print the match line: "{m} of {n} export rows with numbers matched your list", and list the 10 unmatched rows with the most paid engagements, so a person can spot a list company under another URL or name. Companies Hub uses the named page URL (linkedin.com/company/acme). If your `master.csv` holds numeric URLs, replace them before the first Monday.
3. Off the list: a row whose exact normalized name is a `won` or `open` company in the CRM is flagged "excluded but served". The rest is counted as not on your list. Neither is routed.
4. A holdout company with paid impressions is flagged: check pages that share its name or parent. Never a card.
5. A list company that is `won` in the CRM is dropped and counted.
6. Collect the second signals for the company's domain, each dated inside the window. Classify, first match wins: alert, watch, organic, quiet with a second signal, quiet. 3 is also the smallest number the Companies export shows. Below it, the cell is blank, so a blank paid engagement cell is under LinkedIn's threshold, not zero.
7. Route each alert, first match wins. A company under 10 staff: no card, no note and no list move, because a company row there can point to one person. The ads keep running, and its public signals still put it on the A queue. `open`: a note to the owner, no list move, no outreach. You wrote within 14 days: cooldown, with its end date. `lost`: a card only if `master.csv` shows a public signal dated after `stage_date`, otherwise park. Anything else: a card.
8. Every alert except an open deal or a company under 10 staff moves up a list: C to B, B to A, A stays. Write one `ad_alert` row each to `signals-to-add.csv`, so the next refresh counts it. An `ad_alert` is never named in a message.
9. Rank cards by the list after the move (A, B, C), then paid engagements, most first, then the number of second signals, then domain. Cards 1 to 5 go this week.
10. Roles per card: the role that owns what you sell, then the economic buyer (founder or CEO under 50 staff, from 50 the VP or C-level who owns the budget, or the role you name with `--buyer-role`), then whoever would run it. Timing: under 50 staff, day 0, 3 and 7. 50 to 200, one after another: write to the next person once the last has had 7 days to reply. Over 200, all at once. If you find only two, write to two.
11. Thread check: "not run" until the user pastes who sent the last message to each person, and the date. The message text is not needed, so keep it out of a cloud AI. You wrote last and got silence: park that person.
12. A list companies with no card or note this week, open deals and customers left out, go on the person's queue, `a-queue.csv`, worked from day 7 of serving. Two different dated signals are a company raising its hand in public. That's why A gets a person from day 7, clicked or not, while B and C wait for the ads to work. Each is written to once. Leave out a company with a `last_outbound_date`, or a lost deal, unless a public signal is dated after it, and any company inside its 14-day cooldown. Mark each row "not written yet" or "new signal since you wrote". Signal order as in `a-list-queue.csv`, paid engagements shown, except at a company under 10 staff. Never ranked by impressions.
13. Write `crm-update.csv`, the hand-off to your CRM: one row per card and per note to a deal owner, keyed on the company's website domain, with the list, the route, the date, the owner and the card text. The person deletes the cards they said no to, then imports the file or pastes each row into a task on the company record. This skill never writes to a CRM.
14. Write `router_output.csv`, `weekly-brief.md`, `signals-to-add.csv` and `a-queue.csv`. The brief starts with the order for the week: the cards, then the A queue, then unreached companies from a used-up ad set. Stop. Send nothing.

Card layout and output columns: `references/card-template.md`. Message rules: `references/message-rules.md`.

## Answer

```
39 A companies to write to, in signal order
2 cards: engaged far above the ads
1 note to a deal owner
Rule: Hot accounts. Alert line: Bogdan Liutic, CR8 (cr8.eco), my default, not measured.
```

Then the weekly chain, printed even at zero (engaged against plan, alerts, approved, first messages, first messages the same day as the yes, median hours to a first message, replies, meetings), the checks, the cards and `crm-update.csv`. Engaged: a list company outside the holdout with 3 or more paid engagements shown.

## Say this out loud

- A card names roles, never clickers. LinkedIn doesn't say who clicked.
- One person refreshing can make a company look busy.
- A low match share usually means a file problem. Check the page URLs and names in `master.csv`.

## Limits

- Engagements aren't people. On my own account, 2,061 ad engagements turned out to be about 1,000 people.
- I've seen the Companies export run about 2 days behind. It also blanks values under LinkedIn's reporting minimum. That's why this runs weekly.
- At 5 to 10 people a company, 40% to 50% of them reached and 5 views each, a company sees 10 to 25 paid views a month. So an alert is rare, and it marks a company that engaged far more than the dose predicts. Most Mondays you'll get no card, and the work is the A list. Write the zeros down too.
- A person counts under every current employer, so a company can show up through someone's second job.
- At a company under 10 staff, a company row can point to one person. So the router drafts no card or note for it, doesn't move it up a list, and shows no paid engagements for it on the A queue. Never name the engagement anywhere.
- "Excluded but served" matches the CRM by exact name only. "Acme GmbH" in the CRM never matches "Acme".
- `Organic engagements` counts only your Company Page's posts. Engagement with a person's own posts goes in `public-engagement.csv`.
- I have no outcome proof for the alert line yet. It picks who to look at, not who will buy.
- Vendors, consultancies and competitors engage too. Keep them off the list.

## Do not

- Send, connect, upload or change anything. A person sends from their own account.
- Write to a held-out company, or rank without `exclusions.txt`.

## Test

`examples/monday/` with `expected/master.csv` and `exclusions.txt`, synthetic. Today 9 Nov 2026, plan 10, role Head of Marketing. The leads file uses LinkedIn's own month-first dates, and the CRM holds a second, older lost row for customer Sample Co 0005. Expected: 5 placeholder rows struck. 712 of 719 export rows with numbers matched the list. Alerts: Sample Co 0014 (A, 12 alone, card), 0233 (B, 4 plus a return visit and a like, lost with a signal since, card, B to A), 0517 (C, open deal, note). Watch: 0301 and 0702. Organic: 0820. Quiet with a second signal: 0610. Flags: holdout 0400, customer 0005. 6 off the list, 39 A on the queue (Sample Co 0901, a lost deal you wrote to on 28 Jan 2026, is back with new signals), 5 engaged. `crm-update.csv`: 3 rows, 2 cards and 1 note. See `expected/router_output.csv`, `weekly-brief.md`, `a-queue.csv` and `crm-update.csv`.

## Provenance

- 2,061 engagements became about 1,000 people, Sep 2026: CR8's own account.
- Paid engagements, Companies Hub's Company Page requirement, one person under several employers: LinkedIn help a6884751, a7109308 and a10166020, read 17 Oct 2026.
- 3 as the smallest number shown: my own Companies export of 5 Sep 2026, where no column shows a value under 3.
- The 4 paid clicks in 14 days: my older line. The 50-staff cut for it: proposed, not measured.
- Test numbers: synthetic sample files.
