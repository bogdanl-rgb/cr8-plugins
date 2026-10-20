#!/usr/bin/env python3
"""signal-list-check, by Bogdan Liutic, CR8 (cr8.eco). MIT License.

Sorts a target company list into A, B and C lists by how many different dated,
public signals each company has. Carves a holdout from B that never sees ads, writes upload
files in LinkedIn's company-list template and checks LinkedIn's 300-row minimum.

Read-only. Python 3.8 or later, standard library only, no network.

Dates: 2026-11-02 is safest. 11/2/2026 and "November 2, 2026" are read when the month is clear.
A date like 3/4/2026 can mean 3 April or 4 March, so in a CRM file it stops the run, unless you
pass --month-first (your files write the month first, as US exports do).

Month start:
  python3 signal_list_check.py --accounts accounts.csv --signals signals.csv \
      --crm crm-accounts.csv --today 2026-11-02 --out out
  Optional: --names placeholder-names.txt   --holdout-in holdout.csv
            --window funding=120 (repeat to change a freshness window)

Quarter end (retrain mode):
  python3 signal_list_check.py --retrain crm-deals.csv --signals signals.csv \
      --master master.csv --since 2026-11-02 --today 2027-02-01 --out out
"""
import argparse
import collections
import csv
import datetime
import os
import re
import sys

WINDOWS = {
    "new_leader": 90,
    "job_post_names_tool": 45,
    "hiring_for_role": 45,
    "funding": 90,
    "product_launch": 60,
    "ad_alert": 30,
    "other": 60,
}
ORDER = ["new_leader", "job_post_names_tool", "funding", "hiring_for_role", "product_launch"]
UPLOAD_HEADER = ["companyname", "companywebsite", "companyemaildomain", "linkedincompanypageurl",
                 "stocksymbol", "industry", "city", "state", "companycountry", "zipcode"]
ACC_COLS = ["company", "domain", "linkedin_company_url", "country", "employees", "fit_ok", "exclude_reason"]
SIG_COLS = ["domain", "signal_key", "signal_date", "evidence_url"]
CRM_COLS = ["company", "domain", "deal_stage", "owner", "stage_date", "last_outbound_date"]
DEAL_COLS = ["company", "domain", "deal_stage", "first_call_date"]
FALLBACK_EXCLUDE = ["Stealth AI Startup", "Stealth Startup", "Stealth", "Multiple Companies",
                    "Various Companies", "Angel Investor", "Freelancer", "Self-employed",
                    "Something new", "Confidential"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_FIRST = [False]  # set by --month-first
STAGE_RANK = {"won": 0, "open": 1, "lost": 2, "none": 3}  # one row a company: the strongest stage wins
HOLDOUT_FLOOR = 50   # my default: a smaller holdout is not worth carving
UPLOAD_FLOOR = 300   # LinkedIn takes a company list from 300 rows


def die(msg):
    sys.stderr.write("signal-list-check: " + msg + "\n")
    sys.exit(2)


def read_csv(path, needed):
    if not os.path.exists(path):
        die("file not found: " + path)
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in needed if c not in header]
        if missing:
            die(path + " is missing column(s): " + ", ".join(missing) + ". Header was: " + ", ".join(header))
        rows = []
        for r in reader:
            rows.append({(k or "").strip(): (v or "").strip() for k, v in r.items()})
        return rows


