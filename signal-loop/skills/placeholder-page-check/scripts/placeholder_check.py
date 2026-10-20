#!/usr/bin/env python3
"""placeholder-page-check, by Bogdan Liutic, CR8 (cr8.eco). MIT License.

How much of a LinkedIn Ads account's paid impressions and clicks came from people
listed at placeholder employer pages such as "Stealth AI Startup". Exact-name
matching only. Writes the exclusion list. Changes nothing in any account.

Read-only. Python 3.8 or later, standard library only, no network.

  python3 placeholder_check.py --export companies-export.csv \
      --window "2026-10-10 to 2026-11-08" --total-impressions 13710 --total-clicks 400 --out out
  Optional: --names placeholder-names.txt   --ctr (adds a clean CTR, last)

--window is required because the export does not carry its date range.
--total-impressions and --total-clicks come from the Campaign Manager table
(Impressions and Clicks, same dates, same scope). Without them the shares are
against the file's own sums, and the report says so.
"""
import argparse
import collections
import csv
import os
import re
import sys

COLS = {
    "name": ["company name", "company"],
    "url": ["company page url", "company url", "linkedin url"],
    "imp": ["paid impressions", "impressions"],
    "clk": ["paid clicks", "clicks"],
    "eng": ["paid engagements", "engagements"],
}
FALLBACK = {
    "exclude": ["Stealth AI Startup", "Stealth Startup", "Stealth", "Multiple Companies", "Various Companies",
                "Angel Investor", "Freelancer", "Self-employed", "Something new", "Confidential"],
    "review": [],
}


CAP_ROWS = 15000  # my default warning size, not a limit LinkedIn publishes


def die(msg):
    sys.stderr.write("placeholder-page-check: " + msg + "\n")
    sys.exit(2)


