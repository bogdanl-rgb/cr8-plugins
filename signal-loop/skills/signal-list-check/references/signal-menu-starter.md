# Signal menu, a starter

A signal is something a company did in public that says why now. A filter tells you who. A signal tells you when.

## The five tests

A source is only good if it passes all five.

1. **Public.** Anyone could see it without a login or a purchase, even if a tool you license finds it first.
2. **Dated.** You can tell when it happened.
3. **Structured.** It has the same shape every time, so you can compare this week with last week.
4. **Frequent.** It updates at least weekly.
5. **Causal.** It sits upstream of a purchase, not just next to one.

## The top three, in my order

| signal_key | what fires it | default window | evidence to keep |
|---|---|---|---|
| `new_leader` | A new decision-maker started in the role you sell to | 90 days | The announcement link and the start date |
| `job_post_names_tool` | A job ad whose text names the tools or the expectations you serve | 45 days | The job ad link |
| `funding` | A round was announced | 90 days | The news link and the date |

Two more come with defaults, `hiring_for_role` at 45 days and `product_launch` at 60. Any other key you add gets 60 days until you set your own. `ad_alert` (30 days) comes from `warm-account-router`. It's the one key that isn't public. It moves a company up a list, and it's never named in a message.

More signals, by industry: [cr8.eco/signals](https://cr8.eco/signals?utm_source=signal-loop-plugin)

## How a window works

A signal counts while it's younger than its window. On its date plus the window, it expires. The windows above are my defaults, and I haven't measured them. Swap each one for what your own account shows.

## Where rows come from

Careers pages and job boards. Funding news. Company announcements and press pages. Your own CRM. Use only sources you're allowed to use. This plugin never logs in to LinkedIn, and it never opens or reads LinkedIn pages.

For `new_leader`, use the company's own announcement or press page, a news item, or a job-change feed from a people-data provider you license. If you spot one on LinkedIn, type the row by hand, with a public link to the announcement. Never export or copy profiles.

## Row format

`domain, signal_key, signal_date, evidence_url`, one row per signal. No evidence link, no signal.

## Not a signal

- A sector or regulation tag on its own.
- A job post placed by a recruiting firm.
- A namesake: the same name, another company.
- A reaction on someone else's post. Too thin to write on.

When you write, the signal states the fact and stops: "saw you started as VP Marketing in September."
