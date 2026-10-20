---
name: placeholder-page-check
description: Checks how much of a LinkedIn Ads account's paid clicks and impressions came from people listed at placeholder employer pages such as "Stealth AI Startup", "Multiple Companies" or "Angel Investor", and writes the exact names to exclude. Use when someone asks whether their clicks come from real companies, why the CTR looks good but pipeline does not, where the budget is going, before reading any CTR or cost line on a company list or engagement audience, or when they share a Campaign Manager Companies export.
license: CC-BY-4.0 (text), MIT (script). Credit Bogdan Liutic, CR8 (cr8.eco).
compatibility: Any AI with a code tool, on a full export. With no code tool, paste a short file (about 100 rows) and check the sums. Python 3 script in scripts/ for any size.
metadata:
  author: Bogdan Liutic, cr8.eco
  version: "1.0.0"
---

# Placeholder page check

Built by Bogdan Liutic, CR8 (cr8.eco). Version 1.0.0, 21 Oct 2026. The rule it checks: Placeholder pages.

## What this answers

How many of your paid clicks and impressions came from people who list a placeholder page as their employer, and which exact names should you exclude?

One ad set on my own account got 49% of its clicks from people listed at "Stealth AI Startup". That's a placeholder page people pick instead of a real employer. It was 350 of 708 clicks, 7 Aug to 5 Sep 2026. That set ran broad and cheap: a 176,823-member company list built from engagement data, plus LinkedIn's own engaged-companies segment, at 11% of the suggested bid. My reading: LinkedIn's segment scored the page as an engaged company and served its members. Read any rate before this check and it counts those clicks too.

## What you need

1. The Companies export. In Campaign Manager: Plan, then Companies (Companies Hub). Companies Hub needs a Company Page linked to your ad account. Set the date range, then Export. Its 13 columns: `Company name, Company page URL, Engagement level, Organic impressions, Organic engagements, Paid impressions, Paid clicks, Paid engagements, Paid video views, Paid conversions, Paid leads, Paid qualified leads, Cost per qualified lead`. This check reads `Company name`, `Company page URL`, `Paid impressions`, `Paid clicks` and `Paid engagements`. Any tool's export with these columns works too.
2. The date range you set. The file does not carry it.
3. Your Impressions and Clicks for the same dates and scope, from the Campaign Manager reporting table. The export's own sums are not your totals (see Limits).
4. `references/placeholder-names.txt`: an exclude group and a review group. The review group starts empty: add the communities, accelerators and investor groups your account shows. Edit both as you learn.

Checking one ad set? Filter Companies Hub by it before you export, and type its totals. I haven't checked that the export keeps the filter, so compare one total with the ad set's row once. Or paste the Company view of its Professional Demographics instead.

If a column is missing, ask. Never ask for people's names, emails or lead data.

## Rules it applies

| rule | value | source | when it changes |
|---|---|---|---|
| Exact names | Lowercase, delete text in brackets, turn anything not a letter or digit into a space, collapse spaces, compare | my rule | Never: a close match strikes real companies |
| Bands | HIGH at 25% or more, MEDIUM 10% to under 25%, LOW under 10% | my default, from my own account, not measured across accounts | More accounts read |
| What sets the band | Typed totals: the larger of the click and impression share. No totals: the impression share | arithmetic, see Limits | Never |
| One name | Any exclude name above 5% of impressions is named, even at LOW | my default | More accounts read |
| Review group | Never excluded by default | my rule | A person decides |

## Steps

Show the arithmetic, so a second AI reaches the same numbers.

