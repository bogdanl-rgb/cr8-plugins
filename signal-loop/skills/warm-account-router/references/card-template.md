# Card template and output files

## The card

One card per company. One fact a line. The signal states the fact and stops.

```
{company} · {list} list{, moves to X} · {crm state} · route: card
Ads: {n} paid engagements, {n} paid clicks, {n} paid impressions in 30 days. Site: visits on {n} days, last {date}.
Public signal: {signal}, {date}.
Why now: {n} paid engagements is at or above 10 on its own.   (or: {n} paid engagements plus {second signal})
Look for, in order: {role that owns what you sell}, then {economic buyer}, then whoever would run it. {staff} staff: {timing}.
Thread check: not run. Paste who sent the last message to each person, and the date. Not the text.
Write: one message, from your own account. Name only what is public. Never the ads, the clicks or the visit.
Approve? yes / no
```

No public signal on file: the third line reads "Public signal: none on file. Write only if you can name something public. Otherwise wait for one."

A card carries numbers, never a label such as "hot". Dates are written 9 Nov 2026.

## router_output.csv

One row per company that is not quiet, plus the flags. Columns:

`company, domain, list, list_move, route, reason, paid_impressions, paid_clicks, paid_engagements, second_signal, crm_state, owner, roles_to_find, timing, thread_check, card_approved_at, first_message_at, lag_hours, next_review_date`

- `route`: card, card next week, note to owner, park, cooldown, under 10 staff (at the alert line, but a company row this small can point to one person: no card, no note, no list move), watch, organic, quiet (a second signal, paid under the threshold), holdout check, excluded but served.
- The person fills `card_approved_at` and `first_message_at`, written 2026-11-09 10:30. Next Monday, pass the file back. `lag_hours` is the gap between them, and the brief prints the median.
- `next_review_date`: 14 days on for cards, notes, parked and cooling rows. 7 days on for card next week, under 10 staff, watch, organic and quiet. Blank on the two flags.

## signals-to-add.csv

`domain, signal_key, signal_date, evidence_url`, one `ad_alert` row per alert outside an open deal. Add the rows to your `signals.csv` before the next refresh. The evidence is the export window.

## a-queue.csv

`company, domain, status, paid_engagements, signals`: the A companies with no card or note this week, in signal order as in `a-list-queue.csv`, paid engagements shown, blank at a company under 10 staff. Never ranked by impressions. Work it from day 7 of serving. Each company is written to once: log the date in your CRM as `last_outbound_date`, and the queue drops the company until a public signal is dated after it. `status` says "not written yet" or "new signal since you wrote on {date}".

## crm-update.csv

`company_domain, company, signal_list, route, alert_date, owner, next_review_date, card_summary`: one row per card and per note to a deal owner, keyed on the company's website domain. After the yes or no on each card, delete the rows that got a no. Then import the file into your CRM, or paste each row into a task on the company record, owned by the person who writes. The plugin never writes to your CRM.
