# Signal Loop

Read-only checks for LinkedIn Ads on a signal list, by Bogdan Liutic, CR8 (cr8.eco). A signal list is the companies that fit your buyer, sorted by a dated, public reason to buy now. This plugin runs the scenario "Warm leads from a signal list" from The AI Standard: LinkedIn Ads. Four skills read your Campaign Manager exports and your own CSVs. That's it. They never send or change anything. The whole scenario, step by step, is in `SCENARIO.md`.

## The four questions it answers

| Skill | The question |
|---|---|
| `signal-list-check` | Which companies on my list have a reason to buy now? |
| `placeholder-page-check` | Are my clicks from real companies? |
| `list-dose-check` | How much budget can my list hold? |
| `warm-account-router` | Who on my list should I write to this week? |

## Install

- **Claude Code:** `/plugin marketplace add bogdanl-rgb/cr8-plugins`, then `/plugin install signal-loop@cr8`. Each skill runs as `/signal-loop:<skill>`. Want to try it without installing? Start Claude Code with `claude --plugin-dir` and the path to this folder, or to `signal-loop-1.0.0.zip`.
- **Cowork:** download `signal-loop.plugin` from the Releases page of github.com/bogdanl-rgb/cr8-plugins and upload it as a plugin.
- **claude.ai:** zip each skill folder in `skills/` and upload it as a skill.
- **Any other AI:** paste one `SKILL.md` and your file into the chat. Each skill shows its arithmetic, so you can check it. With no code tool, keep the file short, because an AI adding up hundreds of rows by hand can miscount. A Companies export, the file you get from Companies Hub in Campaign Manager, lists every company your ads reached. So it can be too long to paste. Delete the rows where Paid impressions, Paid clicks, Paid engagements and Organic engagements are all empty. Or use an AI with a code tool and the Python scripts in each `scripts/` folder.

## The order

On Mondays, run `placeholder-page-check`, then `list-dose-check`, then `warm-account-router`. The router can run the first two itself. It stops if `exclusions.txt` from the placeholder check is missing. A Monday is four exports (Companies, Leads, site visits by company and CRM), one row per ad set typed from the Delivery columns, up to 5 cards to approve and the messages after each yes.

On the first Monday of a month, or whenever new signal rows come in, run `signal-list-check` before the rest. At quarter end, run `signal-list-check` again in retrain mode, where it reads which signals sat on won deals.

## What you need

| Skill | Files |
|---|---|
| `signal-list-check` | `accounts.csv`, `signals.csv` (one row per signal, with an evidence link), `crm-accounts.csv` |
| `placeholder-page-check` | the Companies export from Campaign Manager, the date window you exported, and your Impressions and Clicks for the same dates from the reporting table |
| `list-dose-check` | `weekly-delivery.csv`, typed each Monday from the Delivery columns |
| `warm-account-router` | the Companies export, `master.csv` from `signal-list-check`, `exclusions.txt`, `crm-accounts.csv`. Optional: `site-visits.csv`, a reduced `leads.csv`, `public-engagement.csv`. It writes `crm-update.csv` for you to import into your CRM |

Each `SKILL.md` has the exact columns and how to get each file. `examples/` has synthetic sample files and the expected answers. I'd try those first.

## Data handling

Everything here works at company level. A site visit is a row of domain, date and page, never a person. Company-level visitor tools still read IP addresses in the EU, so check consent with whoever owns privacy. Pasting a Leads export into a cloud AI? Delete names, email addresses, profile URLs and custom answers first.

LinkedIn's Ads Agreement lets you share ad data only with a provider acting for you. So use an AI plan that doesn't train on your inputs, or run the scripts on your own machine. Your files stay where you put them. Check your company's data rules before you use a cloud AI.

## What it never does

This plugin never logs in to LinkedIn, and it never opens or reads LinkedIn pages. It doesn't call an undocumented endpoint, upload a list, edit an ad set or send a message. A person approves every card and writes from their own account.

## Limits

Reach and frequency are LinkedIn's estimates, and the Companies export doesn't carry them. Type them from the Delivery columns of the reporting table, the ones under Columns, then Delivery. Or export that table with the Delivery columns selected. I haven't checked that export yet, so compare one ad set's reach with the screen.

The exports carry no date window, so every skill asks you for it.

LinkedIn blanks counts under its reporting minimum, so every placeholder count is a floor. The real number can only be higher. Against the export's own sums a click share reads high, because the blanked small counts drop out of the click sum. An impression share can read low, because a person with two employers counts twice. So type your totals.

Each skill says where every threshold comes from, and which ones are only my defaults.

## License and credit

The text (SKILL.md files, references, READMEs, SCENARIO.md, sample data) is CC BY 4.0, so anyone can reuse it with credit: "Bogdan Liutic, CR8 (cr8.eco)". Scripts and manifests are MIT. "Signal Loop" and "CR8" are CR8's names, and the licenses don't cover them. DemandSense may publish, package and edit this plugin for The AI Standard under the names signal-loop and Signal Loop, with my credit, once I've seen the final version. Any other adapted version uses another name and doesn't suggest that CR8 or Bogdan Liutic endorses it. The two images on the Standard's pages are © CR8 and aren't in this plugin. See LICENSE.

Built by Bogdan Liutic, CR8 (cr8.eco). Want the loop run for you? [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)