def norm(s):
    s = re.sub(r"\([^)]*\)", " ", (s or "").lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def num(x):
    x = (x or "").replace(",", "").strip()
    try:
        return int(float(x)) if x else None
    except ValueError:
        return None


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def n(x):
    return "{:,}".format(x)


def find(header, key, required=True):
    low = {h.strip().lower(): h for h in header}
    for alias in COLS[key]:
        if alias in low:
            return low[alias]
    if required:
        die("no %s column. Expected one of: %s. Header was: %s" % (COLS[key][0], ", ".join(COLS[key]), ", ".join(header)))
    return None


def load_names(path):
    groups = {"exclude": [], "review": []}
    group = None
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            t = line.strip()
            if not t:
                continue
            if t.startswith("#"):
                low = t.lower()
                group = "exclude" if low.startswith("# exclude") else "review" if low.startswith("# review") else group
                continue
            if group:
                groups[group].append(t)
    if not groups["exclude"]:
        groups = {k: list(v) for k, v in FALLBACK.items()}
    return groups


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def human_window(w):
    """'2026-10-10 to 2026-11-08' -> 'window 10 Oct to 8 Nov 2026'. Anything else prints as typed."""
    m = re.match(r"\s*(\d{4})-(\d{2})-(\d{2})\s+to\s+(\d{4})-(\d{2})-(\d{2})\s*$", w or "")
    if not m:
        return "window " + (w or "not given")
    y1, m1, d1, y2, m2, d2 = (int(x) for x in m.groups())
    left = "%d %s" % (d1, MONTHS[m1 - 1]) + ("" if y1 == y2 else " %d" % y1)
    return "window %s to %d %s %d" % (left, d2, MONTHS[m2 - 1], y2)


def band(share):
    return "HIGH" if share >= 25 else "MEDIUM" if share >= 10 else "LOW"


def main():
    p = argparse.ArgumentParser(description="placeholder-page-check")
    p.add_argument("--export", required=True)
    p.add_argument("--window", required=True, help='for example "2026-10-10 to 2026-11-08"')
    p.add_argument("--total-impressions", type=int, dest="ti")
    p.add_argument("--total-clicks", type=int, dest="tc")
    p.add_argument("--names")
    p.add_argument("--ctr", action="store_true")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if (a.ti is None) != (a.tc is None):
        die("give both --total-impressions and --total-clicks, or neither")

    names_path = a.names or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references",
                                          "placeholder-names.txt")
    groups = load_names(names_path)
    canon = {}
    for g, lst in groups.items():
        for x in lst:
            canon[norm(x)] = (g, x)

    with open(a.export, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        rows = [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in reader]
    if not rows:
        die("the export has no rows")
    cn, cu, ci, cc = find(header, "name"), find(header, "url", False), find(header, "imp"), find(header, "clk")
    ce = find(header, "eng", False)

    fi = sum(num(r[ci]) or 0 for r in rows)
    fc = sum(num(r[cc]) or 0 for r in rows)
    capped = len(rows) >= CAP_ROWS
    typed = a.ti is not None
    di, dc = (a.ti, a.tc) if typed else (fi, fc)

    hit = collections.OrderedDict()
    for r in rows:
        k = norm(r[cn])
        if k in canon:
            g, label = canon[k]
            h = hit.setdefault(label, {"group": g, "imp": 0, "clk": 0, "eng": 0, "pages": set()})
            h["imp"] += num(r[ci]) or 0
            h["clk"] += num(r[cc]) or 0
            h["eng"] += (num(r[ce]) or 0) if ce else 0
            h["pages"].add(r[cu] if cu else r[cn])
    ex = {k: v for k, v in hit.items() if v["group"] == "exclude" and (v["imp"] or v["clk"])}
    rv = {k: v for k, v in hit.items() if v["group"] == "review" and (v["imp"] or v["clk"])}
    pi, pc = sum(v["imp"] for v in ex.values()), sum(v["clk"] for v in ex.values())
    si, sc = pct(pi, di), pct(pc, dc)
    deciding = max(si, sc) if typed else si
    flag = band(deciding)
    order = sorted(ex.items(), key=lambda kv: (-kv[1]["clk"], -kv[1]["imp"], kv[0]))
    named_low = [k for k, v in ex.items() if pct(v["imp"], di) > 5]

    byname = collections.OrderedDict()
    for r in rows:
        k = norm(r[cn])
        b = byname.setdefault(k, {"label": canon[k][1] if k in canon else r[cn], "clk": 0, "imp": 0, "pages": 0})
        b["clk"] += num(r[cc]) or 0
        b["imp"] += num(r[ci]) or 0
        b["pages"] += 1
    top = sorted(byname.items(), key=lambda kv: (-kv[1]["clk"], -kv[1]["imp"], kv[0]))[:5]
    top_is_ph = top[0][0] in canon and canon[top[0][0]][0] == "exclude" and top[0][1]["clk"] > 0

    L = ["# Placeholder page check, %s" % human_window(a.window), ""]
    L.append("Source: %s, %s rows." % (os.path.basename(a.export), n(len(rows))))
    if typed:
        L.append("Shares are against the totals you typed from the Campaign Manager table for the same dates: "
                 "%s impressions, %s clicks." % (n(di), n(dc)))
    else:
        L.append("No totals typed, so shares are against this file's own sums: %s paid impressions, %s paid clicks. "
                 "The flag uses the impression share only (see Limits)." % (n(fi), n(fc)))
    if capped:
        L.append("WARNING: the file has %s rows. At 15,000 rows or more an export may have stopped early (my default, "
                 "not a limit LinkedIn publishes). Rows may be missing. Export a shorter date range or filter by ad set."
                 % n(len(rows)))
    L += ["", "## Verdict", ""]
    if ex and typed:
        L.append("%s: %.1f%% of paid clicks and %.1f%% of paid impressions came from people listed at %s placeholder page name%s." % (
            flag, sc, si, len(ex), "" if len(ex) == 1 else "s"))
    elif ex:
        L.append("%s on impressions: %.1f%% of paid impressions came from people listed at %s placeholder page name%s." % (
            flag, si, len(ex), "" if len(ex) == 1 else "s"))
    else:
        L.append("LOW: no name from the exclude list carries paid impressions or clicks in this file.")
    if top_is_ph:
        L.append("The top company by paid clicks is a placeholder page: %s, %s clicks%s." % (
            top[0][1]["label"], n(top[0][1]["clk"]), (" on %s page rows" % top[0][1]["pages"]) if top[0][1]["pages"] > 1 else ""))
    if ex:
        L.append("Exclude %s name%s, every page that carries each name. Then read the CTR again." % (
            len(ex), "" if len(ex) == 1 else "s"))
    if flag == "LOW" and named_low:
        L.append("Even at LOW, named because each is above 5%% of impressions: %s." % ", ".join(named_low))
    if not typed and ex:
        L.append("Of the clicks this file shows, %.1f%% are placeholder clicks. That reads high: the file leaves out "
                 "click counts under LinkedIn's reporting minimum. Type the table totals for the true share." % pct(pc, fc))
    L += ["", "## By name, exclude group", "",
          "| name | page rows | paid impressions | share | paid clicks | share |", "|---|---|---|---|---|---|"]
    for k, v in order:
        L.append("| %s | %s | %s | %.1f%% | %s | %.1f%% |" % (k, len(v["pages"]), n(v["imp"]), pct(v["imp"], di),
                                                          n(v["clk"]), pct(v["clk"], dc)))
    L.append("| all | %s | %s | %.1f%% | %s | %.1f%% |" % (sum(len(v["pages"]) for v in ex.values()), n(pi), si, n(pc), sc))
    L += ["", "## Review group (a judgment call, never excluded by default)", ""]
    if rv:
        for k, v in sorted(rv.items(), key=lambda kv: (-kv[1]["clk"], kv[0])):
            L.append("%s: %s page row%s, %s impressions (%.1f%%), %s clicks (%.1f%%). Compare its CTR with the ad set's own before you decide." % (
                k, len(v["pages"]), "" if len(v["pages"]) == 1 else "s", n(v["imp"]), pct(v["imp"], di), n(v["clk"]),
                pct(v["clk"], dc)))
        if len(rv) > 1:
            L.append("Review group together: %.1f%% of paid impressions, %.1f%% of paid clicks. Not in the flag." % (
                pct(sum(v["imp"] for v in rv.values()), di), pct(sum(v["clk"] for v in rv.values()), dc)))
        else:
            L.append("Not in the flag.")
    else:
        L.append("None in this file.")
    L += ["", "## Top 5 companies by paid clicks (page rows with the same name added up)", ""]
    for i, (k, b) in enumerate(top, 1):
        tag = " (placeholder page)" if k in canon and canon[k][0] == "exclude" else " (review group)" if k in canon else ""
        L.append("%d. %s, %s clicks%s" % (i, b["label"], n(b["clk"]), tag))
    L += ["", "## Exclusions (exclusions.txt)", ""]
    for k, _ in order:
        L.append("- %s" % k)
    if ex:
        L.append("")
        L.append("In each ad set, search each name in the company exclusions and add every page with that exact name. "
                 "Write down how many pages you added: the saved list shows names only.")
    unseen = [x for x in groups["exclude"] if x not in ex]
    if unseen:
        L.append("On the exclude list, with no paid numbers in this file: %s. Excluding them now as well costs nothing." % ", ".join(unseen))
    L += ["", "## Before you act", "",
          "- The ads did not send clicks to these pages. The people who clicked list them as their employer.",
          "- This export is account level. It cannot say which ad set leaked. Read each ad set's company breakdown for that.",
          "- The harm is the share of money. The CTR may barely move.",
          "", "## Limits", "",
          "- LinkedIn leaves out companies under its reporting minimum, so the placeholder counts are floors.",
          "- This file's own sums are %s paid impressions and %s paid clicks. They are not your account totals: the file "
          "drops companies under the minimum and can list one person under two employers." % (n(fi), n(fc)),
          "- Nothing was changed in the account. A person makes every exclusion.",
          "", "## Rules used", "",
          "- Bands, proposed from my own account, not measured across accounts: HIGH at 25% or more, MEDIUM from 10% "
          "to under 25%, LOW under 10%. With typed totals the flag reads the larger of the click and impression share. "
          "Without them, the impression share only.",
          "- Any single exclude name above 5% of impressions is named, even at LOW.",
          "- Exact names only, after lowercasing, dropping text in brackets and turning punctuation into spaces. Never close matches."]
    if a.ctr:
        ai_, ac_ = di, dc
        L += ["", "## CTR, last (approximate)", "",
              "All: %.2f%%. Without the exclude group: %.2f%%." % (pct(ac_, ai_), pct(ac_ - pc, ai_ - pi)),
              "Both rest on counts LinkedIn rounds and hides when small. Read the rate again in Campaign Manager after the exclusions run for a week."]
    L += ["", "Checks by Bogdan Liutic, CR8 (cr8.eco). Want the loop run for you? [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)", ""]
    with open(os.path.join(a.out, "placeholder-report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    with open(os.path.join(a.out, "exclusions.txt"), "w", encoding="utf-8") as f:
        f.write("".join(k + "\n" for k, _ in order))
    with open(os.path.join(a.out, "placeholder-summary.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["window", "denominator", "impressions_total", "clicks_total", "placeholder_impressions",
                    "placeholder_clicks", "impression_share", "click_share", "flag", "names_to_exclude"])
        w.writerow([a.window, "typed table totals" if typed else "file sums", di, dc, pi, pc, "%.1f" % si, "%.1f" % sc,
                    flag, len(ex)])
    print("\n".join(L))


if __name__ == "__main__":
    main()