def norm_name(s):
    s = re.sub(r"\([^)]*\)", " ", (s or "").lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def norm_domain(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^[a-z]+://", "", s)
    s = s.split("/")[0]
    if s.startswith("www."):
        s = s[4:]
    return s.rstrip(".")


def read_day(s, month_first=False):
    """Returns (date or None, ok). ok is False when the text is there but cannot be read safely."""
    s = (s or "").strip()
    if not s:
        return None, True
    try:
        return datetime.date.fromisoformat(s[:10]), True
    except ValueError:
        pass
    m = re.match(r"^(\d{1,2})([/.])(\d{1,2})[/.](\d{4})", s)
    if m:
        a, sep, b, y = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
        if a > 12 >= b or sep == ".":
            d, mo = a, b
        elif b > 12 >= a or month_first:
            d, mo = b, a
        else:
            return None, False
        try:
            return datetime.date(y, mo, d), True
        except ValueError:
            return None, False
    m = re.match(r"^([A-Za-z]{3})[A-Za-z]*\.?\s+(\d{1,2}),?\s+(\d{4})", s)
    if m and m.group(1).title() in MONTHS:
        try:
            return datetime.date(int(m.group(3)), MONTHS.index(m.group(1).title()) + 1, int(m.group(2))), True
        except ValueError:
            return None, False
    return None, False


def parse_date(s):
    return read_day(s, MONTH_FIRST[0])[0]


def stage_by_domain(crm):
    """A deals export has one row a deal. Keep the strongest stage per company: won, open, lost, none."""
    best = {}
    for r in crm:
        d = norm_domain(r["domain"])
        if not d:
            continue
        st = r["deal_stage"].lower()
        st = st if st in STAGE_RANK else "none"
        if d not in best or STAGE_RANK[st] < STAGE_RANK[best[d]]:
            best[d] = st
    return best


def human(d):
    return "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year) if d else ""


def n(x):
    return "{:,}".format(x)


def load_exclude_names(path):
    names = []
    if path and os.path.exists(path):
        group = None
        for line in open(path, encoding="utf-8"):
            t = line.strip()
            if not t:
                continue
            if t.startswith("#"):
                low = t.lower()
                if low.startswith("# exclude"):
                    group = "exclude"
                elif low.startswith("# review"):
                    group = "review"
                continue
            if group == "exclude":
                names.append(t)
        if names:
            return {norm_name(x) for x in names}
    return {norm_name(x) for x in FALLBACK_EXCLUDE}


def key_rank(k):
    return (ORDER.index(k), k) if k in ORDER else (len(ORDER), k)


def write_csv(path, header, rows, crlf=False):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n" if crlf else "\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def fresh_signals(signals, keep_domains, today, windows, stats):
    """Return {domain: {key: (date, url)}} for fresh, evidenced signals, newest date per key."""
    fresh = collections.defaultdict(dict)
    for s in signals:
        d = norm_domain(s["domain"])
        if d not in keep_domains:
            stats["company not on the list, or removed"] += 1
            continue
        if not s["evidence_url"]:
            stats["no evidence link"] += 1
            continue
        dt = parse_date(s["signal_date"])
        if dt is None:
            stats["unreadable date"] += 1
            continue
        if dt > today:
            stats["date after today"] += 1
            continue
        key = s["signal_key"].lower()
        w = windows.get(key, windows["other"])
        if (today - dt).days >= w:
            stats["expired"] += 1
            continue
        stats["kept"] += 1
        if key not in fresh[d] or dt > fresh[d][key][0]:
            fresh[d][key] = (dt, s["evidence_url"])
    return fresh


def month_start(a):
    out = a.out
    os.makedirs(out, exist_ok=True)
    today = parse_date(a.today)
    if not today:
        die("--today must be a date like 2026-11-02")
    windows = dict(WINDOWS)
    for w in a.window or []:
        k, _, v = w.partition("=")
        if not v.isdigit():
            die("--window takes key=days, for example funding=120")
        windows[k.strip().lower()] = int(v)
    names_path = a.names or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..",
                                          "placeholder-page-check", "references", "placeholder-names.txt")
    placeholder = load_exclude_names(names_path)

    accounts = read_csv(a.accounts, ACC_COLS)
    signals = read_csv(a.signals, SIG_COLS)
    crm = read_csv(a.crm, CRM_COLS) if a.crm else []
    stage = stage_by_domain(crm)

    removed = collections.Counter()
    kept, seen = [], set()
    for r in accounts:
        d = norm_domain(r["domain"])
        key = d or ("name:" + norm_name(r["company"]))
        st = stage.get(d, "none") if d else "none"
        reason = r["exclude_reason"].lower()
        if key in seen:
            removed["duplicate row"] += 1
        elif st == "won":
            removed["customer"] += 1
        elif st == "open":
            removed["open deal"] += 1
        elif reason:
            removed[reason] += 1
        elif r["fit_ok"].lower() not in ("true", "yes", "1"):
            removed["not a fit"] += 1
        elif norm_name(r["company"]) in placeholder:
            removed["placeholder page"] += 1
        else:
            kept.append(r)
        seen.add(key)
    no_domain = sum(1 for r in kept if not norm_domain(r["domain"]))

    stats = collections.Counter()
    keep_domains = {norm_domain(r["domain"]) for r in kept if r["domain"]}
    fresh = fresh_signals(signals, keep_domains, today, windows, stats)

    lists = {"A": [], "B": [], "C": []}
    for r in kept:
        c = len(fresh.get(norm_domain(r["domain"]), {}))
        lists["A" if c >= 2 else "B" if c == 1 else "C"].append(r)
    for k in lists:
        lists[k].sort(key=lambda r: norm_domain(r["domain"]) or norm_name(r["company"]))
    total = len(kept)
    na, nb, nc = len(lists["A"]), len(lists["B"]), len(lists["C"])

    # Holdout: reuse this quarter's file, or carve from B by a fixed rule anyone can rerun.
    held, underpowered, carve_note = set(), False, ""
    if a.holdout_in:
        prev = read_csv(a.holdout_in, ["domain"])
        held = {norm_domain(r["domain"]) for r in prev} & keep_domains
        carve_note = "Kept from %s: %s companies still on the list. No new carve until the quarter ends." % (
            os.path.basename(a.holdout_in), n(len(held)))
    else:
        want = max(total // 10, 100)
        size = min(want, nb // 2, max(na + nb - UPLOAD_FLOOR, 0))
        if size < HOLDOUT_FLOOR:
            size = 0
        underpowered = 0 < size < want
        bdom = [norm_domain(r["domain"]) for r in lists["B"]]
        held = {bdom[(i * nb) // size] for i in range(size)} if size else set()
        carve_note = ("Size: %s. Rule: 10%% of the list or 100 companies, whichever is larger, from B only, never over "
                      "half of B, and never so large that A plus served B falls under 300 rows. 10%% of %s is %s." % (
                          n(size), n(total), "{:,.1f}".format(total / 10)))
        if not size:
            carve_note += (" No holdout this quarter: the warm list can't spare %s companies and still serve "
                           "(a holdout under %s companies is not carved)." % (HOLDOUT_FLOOR, HOLDOUT_FLOOR))
        if size:
            carve_note += (" Picked: sort B by domain, A to Z, and take row 1 + floor(i x %s / %s) "
                           "for i = 0 to %s." % (nb, size, size - 1))
    b_served = [r for r in lists["B"] if norm_domain(r["domain"]) not in held]
    a_or_b_held = [r for k in ("A", "B", "C") for r in lists[k] if norm_domain(r["domain"]) in held]

    # master.csv
    master_rows, drops = [], []
    for k in ("A", "B", "C"):
        for r in lists[k]:
            d = norm_domain(r["domain"])
            sig = sorted(fresh.get(d, {}).items(), key=lambda kv: key_rank(kv[0]))
            exp = sorted(dt + datetime.timedelta(days=windows.get(key, windows["other"])) for key, (dt, _) in sig)
            drop = exp[0] if k == "B" else (exp[-2] if k == "A" else None)
            if drop:
                drops.append((drop, r["company"], k))
            master_rows.append([r["company"], d, r["linkedin_company_url"], r["employees"], k,
                                " | ".join(x for x, _ in sig), " | ".join(str(v[0]) for _, v in sig),
                                " | ".join(v[1] for _, v in sig), "yes" if d in held else "no",
                                str(drop) if drop else ""])
    write_csv(os.path.join(out, "master.csv"),
              ["company", "domain", "linkedin_company_url", "employees", "list", "signals", "signal_dates",
               "evidence_urls", "holdout", "drops_list_on"], master_rows)
    write_csv(os.path.join(out, "holdout.csv"), ["company", "domain", "list"],
              [[r["company"], norm_domain(r["domain"]), k] for k in ("A", "B", "C") for r in lists[k]
               if norm_domain(r["domain"]) in held])

    # A list for the person, in signal order.
    queue = []
    for r in lists["A"]:
        d = norm_domain(r["domain"])
        sig = sorted(fresh[d].items(), key=lambda kv: key_rank(kv[0]))
        lead_key, (lead_date, _) = sig[0]
        queue.append((key_rank(lead_key), -lead_date.toordinal(), d, r, sig))
    queue.sort(key=lambda t: t[:3])
    write_csv(os.path.join(out, "a-list-queue.csv"),
              ["company", "domain", "linkedin_company_url", "signals_in_order", "evidence_urls"],
              [[t[3]["company"], t[2], t[3]["linkedin_company_url"],
                " | ".join("%s %s" % (k, v[0]) for k, v in t[4]), " | ".join(v[1] for _, v in t[4])]
               for t in queue])

    def upload_rows(rs):
        return [[r["company"], norm_domain(r["domain"]), norm_domain(r["domain"]), r["linkedin_company_url"],
                 "", "", "", "", r["country"], ""] for r in rs]

    files = []
    if na >= 300 and len(b_served) >= 300:
        write_csv(os.path.join(out, "upload-a.csv"), UPLOAD_HEADER, upload_rows(lists["A"]), True)
        write_csv(os.path.join(out, "upload-b.csv"), UPLOAD_HEADER, upload_rows(b_served), True)
        files.append("upload-a.csv: %s rows. upload-b.csv: %s rows." % (n(na), n(len(b_served))))
        ride = "A and served B each have 300 rows or more, so they upload as two lists."
    else:
        ab = lists["A"] + b_served
        write_csv(os.path.join(out, "upload-ab.csv"), UPLOAD_HEADER, upload_rows(ab), True)
        line = "upload-ab.csv: %s rows (A %s + B %s served)." % (n(len(ab)), n(na), n(len(b_served)))
        if len(ab) < 300:
            line += (" UNDER 300 rows: LinkedIn will not take it. Widen the signal set, or run the whole list cold, as a fit list. Adding C companies "
                     "here would put them on the warm dose.")
        files.append(line)
        ride = "A rides with B: %s rows, %s 300." % (n(len(ab)), "over" if len(ab) >= 300 else "UNDER")
    write_csv(os.path.join(out, "upload-c.csv"), UPLOAD_HEADER, upload_rows(lists["C"]), True)
    excl_holdout = [r for k in ("A", "B", "C") for r in lists[k] if norm_domain(r["domain"]) in held]
    write_csv(os.path.join(out, "exclude-holdout.csv"), UPLOAD_HEADER, upload_rows(excl_holdout), True)
    excl_crm = sorted({norm_domain(r["domain"]): r for r in crm if r["domain"]
                       and stage.get(norm_domain(r["domain"])) in ("won", "open")}.values(),
                      key=lambda r: norm_domain(r["domain"]))
    write_csv(os.path.join(out, "exclude-crm.csv"), UPLOAD_HEADER,
              [[r["company"], norm_domain(r["domain"]), norm_domain(r["domain"]), "", "", "", "", "", "", ""]
               for r in excl_crm], True)
    cline = "upload-c.csv: %s rows." % n(nc)
    if nc < 300:
        cline += " Under 300 rows: leave C out this month, or widen the fit list."
    files.append(cline)

    warm = na + nb
    warm_rows = na + len(b_served)
    share_txt = "{:.1f}".format(100.0 * warm / total) if total else "0.0"
    if warm_rows >= UPLOAD_FLOOR:
        v1 = "%s of %s companies (%s%%) have a dated reason to buy now (A and B): warm." % (n(warm), n(total), share_txt)
    else:
        v1 = ("%s of %s companies (%s%%) have a dated reason to buy now (A and B), %s rows to serve. Under 300 rows "
              "there is no warm list yet: widen the signal set, or run the whole list cold, as a fit list." % (
                  n(warm), n(total), share_txt, n(warm_rows)))
    v2 = "%s are fit only (C): cold until a signal moves them in." % n(nc)
    if a.holdout_in:
        v3 = "%s companies held back as the test, no ads and no messages (this quarter's file)." % n(len(held))
    elif held:
        v3 = "%s warm companies held back as the test, no ads and no messages." % n(len(held))
    else:
        v3 = "No holdout this quarter: the warm list can't spare %s companies and still serve." % HOLDOUT_FLOOR
    lines = ["# Signal list check, %s" % human(today), "",
             "Files read: %s (%s rows), %s (%s rows)%s." % (
                 os.path.basename(a.accounts), n(len(accounts)), os.path.basename(a.signals), n(len(signals)),
                 (", %s (%s rows)" % (os.path.basename(a.crm), n(len(crm)))) if a.crm else ""),
             "", "## Verdict", "", v1, v2, v3, "",
             "%s companies: %s A, %s B, %s C. %s" % (n(total), n(na), n(nb), n(nc), ride),
             "", "## Removed before the split (names never shown)", ""]
    order = ["duplicate row", "customer", "open deal", "competitor", "employee", "not a fit", "placeholder page"]
    rem = [k for k in order if removed.get(k)] + sorted(k for k in removed if k not in order)
    lines.append(", ".join("%s %s" % (k, removed[k]) for k in rem) + (". Total %s." % n(sum(removed.values()))
                 if removed else "None."))
    if no_domain:
        lines.append("%s kept rows have no domain, so no signal can join them. They stay in C." % n(no_domain))
    lines += ["", "## Signal rows", "",
              "Read %s. Kept %s." % (n(len(signals)), n(stats["kept"])) + (" Dropped: " + ", ".join(
                  "%s %s" % (k, stats[k]) for k in ["no evidence link", "expired", "date after today",
                                                     "unreadable date", "company not on the list, or removed"]
                  if stats.get(k)) + "." if sum(v for k, v in stats.items() if k != "kept") else ""),
              "One signal firing twice is still one signal: each company counts different signal keys.",
              "", "## Holdout", "", carve_note]
    if underpowered:
        lines.append("The warm list can't spare that many and still serve, so the holdout is smaller. A holdout this "
                     "small cannot show a difference.")
    if held:
        exp = len(held) / 200.0
        exp_txt = "half a meeting" if exp == 0.5 else "%s meeting%s" % ("{:g}".format(round(exp, 1)), "" if exp == 1 else "s")
        lines.append("Take an example rate, not a forecast: if 1 company in 200 books a meeting in a quarter, a holdout "
                     "of %s expects %s. Read it only at quarter end, as two counts with both list sizes, never as a "
                     "lift." % (n(len(held)), exp_txt))
        lines.append("Keep holdout.csv all quarter. At each monthly refresh, pass it back in with --holdout-in. "
                     "Also save this master.csv as master-carve.csv: the quarter-end count compares the groups of this day.")
    files.append("exclude-holdout.csv: %s rows. exclude-crm.csv: %s rows (customers and open deals). Upload each once "
                 "and add both as excluded company lists on every other ad set in the account." % (
                     n(len(excl_holdout)), n(len(excl_crm))))
    lines += ["", "## Upload files (LinkedIn's company template, holdout removed)", ""] + files + [
        "", "LinkedIn takes a company list from 300 rows and serves it once 300 members match, not 300 companies. "
        "It recommends 1,000 or more companies. Matching can take up to 48 hours, on rare occasions longer. In the EEA and Switzerland only "
        "members who opted in are matched, so those lists come out smaller.",
        "Upload in Campaign Manager: Plan, Audiences, Create audience, Matched Audience, Company / Contact. You upload. This check does not.",
        "Next: 48 hours after upload, type the matched member count of each list. Under 300, it does not serve.",
        "", "## For the person", "",
        "a-list-queue.csv: %s A companies in signal order (new leader, then a job ad that names the tools, "
        "then funding, then the rest, newest first)." % n(na), "", "## Next dates", ""]
    drops.sort()
    if drops:
        first = drops[0][0]
        same = [x for x in drops if x[0] == first]
        lines.append("First drop: %s, when %s %s leave%s their list." % (
            human(first), n(len(same)), "company" if len(same) == 1 else "companies", "s" if len(same) == 1 else ""))
        nxt = [x for x in drops if x[0] < today + datetime.timedelta(days=30)]
        lines.append("Drops in the next 30 days: %s. Each row's date sits in master.csv, drops_list_on." % n(len(nxt)))
        lines.append("Drops take effect at the next monthly refresh. A replaced list takes up to 48 hours to match again.")
    lines += ["", "## Freshness windows used (my defaults, not measured)", "",
              ", ".join("%s %s days" % (k, windows[k]) for k in ORDER + ["ad_alert"]) +
              ", any other key %s days." % windows["other"],
              "A signal counts while it is younger than its window. On signal date + window it expires.", ""]
    with open(os.path.join(out, "list-report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


def retrain(a):
    out = a.out
    os.makedirs(out, exist_ok=True)
    today, since = parse_date(a.today), parse_date(a.since)
    if not today or not since:
        die("--today and --since must be dates like 2027-02-01")
    windows = dict(WINDOWS)
    for w in a.window or []:
        k, _, v = w.partition("=")
        windows[k.strip().lower()] = int(v)
    deals = read_csv(a.retrain, DEAL_COLS)
    unread = [dl["first_call_date"] for dl in deals if not read_day(dl["first_call_date"], MONTH_FIRST[0])[1]]
    if unread:
        die("%s first_call_date value(s) I could not read safely, for example %s. Write them as 2027-02-01 and rerun."
            % (len(unread), unread[0]))
    signals = read_csv(a.signals, SIG_COLS)
    master = read_csv(a.master, ["company", "domain", "list", "signals", "holdout"])
    mlist = {norm_domain(r["domain"]): r for r in master}

    sigs = collections.defaultdict(list)
    for s in signals:
        dt = parse_date(s["signal_date"])
        if dt and s["evidence_url"]:
            sigs[norm_domain(s["domain"])].append((s["signal_key"].lower(), dt))

    groups = {"A": [0, 0], "B served": [0, 0], "holdout": [0, 0], "C": [0, 0]}
    for r in master:
        g = "holdout" if r["holdout"] == "yes" else ("B served" if r["list"] == "B" else r["list"])
        groups[g][1] += 1
    off_list, before, undated = 0, 0, 0
    table = collections.defaultdict(lambda: collections.Counter())
    called = set()
    won_total = 0
    for dl in deals:
        d = norm_domain(dl["domain"])
        fc = parse_date(dl["first_call_date"])
        if not fc or fc > today:
            undated += 1
            continue
        if fc < since:
            before += 1
            continue
        if d not in mlist:
            off_list += 1
            continue
        called.add(d)
        m = mlist[d]
        g = "holdout" if m["holdout"] == "yes" else ("B served" if m["list"] == "B" else m["list"])
        groups[g][0] += 1
        stage = dl["deal_stage"].lower()
        if stage == "won":
            won_total += 1
        keys = {k for k, dt in sigs.get(d, []) if dt < fc and (fc - dt).days < windows.get(k, windows["other"])}
        for k in keys:
            table[k][stage if stage in ("won", "lost", "open") else "open"] += 1
    for r in master:
        d = norm_domain(r["domain"])
        if d in called or r["holdout"] == "yes":
            continue
        for k in [x.strip() for x in r["signals"].split("|") if x.strip()]:
            table[k]["no call"] += 1

    lines = ["# Signal list retrain, %s" % human(today), "",
             "First calls counted from %s (the list went live) to %s." % (human(since), human(today)), "",
             "## Meetings per group (counts, never a lift)", "",
             "B served: %s of %s companies had a first call." % (groups["B served"][0], n(groups["B served"][1])),
             "Holdout (from B, never served): %s of %s." % (groups["holdout"][0], n(groups["holdout"][1])),
             "This pair is the comparison: the same B list, one part served, one part held out.",
             "Expected in the holdout at the served B rate: %s x %s / %s = %s. Observed: %s. At these sizes only a gap of several meetings means anything." % (
                 groups["B served"][0], n(groups["holdout"][1]), n(groups["B served"][1]),
                 "{:.1f}".format(groups["B served"][0] * groups["holdout"][1] / groups["B served"][1]) if groups["B served"][1] else "0",
                 groups["holdout"][0]),
             "For reference, not compared with the holdout: A %s of %s, C %s of %s. A and C differed from B before the first ad." % (
                 groups["A"][0], n(groups["A"][1]), groups["C"][0], n(groups["C"][1])),
             "First calls with companies not on the list: %s. Before the list went live: %s. No first call date: %s. None of these is part of the comparison." % (
                 off_list, before, undated),
             "", "## Signals that sat on each company before its first call", "",
             "| signal | won | lost | open | on the list, no call |", "|---|---|---|---|---|"]
    for k in sorted(table, key=lambda k: (-table[k]["won"], table[k]["lost"], key_rank(k))):
        t = table[k]
        lines.append("| %s | %s | %s | %s | %s |" % (k, t["won"], t["lost"], t["open"], n(t["no call"])))
    lines += ["", "A signal counts here when it was dated before the first call and still inside its window on that day.",
              "", "## Proposal", ""]
    if won_total < 5:
        lines.append("Too few won deals (%s) to rank signals. Keep the menu as it is and read again next quarter." % won_total)
    else:
        lines.append("Proposed order for next quarter: the table order above (most won first, then fewest lost).")
    lines += ["A person decides. Never read this table as cause: a won company had other reasons too.", ""]
    with open(os.path.join(out, "retrain-report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


def main():
    p = argparse.ArgumentParser(description="signal-list-check: A, B and C lists from dated public signals.")
    p.add_argument("--accounts")
    p.add_argument("--signals", required=True)
    p.add_argument("--crm")
    p.add_argument("--today", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--names")
    p.add_argument("--holdout-in", dest="holdout_in")
    p.add_argument("--window", action="append")
    p.add_argument("--retrain")
    p.add_argument("--master")
    p.add_argument("--since")
    p.add_argument("--month-first", action="store_true", help="read 11/3/2026 as 3 Nov (US exports)")
    a = p.parse_args()
    MONTH_FIRST[0] = a.month_first
    if a.retrain:
        if not a.master or not a.since:
            die("retrain mode needs --master and --since")
        retrain(a)
    else:
        if not a.accounts:
            die("month-start mode needs --accounts")
        month_start(a)


if __name__ == "__main__":
    main()
