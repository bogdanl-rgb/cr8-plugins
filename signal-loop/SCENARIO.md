# Warm leads from a signal list

Built by [Bogdan Liutic](https://www.linkedin.com/in/bgdn), CR8 ([cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin))

Every Monday this tells you which companies on your target list a person should write to this week, and why now. Your ads go only to that list, sorted by a dated, public reason to buy, like a new leader, a job ad or a funding round. It's the Signal Loop from my playbook in Kyle Poyar's Growth Unhinged (13 Sep 2026), rebuilt as free checks you run on your own exports.

This is the full runbook. The scenario page in The AI Standard: LinkedIn Ads is cut from it.

## For the business owner

**What you get.** Your LinkedIn ads reach only 500 to 1,000 companies that fit your buyer. Companies with 2 or more dated signals see your ads from day one, and a person on your team writes to each of them from day 7, in signal order. Every Monday you also get a card for any company that engaged far more than the ads explain, saying what it did and who to write to. An open deal goes to its owner as a note instead. By week 6 you compare engaged companies with the number you wrote down before launch. Each company sits in one of three lists: A has 2 or more dated signals, B has 1, C fits but has none yet. At quarter end you count meetings in two groups of one-signal companies: those that got your ads, and about 100 you held back.

**It catches waste first, too.** One ad set on my own account got 49% of its clicks from people listed at "Stealth AI Startup", 350 of 708 from 7 Aug to 5 Sep 2026. People pick that placeholder page instead of a real employer. The set ran broad and cheap, the opposite of a signal list.

**What it costs.**

- The ad budget your list can hold. A made-up example: an ad set of 2,200 people at $80 per 1,000 views holds $352 to $440 a month at my planned dose. Step 2 works yours out from your own price. Above that, add a second signal list from the same market, or let the cold C list carry the rest.
- One named person's Monday: four exports, up to 5 cards, and the messages after each yes.
- Messages to every company with 2 or more signals, from day 7. In the sample, 40 A companies at month start and up to 120 messages: one per person, up to 3 people a company.
- Someone checks 500 to 1,000 companies for fresh signals once a month. The plugin doesn't find them.
- About 100 companies with a signal get no ads and no messages for the quarter. That's the price of a fair test. Within a year it can show whether the ads made a big difference, not a small one.

The checks are free. The work is the weekly part, and I run it on your own ad account. You keep the list, the ads and the records. Want the loop run for you? I start with a free map of your signals, drawn with you on a call. [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)

## For the specialist

> **Where I disagree with the default**
>
> LinkedIn suggests starting broad, with ad sets of at least 50,000 members. I go the other way. My signal lists are 500 to 1,000 companies, about 2,500 to 5,000 people, sorted by a dated reason to buy now. A filter tells you who. A signal tells you when. Run a company with a fresh signal in the cold band, under 3 to 5 views in 90 days, and it barely sees you right when it has a reason to buy. So I plan about 5 views a person a month: well above the cold band, and up to the floor of the retargeting band over 90 days. Fit-only companies stay cold until a signal shows up.

You feed it LinkedIn Campaign Manager's own exports, plus CSVs from your CRM and your site analytics. There are four read-only skills, and each comes with a sample test you can run first. Every threshold says where it comes from: my own account, a LinkedIn help page, or my plan. The placeholder check runs before you read any rate.

## The card

```
SCENARIO      Warm leads from a signal list
INSTALL       /plugin marketplace add bogdanl-rgb/cr8-plugins
              /plugin install signal-loop@cr8
              Built with Bogdan Liutic, CR8 (cr8.eco)
TRIGGER       Every Monday, on each signal list you run
SOURCES       Your signal list, LinkedIn Ads exports, your CRM, site visits by company
SKILL         signal-list-check
SKILL         placeholder-page-check
SKILL         list-dose-check
AI AGENT      warm-account-router: rank list companies by signal, draft the week's cards
OUTPUT        Who to write to this week
              39 A companies, 2+ dated signals each, in signal order
              2 cards: companies that engaged far above the ads
              + replies and meetings against your plan, even at zero
HUMAN GATE    You approve each card. A human writes from their own account.
NOT COVERED   Sending, uploading, editing the ad account, finding signals
TERMS         This plugin reads LinkedIn's own exports only. Ad data stays at company level.
              It never opens or reads LinkedIn pages.
```

I took the output lines from a deliberately dense sample week, where every route fires at least once. Its Monday brief opens: "3 list companies hit the alert line. 2 cards to approve. 1 note to a deal owner. 0 sent." One A company got a card that week, so 39 sit in the queue.

**Your tools, by the Standard's categories:** LinkedIn Campaign Manager. A CRM (HubSpot, Salesforce or a spreadsheet), where each approved card becomes a task for the person who writes. Any company database, to look up each company's website. Site analytics that tell you which company a visit came from. Company level only, and behind your consent banner if your tool needs one. Spreadsheets for the CSVs, and Slack or email for the Monday brief.

Signal rows come from public, dated sources you're allowed to use: careers pages, job boards, funding news, company announcements, and a people-data tool you license for job changes.

## The steps

### Step 0. The math (once, before any spend)

- **TRIGGER** Before the first dollar
- **SOURCES** Your deal data and your market count
- **SKILL** None. Three questions
- **AI AGENT** Checks the three numbers you give it
- **OUTPUT** Go, or stop with the reason
- **HUMAN GATE** The business owner says yes to all three
- **WHAT TO MEASURE** The three numbers, written down with a date, plus how many list companies you expect to engage by week 6

First: a deal is worth $10,000 or more over a customer's life. Otherwise the math just doesn't fit. Second: your market holds 10,000 or more decision-makers. People are not sitting on LinkedIn all the time (surprise!). You need critical mass for LinkedIn ads to work at any given moment. Third, the obvious one: your buyer is on LinkedIn. If any of the three fails, stop here.

That 10,000 is your market. The list in step 1 is the slice of it you sort by signal, 500 to 1,000 companies.

### Step 1. The list (monthly)

- **TRIGGER** First Monday of the month, or new signal rows
- **SOURCES** Your fit list, public dated signals, your CRM for exclusions
- **SKILL** `signal-list-check`
- **AI AGENT** Drops stale or unlinked signal rows, splits A, B and C, sets aside the holdout
- **OUTPUT** Three lists, the upload and exclusion files, the A list in signal order
- **HUMAN GATE** You read the A list, then upload it yourself
- **WHAT TO MEASURE** Share of companies with a fresh signal. Matched members 48 hours after upload

A signal is something a company did in public that tells you why now. Its source has to pass five tests: public, dated, structured, frequent and causal. You'll find all five in `signal-menu-starter.md`. I rank a new leader in the role inside 90 days first, then a job ad whose text names the tools or the expectations, then funding.

A company with 2 or more different fresh signals goes on the A list. Exactly 1 puts it on B. C is fit only, a company that matches your buyer profile and has no signal yet. Not wrong, just not now. And one signal firing twice still counts as one. Two different dated signals are a company raising its hand in public. That's why A gets a person from day 7, clicked or not, while B and C wait for the ads to work.

Matched members are the people LinkedIn finds at your companies. Under 300 and LinkedIn won't show your ads. Your ad set needs 300 too, after you add job titles and location. LinkedIn also takes a company list only from 300 rows. So at 500 companies, 3 in 5 need a dated signal before the list runs warm.

The check also sets aside a holdout, a group of companies you keep away from everything so you have something to compare against. The holdout is 10% of the list or 100 companies, whichever is bigger. It all comes from B, and it's never more than half of B. For the whole quarter those companies get no ads and no messages. Yes, that feels like wasting warm companies. It's the price of a fair test, because at quarter end their meetings are the only clean comparison you'll have. At these sizes only a gap of about 5x shows inside a year (step 5), so keep adding the counts up, quarter after quarter.

The upload still comes first, though. If holding back 100 companies would leave A and B under 300 rows, the holdout gets smaller. Under 350 warm companies there's no holdout at all, so at 500 companies, 7 in 10 need a dated signal first.

### Step 2. The ads, by list (at launch, re-planned monthly)

- **TRIGGER** The list is uploaded. Matching can take 48 hours
- **SOURCES** Each ad set's target audience size in Campaign Manager
- **SKILL** `list-dose-check`, plan mode
- **AI AGENT** Plans the dose (views a person a month), the monthly spend and the ad cap per list
- **OUTPUT** One ad set per list. A and B: consideration, with the offer as an ad. C: awareness first
- **HUMAN GATE** You build, launch, and check every setting after each edit
- **WHAT TO MEASURE** Planned against delivered views a person a month, per list

Run one ad set per list, and rotate the offer in as an ad, not as a second ad set. A gets its own ad set (Website conversions or Lead generation) only once A and B minus the holdout each have 300 rows or more. Until then A rides along with B and gets the same ads. The difference is that a human writes to A from day 7, once the ads have served, in signal order, once per company.

On A and B the ads start with consideration, meaning case studies and guides, with the offer rotated in as one of the ads. C starts with awareness (the founder's posts run as ads), then case studies, and the offer comes last. A and B get about 5 views a person a month. C runs cold for awareness, at the size it is, until a signal moves a company up a list.

The dose is how many times each person sees your ads in a month, and it caps the spend a list can hold. It counts every ad set on the list together. Whatever's left of your budget goes to the C list or a second signal list. Never to more views for the same people. So one signal list holds only so much spend, $352 to $440 a month in the made-up example above. A bigger budget means more signal lists from the same market, each at its own dose. The sample still runs two ad sets on one list, on purpose, so you can see the check catch it.

Target the uploaded list plus the job titles that own what you sell, every variant, with the countries set wide. Then plan the dose on that ad set's audience size, not on the list's matched count.

Settings can switch back on when you edit or copy an ad set. So after every edit, open the saved ad set and look again.

- Audience Network off, so your ads don't show on other apps and sites.
- Audience Expansion off, so LinkedIn doesn't add similar members.
- Location on "Permanent". "Recent or permanent" also reaches people who are only visiting.
- A manual bid inside LinkedIn's suggested range.
- Exclusions set: customers, open deals, employees, competitors, placeholder pages and the holdout. Strip placeholder names from any list you build from engagement data too.

`signal-list-check` writes the holdout and CRM exclusion files for you.

### Step 3. The catch: who engaged (every Monday)

- **TRIGGER** Monday, after you export from Companies Hub
- **SOURCES** The Companies export, the Leads export without test leads, site visits by company, your CRM
- **SKILL** `placeholder-page-check`, then `list-dose-check` weekly, then the agent
- **AI AGENT** `warm-account-router`: strike placeholders, read the dose, rank by signal
- **OUTPUT** Up to 5 cards to approve, plus the Monday line
- **HUMAN GATE** You approve or skip each card
- **WHAT TO MEASURE** Engaged list companies against the plan you wrote before launch (how many by week 6)

The alert line: 10 or more paid engagements in 30 days. Or 3 or more, plus a second signal in the same 30 days. That second signal is a return visit, a form fill, or someone in your target roles liking or commenting on a post you're not promoting.

By paid engagements I mean what LinkedIn counts on your ads: social actions plus clicks to your landing page or LinkedIn Page. LinkedIn counts them whether it charged you or not. On my own Companies export of 5 Sep 2026, 3 is the smallest number any cell shows. Below it, the cell is blank.

An alert counts as one more signal, so the company moves up a list, unless it's an open deal. You never mention it in a message. Then your CRM decides the route. A customer drops out, an open deal becomes a note to its owner, and the rest get cards. A company under 10 staff gets no card, no note and no list move. At that size, a company row can point to one person.

Placeholders go first, because of my own ad set above. It ran broad and cheap: a 176,823-member company list built from engagement data, plus LinkedIn's own engaged-companies segment, at 11% of the suggested bid. My reading of how the page got in: LinkedIn's engaged-companies segment scored "Stealth AI Startup" as an engaged company and served its members, and each new click raised that score. Rank that file as it comes, and your top account is a company that doesn't exist.

Once a week is enough. Form fills and replies should still get a human within minutes, but company engagement can't move that fast. I've seen the Companies export run about 2 days behind, and it blanks any value under LinkedIn's reporting minimum.

At about 5 people a company, 40% to 50% of them reached and 5 views each, a company sees 10 to 13 paid views a month. So an alert is rare, and it marks a company that engaged far more than the dose predicts. Most Mondays you'll get no card, and the work is the A list. Write the zeros down too.

### Step 4. A human writes (the same day as the yes)

- **TRIGGER** A card is approved
- **SOURCES** The card, and who sent the last message to each person
- **SKILL** `warm-account-router`, thread check
- **AI AGENT** Sends nothing. The card names the public signal. The human writes the line (message rules in the plugin)
- **OUTPUT** One message per person: the public signal as a plain fact, then one question, nothing after it. Never the ad, the click or the visit
- **HUMAN GATE** Before any ad runs, one named person owns the cards, with a backup, and sends from their own account. If you wrote last and got silence, park the thread until a new signal
- **WHAT TO MEASURE** Median hours from approved card to first message. Share of cards worked the same day

Who do you write to? Start with the role that owns what you sell. It's often the one the signal names, so a new leader goes first. Then the economic buyer, whoever signs off the budget: the founder or CEO under 50 staff, a VP or C-level above that. Then whoever would run it.

Timing depends on size. Under 50 staff, write to them on day 0, 3 and 7. From 50 to 200, write to the next person once the last has had 7 days to reply. Over 200, write to all of them at once. If you only find two people, write to two.

Each Monday the router also writes a hand-off file for your CRM, `crm-update.csv`. It has one row per card and per note to a deal owner, keyed on the company's website domain. After your yes or no, delete the rows that got a no. Then import the file into your CRM, or paste each row into a task on the company record, owned by the person who writes. Fill in `card_approved_at` and `first_message_at` in `router_output.csv`, and next Monday's brief counts the hours between them. The plugin never writes to your CRM.

A sample DM, lowercase, the way people write them:

> hey {first name}, saw you started as VP Marketing at {company} in September. how are you planning the first 90 days?

You pick people by role because LinkedIn names the company, never the person. And engagements aren't people. On my own account, 2,061 ad engagements came down to about 1,000 people.

### Step 5. Closed-won retrains the list (each quarter, and at every closed deal)

- **TRIGGER** Quarter end, or a deal closes, won or lost
- **SOURCES** Won and lost deals with first-call dates, the list as saved the day the holdout was set aside (`master-carve.csv`), the holdout
- **SKILL** `signal-list-check`, retrain mode
- **AI AGENT** Lists the signals that sat on won companies before the first call, against lost and unconverted ones. Proposes next quarter's signal menu
- **OUTPUT** A signal ranking proposal and the quarter-end count
- **HUMAN GATE** You change the signal menu
- **WHAT TO MEASURE** Whether each company was on the list before its first call, from your CRM's dates. Meetings among served B companies and among the holdout, both carved from B, as two counts with both sizes, never as a percentage gain

The meetings stay two counts, never a percentage. A made-up example: say 1 company in 200 books a meeting in a quarter. Then you'd expect half a meeting from a holdout of 100, and a percentage on half a meeting means nothing. At that rate, at the sample's sizes of about 320 served B companies and 100 held back, the holdout catches a 5x gap within a year. A 2x gap can take three years or more. So it guards against a big false belief. It doesn't measure lift.

Compare served B with the holdout only. A and C differed from B before the first ad, so they print for reference. And never compare engaged companies with unengaged ones. The engaged ones were warmer before the first ad.

## What to measure

Every week you get one line, the Monday line, printed even at zero. It counts engaged list companies against your plan, alerts, cards approved, first messages, first messages the same day as the yes, median hours to the first message, replies and meetings. Engaged means a list company outside the holdout with 3 or more paid engagements shown. The line also carries the placeholder share of paid clicks. Under 10% is my proposed low band. At quarter end you count meetings among served B companies and among the holdout, both carved from B, as two counts. The holdout got no ads and no messages, so it's the only control.

Don't trust LinkedIn's conversions column as it comes. Pick one conversion yourself, a form fill or a booked call. Count it only after a click, and set the counting window by hand.

## What it doesn't do

The plugin reads exports from LinkedIn Campaign Manager and files you already hold. It doesn't log in to LinkedIn, read LinkedIn pages, automate messages, write to your CRM or track people across sites. This scenario reads site visits at company level only, and it doesn't use person-level visitor identification. Even company-level tools read IP addresses in the EU, so check consent and your privacy notice first.

LinkedIn's Ads Agreement lets you share ad data only with a provider acting for you. So use an AI plan that doesn't train on what you paste, or run the scripts on your own machine. Before you paste a Leads export into a cloud AI, delete names, email addresses and profile URLs.

A human decides who to write to and sends from their own account. Before you write to someone, check the consent rules where they live.

## What I haven't measured yet

The 5-a-month dose is my plan and the alert line is my default. I haven't run this exact version for a full quarter, so I can't show you a quarter of meetings. That's why it counts them from day one: engaged companies against your plan by week 6, meetings against a held-back group at quarter end. And `list-dose-check` is the test that can prove my dose wrong for your account.

## Who runs this

Every Monday someone exports four files: Companies, Leads, site visits by company and CRM. They type one row per ad set from the Delivery columns, the spend, impressions and reach numbers in Campaign Manager's reporting table. Then they run the checks, approve up to 5 cards and write to up to 15 people from them, up to 3 a company.

On top of the cards, each A company gets written to once, in signal order, from day 7. Log the date in your CRM, and the queue drops that company until it has a new signal.

Once a month someone checks 500 to 1,000 companies for fresh, dated signals and logs each one with its link. The plugin won't find them for you. Any input can stop updating without telling you, so check every file is fresh before you trust the Monday line.

## Install and run

The install lines are on the card. Everything lives at [github.com/bogdanl-rgb/cr8-plugins](https://github.com/bogdanl-rgb/cr8-plugins): the four SKILL.md files, the scripts and the sample files. On Mondays, run `/signal-loop:warm-account-router`. Each time you refresh the list, run `/signal-loop:signal-list-check`.

In Cowork, download `signal-loop.plugin` from the repository's Releases page and upload it as a plugin. In claude.ai, zip each skill folder and upload it as a skill. In any other AI, paste one SKILL.md and your file, and keep the file short. An AI adding up hundreds of rows by hand can miscount. A Companies export lists every company your ads reached, so it can be too long to paste. Delete the rows where Paid impressions, Paid clicks, Paid engagements and Organic engagements are all empty, or use an AI with a code tool and the scripts. With no AI at all, each SKILL.md works as a spreadsheet checklist.

Try it on the synthetic files in `examples/` first.

## From the Growth Unhinged playbook to this

Since that playbook I've added the C list, the A, B and C names and the dose per list. Placeholder pages now get struck first, the hours from a yes to the first message get counted, and there's a holdout. I also changed one thing on purpose. This version stays at company level and reads only LinkedIn's own exports and your own files, so it runs on any account with no extra tools.

First published in Growth Unhinged, 13 Sep 2026: https://www.growthunhinged.com/p/linkedin-ad-playbook

Version 1.0.0, 21 Oct 2026. Bogdan Liutic, CR8 ([cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)).

Text licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Credit "Bogdan Liutic, CR8 (cr8.eco)" and say what you changed.
