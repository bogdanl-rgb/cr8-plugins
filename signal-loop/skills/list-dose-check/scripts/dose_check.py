#!/usr/bin/env python3
"""list-dose-check, by Bogdan Liutic, CR8 (cr8.eco). MIT License.

Is each ad set on a company list buying new people or the same ones again?
Views a person a month, share of the list reached, new people a week, price per
1,000 views, against the warm band (signal lists) or the cold band (fit only).

Read-only. Python 3.8 or later, standard library only, no network.

Weekly:
  python3 dose_check.py --delivery weekly-delivery.csv --out out \
      [--companies companies-export.csv --master master.csv]
  Optional columns in weekly-delivery.csv: frequency_90d, budget_week (for a manual bid).
Plan (before launch):
  python3 dose_check.py --plan --audience 2200 --daily 35 --price 80 --out out
  --audience is the ad set's target audience size (list plus job titles plus location),
  not the matched count of the list on the Audiences page. --matched still works as an old name.
"""
import argparse
import csv
import datetime
import math
import os
import re
import sys

COLS = ["week_start", "list", "ad_set_name", "spend_week", "impressions_week", "impressions_30d",
        "reach_30d", "reach_cumulative", "audience_size"]
WARM_LOW, WARM_HIGH = 4.0, 8.0     # views a person a month: under 4 under dose, 8 or more look at CTR and price
COLD_90 = 5.0                      # my cold default, the same as the Standard's example cold line: under 3 to 5 views in 90 days
USED_SHARE = 70.0                  # share of the list reached that counts toward "used up"
UNDERSPEND = 0.70                  # a manual bid spending under 70% of the weekly budget
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def die(msg):
    sys.stderr.write("list-dose-check: " + msg + "\n")
    sys.exit(2)


def f(x):
    x = (x or "").replace(",", "").replace("$", "").strip()
    try:
        return float(x)
    except ValueError:
        return None


def human(d):
    return "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year)


def money(x, cur):
    return "%s%s" % (cur, "{:,.0f}".format(x))