1. Count the rows. Print the date range and the totals you divide by. Use typed totals when given. If not, sum `Paid impressions` and `Paid clicks` over all rows, blanks as 0, and call them the file's own sums.
2. If the file has 15,000 rows or more, warn that the export may have stopped early: export a shorter date range or filter by ad set. The 15,000 is my default, not a limit LinkedIn publishes.
3. Normalize each `Company name` and each listed name as the first rule says. A row matches only if both results are identical.
4. Per matched name, add up paid impressions, clicks and engagements across its rows. Count its page rows: the different `Company page URL` values. A name counts as found only if it carries paid impressions or paid clicks.
5. Shares: exclude group impressions / total impressions x 100, and the same for clicks, one decimal. A 5 in the second decimal rounds to the even digit, so 2.25 prints 2.2. The review group the same way, apart.
6. Set the band. At LOW, still name any exclude name above 5% of impressions. Without typed totals, add: "of the clicks this file shows, {share} are placeholder clicks, and that reads high".
7. Top 5 by paid clicks, same-name rows added up, ties to the one with more impressions. If the first is an exclude name, say so first.
8. Write `exclusions.txt`: each exclude name found, one a line, spelled as in the list, most clicks first.
9. Only if asked, and last: clean CTR = (clicks minus exclude clicks) / (impressions minus exclude impressions).

## Answer

```
HIGH: 30.0% of paid clicks, 23.3% of impressions
Exclude 4 names, every page each
Then read the CTR again
Rule: Placeholder pages. Bands: Bogdan Liutic, CR8 (cr8.eco), proposed from his own account. Window 10 Oct to 8 Nov 2026.
```

Then the table by name, the review group, the top 5 and the exclusions.

## Say this out loud

- The ads did not send clicks to these pages. The people who clicked list them as their employer.
- What hurts is the share of your money those people take. The CTR, your click-through rate, may barely move.
- Type in your totals. Without them the band reads impressions only, and that can sit a level below the click share.
- Search each name in each ad set's company exclusions and add every page that carries it. Write down how many you added, because the saved list shows names only.
- If an ad set targets only your company list, a high share points at the targeting first. Check Audience Expansion (that's LinkedIn adding similar members), any OR group and any engaged-companies segment.
- Strip placeholder names from any list you build from engagement data. If an ad set also runs on LinkedIn's engaged-companies segment, put the exclusions on that ad set too.

## Limits

- Companies Hub counts a person under every current employer, and leaves out people with none. So the file's sums aren't your totals.
- Values under LinkedIn's threshold show as a dash on screen and a blank in the export. A blank isn't zero. That makes placeholder counts floors, so the real number can only be higher. And a click share against the file's own sum reads high.
- Without an ad set filter, the export is account level, so it can't tell you which ad set leaked.
- Real stealth companies do exist, and communities or suppliers are a judgment call. This check proposes. A person decides.

## Do not

- Change anything in the ad account.
- Match loosely, by the start of a name, or by a guess.
- Move a review name to exclude without the person's yes.

## Test

`examples/monday/sample-companies-export.csv`, 901 synthetic rows, with `examples/sample-placeholder-names.txt`. Window 10 Oct to 8 Nov 2026. Typed totals 13,710 impressions, 400 clicks.

Expected: HIGH. 120 of 400 clicks (30.0%), 3,200 of 13,710 impressions (23.3%). 4 names: Stealth AI Startup (2 page rows, 84 clicks), Multiple Companies 18, Angel Investor 12, Freelancer 6. Sample Community 01 under review, 9 clicks (2.2%). No typed totals: MEDIUM on 3,200 of 14,449 impressions (22.1%), and 120 of the 180 clicks the file shows (66.7%). See `examples/expected/placeholder-report.md` and `exclusions.txt`. Script: `python3 scripts/placeholder_check.py --help`.

## Provenance

- 350 of 708 clicks and 3,717 of 7,825 impressions, 7 Aug to 5 Sep 2026: CR8's own account.
- What that set ran on, read 5 Sep 2026 on CR8's own account: a 176,823-member uploaded company list, recorded as built from engagement data, and LinkedIn's "Highly Engaged | 90 days" companies segment, at a manual bid of 11% of LinkedIn's suggested one. Its two retargeting audiences were under 300 members and never served. How the page got in, through the segment's scoring, is my reading. I have no read of either audience's companies.
- Companies Hub, its Company Page requirement, Export, column meanings, the dash, one person under several employers: LinkedIn help a6884751, a7109308 and a10166020, read 17 Oct 2026.
- Test numbers: synthetic sample files.