def norm(s):
    s = re.sub(r"\([^)]*\)", " ", (s or "").lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def norm_url(u):
    u = (u or "").strip().lower().split("?")[0]
    u = re.sub(r"^[a-z]+://", "", u)
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


def lists_of(label):
    """'AB', 'A+B', 'A and B', 'B' -> {'A', 'B'}"""
    return {c for c in re.sub(r"[^ABC]", "", label.upper())}


def plan(a):
    lo, hi = a.reachable
    views = a.views
    m_lo = a.matched * lo * views / 1000.0 * a.price
    m_hi = a.matched * hi * views / 1000.0 * a.price
    monthly = a.daily * 30.4
    cap = math.floor(a.daily * 14 / a.price)
    verdict = ("is over the dose: the list will be used up within weeks. Lower the budget, or move the rest of the "
               "budget to the C list or a second signal list from the same market."
               if monthly > m_hi else
               "is under the dose: a smaller list or a lower dose, said before any spend." if monthly < m_lo else
               "holds the dose.")
    cur = a.currency
    L = ["# List dose plan", "",
         "Inputs you gave: %s people in the ad set's target audience, %s a day, %s per 1,000 views (your own price, "
         "never a benchmark)." % (
             "{:,}".format(a.matched), money(a.daily, cur), money(a.price, cur)), "",
         "## Monthly spend that holds about %s views a person a month" % ("{:g}".format(views)), "",
         "%s x %d%% to %d%% reachable in a month x %s views / 1,000 x %s = %s to %s a month." % (
             "{:,}".format(a.matched), round(lo * 100), round(hi * 100), "{:g}".format(views), money(a.price, cur),
             money(m_lo, cur), money(m_hi, cur)),
         "Your budget: %s a day x 30.4 = %s a month. That %s" % (money(a.daily, cur), money(monthly, cur), verdict), "",
         "## Most live ads this ad set can feed", "",
         "%s a day x 14 / %s = %.1f, so %d live ads at most (rounded down)." % (
             money(a.daily, cur), money(a.price, cur), a.daily * 14 / a.price, cap),
         "Under 2: merge ad sets or add budget. Trimming ads does not help." if cap < 2 else
         "Run %d or fewer ads in this ad set." % cap,
         "Why: each live ad then gets about 1,000 views in 14 days, my default for when an ad's numbers can be read. "
         "Use what the ad set really spends, not the budget field.", "",
         "The dose caps what one list can absorb. If your lists together hold less than you need, add a second signal "
         "list or let the C list carry the rest. Never buy more views for the same people.",
         "The 40% to 50% reachable share, the 5 views and the 1,000 views an ad are my plan and defaults, not measured. "
         "Read the real numbers at day 14.", ""]
    with open(os.path.join(a.out, "dose-plan.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("\n".join(L))


def weekly(a):
    with open(a.delivery, encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        header = [h.strip() for h in (rd.fieldnames or [])]
        missing = [c for c in COLS if c not in header]
        if missing:
            die("weekly-delivery is missing column(s): " + ", ".join(missing))
        rows = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in rd]
    sets = {}
    for r in rows:
        sets.setdefault(r["ad_set_name"], []).append(r)
    cur = a.currency
    results = []
    for name, rs in sets.items():
        rs.sort(key=lambda r: r["week_start"])
        lab = rs[-1]["list"]
        ls = lists_of(lab)
        if not ls:
            die("list must name A, B, C or a mix such as AB, for ad set " + name)
        warm = "C" not in ls
        if "C" in ls and len(ls) > 1:
            die("ad set %s mixes C with A or B. Split it, or type it as C." % name)
        cum = [f(r["reach_cumulative"]) for r in rs]
        raw = [cum[0]] + [cum[i] - cum[i - 1] for i in range(1, len(cum))]
        restated = any(x < 0 for x in raw)
        new = [max(x, 0.0) for x in raw]  # LinkedIn can restate reach downward. Never a negative count.
        price = [f(r["spend_week"]) / f(r["impressions_week"]) * 1000 if f(r["impressions_week"]) else None for r in rs]
        last = rs[-1]
        vm = f(last["impressions_30d"]) / f(last["reach_30d"]) if f(last["reach_30d"]) else None
        share = 100.0 * cum[-1] / f(last["audience_size"]) if f(last["audience_size"]) else None
        falling = len(rs) >= 3 and new[-1] < new[-2] / 2 and new[-2] < new[-3] / 2
        priced = price[-1] is not None and price[0] is not None and price[-1] >= 2 * price[0]
        bw = f(last.get("budget_week", ""))
        underspent = bw is not None and bw > 0 and f(last["spend_week"]) is not None and f(last["spend_week"]) < UNDERSPEND * bw
        reached = share is not None and share >= USED_SHARE
        why_used = [w for w, ok in (("this week's price is %.1f times the first week's (2 times or more)" % (
            price[-1] / price[0]) if priced else "", priced),
            ("this week's spend is under 70% of the weekly budget (a manual bid)", underspent),
            ("%.1f%% of the list is reached (70%% or more)" % share if reached else "", reached)) if ok]
        used = falling and bool(why_used)
        f90 = f(last.get("frequency_90d", ""))
        if used:
            verdict, action = "used up", ("add no budget. Hand the unreached companies to a person, or start a second "
                                          "signal list from the same market.")
        elif vm is None:
            verdict, action = "no read", "type reach_30d from the Delivery columns."
        elif warm:
            if vm < WARM_LOW:
                verdict, action = "under dose", "raise the budget or the bid."
            elif vm < WARM_HIGH:
                verdict, action = "on plan", "hold."
            else:
                verdict, action = "look at CTR and price", "add nothing until CTR and price per 1,000 views are read."
        else:
            v90 = f90 if f90 is not None else vm * 3
            if v90 < COLD_90:
                verdict, action = "on plan", "hold."
            else:
                verdict, action = "over the cold band", "widen reach, add no frequency."
        results.append({"name": name, "list": lab, "band": "warm" if warm else "cold", "weeks": len(rs),
                        "vm": vm, "share": share, "new": new, "price": price, "verdict": verdict,
                        "action": action, "lists": ls, "first": rs[0]["week_start"], "last": last["week_start"], "f90": f90,
                        "why_used": why_used, "restated": restated})

    results.sort(key=lambda r: (r["verdict"] != "used up", r["name"]))
    unreached = []
    if a.companies and a.master:
        with open(a.master, encoding="utf-8-sig", newline="") as fh:
            master = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh)]
        with open(a.companies, encoding="utf-8-sig", newline="") as fh:
            exp = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh)]
        by_url = {norm_url(r.get("Company page URL", "")): r for r in exp if r.get("Company page URL")}
        by_name = {}
        for r in exp:
            by_name.setdefault(norm(r.get("Company name", "")), r)
        want = set()
        for r in results:
            if r["verdict"] == "used up":
                want |= r["lists"]
        for m in master:
            if m["list"] not in want or m["holdout"] == "yes":
                continue
            row = by_url.get(norm_url(m["linkedin_company_url"])) or by_name.get(norm(m["company"]))
            imp = f(row.get("Paid impressions", "")) if row else None
            if not imp:
                unreached.append(m)
        unreached.sort(key=lambda m: ("ABC".index(m["list"]), m["domain"]))
        with open(os.path.join(a.out, "unreached.csv"), "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["company", "domain", "list", "linkedin_company_url"])
            for m in unreached:
                w.writerow([m["company"], m["domain"], m["list"], m["linkedin_company_url"]])

    used_n = sum(1 for r in results if r["verdict"] == "used up")
    week = max(r["last"] for r in results)
    d = datetime.date.fromisoformat(week)
    L = ["# List dose check, week of %s" % human(d), "",
         "Source: %s, %s ad sets, %s weekly rows typed from the Delivery columns." % (
             os.path.basename(a.delivery), len(results), len(rows)), "",
         "## Verdict", "", "%s of %s ad sets %s used up." % (used_n, len(results), "is" if used_n == 1 else "are")]
    for r in results:
        L.append("%s (%s list, %s band): %s. %s" % (r["name"], r["list"], r["band"], r["verdict"],
                                                  r["action"][0].upper() + r["action"][1:]))
    L += ["", "## The numbers", "",
          "| ad set | list | weeks | views a person a month | share of list reached | new people this week | price per 1,000 views this week | first week |",
          "|---|---|---|---|---|---|---|---|"]
    for r in results:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["name"], r["list"], r["weeks"], "%.1f" % r["vm"] if r["vm"] is not None else "not typed",
            "%.1f%%" % r["share"] if r["share"] is not None else "not typed", "{:,.0f}".format(r["new"][-1]),
            money(r["price"][-1], cur) if r["price"][-1] is not None else "n/a",
            money(r["price"][0], cur) if r["price"][0] is not None else "n/a"))
    L += ["", "## How each verdict was reached", ""]
    for r in results:
        nw = ", ".join("{:,.0f}".format(x) for x in r["new"])
        pr = ", ".join(money(x, cur) if x is not None else "n/a" for x in r["price"])
        L.append("%s: new people a week %s. Price per 1,000 views %s." % (r["name"], nw, pr))
        if r["verdict"] == "used up":
            L.append("  Used up: new people fell under half of the week before, two weeks running, and %s." % (
                " and ".join(r["why_used"])))
        elif r["band"] == "warm":
            L.append("  Warm band: about 5 views a person a month planned. %.1f is %s." % (
                r["vm"], "under 4" if r["vm"] < WARM_LOW else "8 or more" if r["vm"] >= WARM_HIGH else "between 4 and 8"))
        elif r["f90"] is not None:
            L.append("  Cold band: %.1f views a person in 90 days, typed from the Delivery columns, %s 5. Share of the list "
                     "reached: %s." % (r["f90"], "under" if r["f90"] < COLD_90 else "at or over",
                                      "%.1f%%" % r["share"] if r["share"] is not None else "not typed"))
        else:
            L.append("  Cold band: %.1f a month x 3 = %.1f in 90 days at most, an upper bound, %s 5. Share of the list "
                     "reached: %s." % (
                r["vm"], r["vm"] * 3, "under" if r["vm"] * 3 < COLD_90 else "at or over",
                "%.1f%%" % r["share"] if r["share"] is not None else "not typed"))
        if r["restated"]:
            L.append("  LinkedIn restated reach downward in one week. That week's new people is set to 0.")
    if a.companies and a.master:
        L += ["", "## Unreached companies (unreached.csv)", ""]
        if used_n:
            L.append("%s companies on the used-up list%s show no paid impressions in the Companies export. Hand them to a "
                     "person, in list order, A first. The export is account level, so a company reached by any ad set "
                     "counts as reached." % ("{:,}".format(len(unreached)), "" if used_n == 1 else "s"))
            by = {}
            for m in unreached:
                by[m["list"]] = by.get(m["list"], 0) + 1
            L.append("By list: " + ", ".join("%s %s" % (k, by[k]) for k in "ABC" if k in by) + ".")
        else:
            L.append("No ad set is used up, so no hand-off list.")
    L += ["", "## Before you act", "",
          "- The 5 a month is my plan, not a measurement. When a list runs out of new people, the price per 1,000 views "
          "climbs as the same people see the ads again: read it at day 14.",
          "- On the cold band, low reach is the usual problem, not high frequency. Read the share reached before the views.",
          "- If the price climbs while new people fall, the list is used up, and this check will tell you I was wrong "
          "for your budget.",
          "", "## Limits", "",
          "- LinkedIn models reach, frequency and audience penetration and says to read them only as a direction. Treat them as estimates.",
          "- A pause and restart looks like a collapse in new people. Check the ad set's history before you act.",
          "- LinkedIn can restate spend after the fact. Use the latest read of each week.",
          "- Ad sets with an industry or title filter have small pools and use them up sooner.",
          "- Without a frequency_90d column, the cold band is read as views a month x 3. Average frequency over the last 90 days, typed from the Delivery columns, gives the 90-day number directly.",
          "- Delivery numbers take 24 to 36 hours to settle, so last week's numbers typed on Monday run a little short on Sunday. Type them on the same day every week.",
          "", "## Rules used", "",
          "- Warm band (A, B, AB): about 5 views a person a month, my plan, not measured. Under 4: under dose. 8 or more: "
          "look at CTR and price before adding anything. These edges are my defaults.",
          "- Cold band (C): under 3 to 5 views in 90 days, my default for fit-only lists, the same as the Standard's "
          "example cold line, read 17 Oct 2026.",
          "- Used up: new people this week under half of last week's, two weeks running, while one of these holds: this "
          "week's price per 1,000 views is 2 times the first week's or more (automated bid), this week's spend is under 70% "
          "of the weekly budget (manual bid), or 70% or more of the list is reached. Proposed, not yet tested across accounts.",
          "- For now LinkedIn offers a frequency cap (3 to 30 views a member in 7 days) only on brand awareness ad sets, and "
          "not every account has it. On every other objective there is no cap you can set: your budget, your bid and the "
          "size of your list set the dose.", ""]
    with open(os.path.join(a.out, "dose-report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    with open(os.path.join(a.out, "dose.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["ad_set_name", "list", "band", "weeks", "views_a_month", "share_reached", "new_people_this_week",
                    "price_this_week", "price_first_week", "verdict", "action"])
        for r in results:
            w.writerow([r["name"], r["list"], r["band"], r["weeks"], "%.1f" % r["vm"] if r["vm"] is not None else "",
                        "%.1f" % r["share"] if r["share"] is not None else "", "%.0f" % r["new"][-1],
                        "%.2f" % r["price"][-1] if r["price"][-1] is not None else "",
                        "%.2f" % r["price"][0] if r["price"][0] is not None else "", r["verdict"], r["action"]])
    print("\n".join(L))


def main():
    p = argparse.ArgumentParser(description="list-dose-check")
    p.add_argument("--delivery")
    p.add_argument("--companies")
    p.add_argument("--master")
    p.add_argument("--out", required=True)
    p.add_argument("--plan", action="store_true")
    p.add_argument("--audience", "--matched", dest="matched", type=int, metavar="SIZE",
                   help="the ad set's target audience size from Campaign Manager (list plus job titles plus "
                        "location), not the matched count on the Audiences page")
    p.add_argument("--daily", type=float)
    p.add_argument("--price", type=float)
    p.add_argument("--views", type=float, default=5.0)
    p.add_argument("--reachable", default="0.40,0.50")
    p.add_argument("--currency", default="$")
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.plan:
        if not (a.matched and a.daily and a.price):
            die("plan mode needs --audience, --daily and --price (your own price per 1,000 views)")
        a.reachable = tuple(float(x) for x in a.reachable.split(","))
        plan(a)
    else:
        if not a.delivery:
            die("weekly mode needs --delivery")
        weekly(a)


if __name__ == "__main__":
    main()
