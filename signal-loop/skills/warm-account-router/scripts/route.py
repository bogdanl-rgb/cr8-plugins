#!/usr/bin/env python3
"""warm-account-router, by Bogdan Liutic, CR8 (cr8.eco). MIT License.

Ranks the companies on a signal list that engaged with LinkedIn ads, joins them to
site visits (company level) and CRM state, and drafts one card per company for a
person to approve. Writes crm-update.csv for the person to import into their CRM.
It sends nothing, writes to no CRM and changes nothing.

Read-only. Python 3.8 or later, standard library only, no network.

  python3 route.py --export companies-export.csv --master master.csv \
      --exclusions exclusions.txt --crm crm-accounts.csv --today 2026-11-09 --out out \
      [--visits site-visits.csv --leads leads.csv --public public-engagement.csv] \
      [--dose dose.csv --placeholder placeholder-summary.csv --last-week router_output.csv] \
      [--plan-engaged 10 --replies 0 --meetings 0 --owner-role "Head of Marketing" --buyer-role "VP Sales"]
Config: --paid-alone 10 --paid-min 3 --cooldown 14 --cap 5 --profile default|small-list
        --window-start / --window-end (default: the 30 days before --today, 14 days on small-list)

Dates: 2026-11-02 is safest. LinkedIn's Leads export writes 11/2/2026, month first, and that is read.
In any other file a date like 3/4/2026 can mean 3 April or 4 March, so it stops the run, unless you
pass --month-first (every file writes the month first, as US exports do). A date that cannot be read
stops the run too, so no form fill or cooldown is lost in silence.
"""
import argparse
import collections
import csv
import datetime
import os
import re
import statistics
import sys

ORDER = ["new_leader", "job_post_names_tool", "funding", "hiring_for_role", "product_launch"]
LABEL = {"new_leader": "new leader in the role", "job_post_names_tool": "job ad that names the tools",
         "funding": "funding", "hiring_for_role": "hiring for the role", "product_launch": "product launch",
         "ad_alert": "ad alert"}
OUT_COLS = ["company", "domain", "list", "list_move", "route", "reason", "paid_impressions", "paid_clicks",
            "paid_engagements", "second_signal", "crm_state", "owner", "roles_to_find", "timing", "thread_check",
            "card_approved_at", "first_message_at", "lag_hours", "next_review_date"]
EXPORT_COLS = ["Company name", "Company page URL", "Organic engagements", "Paid impressions", "Paid clicks",
               "Paid engagements"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
CAREERS = re.compile(r"/(careers?|jobs?)(/|$)")
STAGE_RANK = {"won": 0, "open": 1, "lost": 2, "none": 3}  # one row a company: the strongest stage wins
SMALL = 10  # under this many staff a company row can point to one person: no card, no note, no list move
UNREAD = collections.Counter()
MONTH_FIRST = [False]  # set by --month-first


def die(msg):
    sys.stderr.write("warm-account-router: " + msg + "\n")
    sys.exit(2)


def read(path, needed):
    if not path:
        return []
    if not os.path.exists(path):
        die("file not found: " + path)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        header = [h.strip() for h in (rd.fieldnames or [])]
        missing = [c for c in needed if c not in header]
        if missing:
            die("%s is missing column(s): %s. Header was: %s" % (path, ", ".join(missing), ", ".join(header)))
        return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in rd]


def norm(s):
    s = re.sub(r"\([^)]*\)", " ", (s or "").lower())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def norm_url(u):
    u = (u or "").strip().lower().split("?")[0]
    u = re.sub(r"^[a-z]+://", "", u)
    if u.startswith("www."):
        u = u[4:]
    return u.rstrip("/")


def norm_domain(s):
    s = re.sub(r"^[a-z]+://", "", (s or "").strip().lower()).split("/")[0]
    return (s[4:] if s.startswith("www.") else s).rstrip(".")


def num(x):
    x = (x or "").replace(",", "").strip()
    try:
        return int(float(x)) if x else None
    except ValueError:
        return None


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


def day(s, where=None, month_first=False):
    d, ok = read_day(s, month_first or MONTH_FIRST[0])
    if not ok and where:
        UNREAD[where] += 1
    return d


def strongest(rows, key, where=None):
    """A CRM export can hold one row a deal. Keep one row a company: the strongest stage (won, open, lost,
    none), the newest stage_date among those, and the latest last_outbound_date across all its rows."""
    best = {}
    for c in rows:
        k = key(c)
        if not k:
            continue
        st = c["deal_stage"].lower()
        rank = STAGE_RANK.get(st, 3)
        sd = day(c["stage_date"], where) or datetime.date.min
        lo = day(c["last_outbound_date"], where)
        cur = best.get(k)
        if cur is None or (rank, -sd.toordinal()) < (cur["_rank"], -cur["_sd"].toordinal()):
            keep_lo = cur["_lo"] if cur else None
            cur = dict(c)
            cur.update({"_rank": rank, "_sd": sd, "_lo": keep_lo})
            best[k] = cur
        if lo and (cur["_lo"] is None or lo > cur["_lo"]):
            cur["_lo"] = lo
    for c in best.values():
        c["last_outbound_date"] = str(c["_lo"]) if c["_lo"] else ""
    return best


def stamp(s):
    """'2026-11-09 10:30' (or with seconds, or a T) -> datetime. A bare date counts as midnight."""
    s = (s or "").strip().replace("T", " ")[:16]
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def span(d1, d2):
    left = "%d %s" % (d1.day, MONTHS[d1.month - 1]) + ("" if d1.year == d2.year else " %d" % d1.year)
    return "%s to %s" % (left, human(d2))


def cap1(s):
    return s[:1].upper() + s[1:]


def human(d):
    return "%d %s %d" % (d.day, MONTHS[d.month - 1], d.year) if d else ""


def key_rank(k):
    return (ORDER.index(k), k) if k in ORDER else (len(ORDER), k)


def main():
    p = argparse.ArgumentParser(description="warm-account-router")
    for a_ in ("export", "master", "exclusions", "crm", "today", "out"):
        p.add_argument("--" + a_, required=True)
    for a_ in ("visits", "leads", "public", "dose", "placeholder", "last-week", "window-start", "window-end"):
        p.add_argument("--" + a_)
    p.add_argument("--plan-engaged", type=int)
    p.add_argument("--replies", type=int)
    p.add_argument("--meetings", type=int)
    p.add_argument("--owner-role", default="the person who would own what you sell")
    p.add_argument("--buyer-role", help="the economic buyer at companies of 50 staff or more "
                                         "(default: the VP or C-level who owns the budget)")
    p.add_argument("--paid-alone", type=int, default=10)
    p.add_argument("--paid-min", type=int, default=3)
    p.add_argument("--cooldown", type=int, default=14)
    p.add_argument("--cap", type=int, default=5)
    p.add_argument("--profile", choices=["default", "small-list"], default="default")
    p.add_argument("--month-first", action="store_true", help="read 11/3/2026 as 3 Nov in every file (US exports)")
    a = p.parse_args()
    MONTH_FIRST[0] = a.month_first
    os.makedirs(a.out, exist_ok=True)

    today = day(a.today) or die("--today must be a date like 2026-11-09")
    w_end = day(a.window_end) if a.window_end else today - datetime.timedelta(days=1)
    w_start = day(a.window_start) if a.window_start else today - datetime.timedelta(
        days=14 if a.profile == "small-list" else 30)

    if not os.path.exists(a.exclusions):
        die("exclusions.txt not found. Run placeholder-page-check first. Never rank without it.")
    excl = {norm(x) for x in open(a.exclusions, encoding="utf-8") if x.strip() and not x.startswith("#")}
    export = read(a.export, EXPORT_COLS)
    master = read(a.master, ["company", "domain", "linkedin_company_url", "employees", "list", "signals",
                             "signal_dates", "holdout"])
    crm = read(a.crm, ["company", "domain", "deal_stage", "owner", "stage_date", "last_outbound_date"])
    visits = read(a.visits, ["domain", "visit_date", "page"])
    leads = read(a.leads, ["lead_id", "created_date", "form_id", "test_lead", "email_domain"])
    public = read(a.public, ["domain", "date", "what"])

    if a.placeholder and os.path.exists(a.placeholder):
        for ph in read(a.placeholder, ["window"]):
            mw = re.match(r"\s*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})\s*$", ph["window"])
            if mw and (day(mw.group(1)), day(mw.group(2))) != (w_start, w_end):
                die("placeholder-page-check read %s, this run reads %s to %s. Use one window: pass --window-start and "
                    "--window-end, or rerun the placeholder check." % (ph["window"], w_start, w_end))

    m_url = {norm_url(m["linkedin_company_url"]): m for m in master if m["linkedin_company_url"]}
    m_name = {}
    for m in master:
        m_name.setdefault(norm(m["company"]), m)
    c_dom = strongest(crm, lambda c: norm_domain(c["domain"]), "crm-accounts.csv")
    c_name = strongest(crm, lambda c: norm(c["company"]))

    def inwin(d):
        return d is not None and w_start <= d <= w_end

    vdays = collections.defaultdict(set)
    careers_only = set()
    for v in visits:
        d = day(v["visit_date"], "site-visits.csv")
        if not inwin(d):
            continue
        dom = norm_domain(v["domain"])
        if CAREERS.search(v["page"].lower()):
            careers_only.add(dom)
            continue
        vdays[dom].add(d)
    forms = collections.defaultdict(list)
    test_dropped = 0
    for l in leads:
        if l["test_lead"].lower() in ("true", "yes", "1"):
            test_dropped += 1
            continue
        d = day(l["created_date"], "leads.csv", month_first=True)
        if inwin(d):
            forms[norm_domain(l["email_domain"])].append(d)
    pub = collections.defaultdict(list)
    for r in public:
        d = day(r["date"], "public-engagement.csv")
        if inwin(d):
            pub[norm_domain(r["domain"])].append((d, r["what"]))

    def seconds(dom):
        out = []
        if len(vdays.get(dom, ())) >= 2:
            out.append("return visit (%d days, last %s)" % (len(vdays[dom]), human(max(vdays[dom]))))
        for d in sorted(forms.get(dom, [])):
            out.append("form fill %s" % human(d))
        for d, what in sorted(pub.get(dom, [])):
            out.append("%s %s" % (what, human(d)))
        return out

    if UNREAD:
        die("dates I could not read safely: %s. Write them as 2026-11-02 and rerun. A date like 3/4/2026 can mean "
            "3 April or 4 March." % ", ".join("%s in %s" % (v, k) for k, v in sorted(UNREAD.items())))

    struck = 0
    with_numbers = 0
    rows = {}
    excluded_served, not_on_list, holdout_served, customers_on_list = [], [], [], []
    seen_domains = {}
    for r in export:
        nm = norm(r["Company name"])
        if nm in excl:
            struck += 1
            continue
        pi, pc, pe, oe = (num(r["Paid impressions"]), num(r["Paid clicks"]), num(r["Paid engagements"]),
                          num(r["Organic engagements"]))
        if pi is None and pc is None and pe is None and oe is None:
            continue
        with_numbers += 1
        m = m_url.get(norm_url(r["Company page URL"])) or m_name.get(nm)
        if not m:
            c = c_name.get(nm)
            if c and c["deal_stage"].lower() in ("won", "open"):
                excluded_served.append((r, c, pe))
            else:
                not_on_list.append((r, pe))
            continue
        dom = norm_domain(m["domain"])
        prev = seen_domains.get(dom)
        if prev:  # a second page for the same company: add it up
            for k, v in (("pi", pi), ("pc", pc), ("pe", pe), ("oe", oe)):
                if v is not None:
                    prev[k] = (prev[k] or 0) + v
            continue
        seen_domains[dom] = {"m": m, "pi": pi, "pc": pc, "pe": pe, "oe": oe}

    results = []
    engaged = 0
    for dom, x in seen_domains.items():
        m, pi, pc, pe, oe = x["m"], x["pi"], x["pc"], x["pe"], x["oe"]
        if m["holdout"].lower() == "yes":
            if pi:
                holdout_served.append((m, pi))
            continue
        c = c_dom.get(dom)
        stage = c["deal_stage"].lower() if c else "none"
        if stage == "won":
            customers_on_list.append(m)
            continue
        sec = seconds(dom)
        if a.profile == "small-list":
            alert = pc is not None and pc >= 4  # my older line: 4 paid clicks in 14 days
        else:
            alert = pe is not None and (pe >= a.paid_alone or (pe >= a.paid_min and bool(sec)))
        if pe is not None and pe >= a.paid_min:
            engaged += 1
        if alert:
            cls = "alert"
        elif pe is not None and pe >= a.paid_min:
            cls = "watch"
        elif pe is None and oe:
            cls = "organic"
        elif sec:
            cls = "quiet with a second signal"
        else:
            continue
        results.append({"m": m, "dom": dom, "pi": pi, "pc": pc, "pe": pe, "oe": oe, "sec": sec, "cls": cls,
                        "crm": c, "stage": stage})

    def move(lst):
        return {"A": ("A", "stays A"), "B": ("A", "B to A"), "C": ("B", "C to B")}[lst]

    def is_small(m):
        emp = num(m["employees"])
        return emp is not None and emp < SMALL

    cards = []
    for r in results:
        m, c = r["m"], r["crm"]
        r["list_after"], r["move"] = m["list"], ""
        r["owner"] = c["owner"] if c else ""
        if r["cls"] != "alert":
            r["route"] = {"watch": "watch", "organic": "organic", "quiet with a second signal": "quiet"}[r["cls"]]
            continue
        if is_small(m):  # before the CRM: ad data at a company this small can point to one person
            r["route"] = "under 10 staff"
            r["reason"] = "under 10 staff: a company row can point to one person, so no card, no note and no list move"
            continue
        if r["stage"] == "open":
            r["route"], r["reason"] = "note to owner", "open deal: tell the owner, no new outreach"
            r["crm_state"] = "open deal since %s" % human(day(c["stage_date"])) if c and day(c["stage_date"]) else "open deal"
            continue
        r["list_after"], r["move"] = move(m["list"])
        last_out = day(c["last_outbound_date"]) if c else None
        if last_out and (today - last_out).days < a.cooldown:
            r["route"] = "cooldown"
            r["reason"] = "you wrote on %s: no card until %s" % (human(last_out), human(last_out + datetime.timedelta(days=a.cooldown)))
            continue
        if r["stage"] == "lost":
            lost = day(c["stage_date"])
            sd = [day(x) for x in m["signal_dates"].split("|") if day(x)]
            after = [d for d in sd if lost and d > lost]
            r["crm_state"] = "lost %s" % human(lost)
            if not after:
                r["route"], r["reason"] = "park", "lost deal, no public signal since the loss"
                continue
            r["crm_state"] += ", public signal since"
        cards.append(r)

    lrank = {"A": 0, "B": 1, "C": 2}
    cards.sort(key=lambda r: (lrank[r["list_after"]], -(r["pe"] or 0), -len(r["sec"]), r["dom"]))
    for i, r in enumerate(cards):
        r["route"] = "card" if i < a.cap else "card next week"

    def roles(m):
        emp = num(m["employees"])
        buyer = "founder or CEO" if emp is not None and emp < 50 else (a.buyer_role or "the VP or C-level who owns the budget")
        if emp is None:
            timing = "size unknown: write to the next person once the last has had 7 days to reply"
        elif emp < 50:
            timing = "%s staff: day 0, 3 and 7" % emp
        elif emp <= 200:
            timing = "%s staff: write to the next person once the last has had 7 days to reply" % emp
        else:
            timing = "%s staff: all at once" % "{:,}".format(emp)
        return "%s, then %s, then whoever would run it" % (a.owner_role, buyer), timing

    def why(r):
        if r["pe"] is not None and r["pe"] >= a.paid_alone:
            return "%s paid engagements is at or above %s on its own." % (r["pe"], a.paid_alone)
        return "%s paid engagements plus %s." % (r["pe"], " and ".join(r["sec"]))

    order = {"card": 0, "card next week": 1, "note to owner": 2, "park": 3, "cooldown": 4, "under 10 staff": 5,
             "watch": 6, "organic": 7, "quiet": 8}
    results.sort(key=lambda r: (order[r["route"]], lrank[r["m"]["list"]], -(r["pe"] or 0), r["dom"]))
    out_rows = []
    for r in results:
        m = r["m"]
        rl, tm = roles(m) if r["route"] in ("card", "card next week") else ("", "")
        if r["route"] in ("card", "card next week"):
            r["reason"] = why(r)
        elif r["route"] == "watch":
            r["reason"] = "%s paid engagements, no second signal" % r["pe"]
        elif r["route"] == "organic":
            r["reason"] = "organic engagement only: labeled, no alert"
        elif r["route"] == "quiet":
            r["reason"] = "second signal, paid engagements under LinkedIn's reporting minimum"
        crm_state = r.get("crm_state") or ("no deal" if r["stage"] == "none" else r["stage"])
        nxt = today + datetime.timedelta(days=14 if r["route"] in ("card", "note to owner", "park", "cooldown") else 7)
        out_rows.append([m["company"], r["dom"], m["list"], r["move"], r["route"], r["reason"],
                         "" if r["pi"] is None else r["pi"], "" if r["pc"] is None else r["pc"],
                         "" if r["pe"] is None else r["pe"], " | ".join(r["sec"]), crm_state, r["owner"], rl, tm,
                         "not run" if r["route"] == "card" else "", "", "", "", str(nxt)])
    for m, pi in holdout_served:
        out_rows.append([m["company"], norm_domain(m["domain"]), m["list"], "", "holdout check",
                         "held-out company served (%s paid impressions): check pages that share its name or parent" % pi,
                         pi, "", "", "", "", "", "", "", "", "", "", "", ""])
    for r, c, pe in excluded_served:
        out_rows.append([r["Company name"], norm_domain(c["domain"]), "off list", "", "excluded but served",
                         "%s in your CRM, yet served: check your exclusions" % ("customer" if c["deal_stage"].lower() == "won" else "open deal"),
                         num(r["Paid impressions"]) or "", num(r["Paid clicks"]) or "", pe if pe is not None else "",
                         "", c["deal_stage"].lower(), c["owner"], "", "", "", "", "", "", ""])
    with open(os.path.join(a.out, "router_output.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(OUT_COLS)
        w.writerows(out_rows)

    alerts = [r for r in results if r["cls"] == "alert"]
    moved = [r for r in alerts if r["move"] in ("B to A", "C to B")]
    with open(os.path.join(a.out, "signals-to-add.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["domain", "signal_key", "signal_date", "evidence_url"])
        for r in alerts:
            if r["stage"] != "open" and r["route"] != "under 10 staff":
                w.writerow([r["dom"], "ad_alert", str(today), "companies export %s to %s, %s paid engagements" % (
                    w_start, w_end, r["pe"])])

    # A company under 10 staff stays on the A queue on its public signals alone, with no ad numbers shown.
    routed = {r["dom"] for r in results if r["cls"] == "alert" and r["route"] != "under 10 staff"}
    engaged_rows = {d: x for d, x in seen_domains.items()}
    aq, aq_written = [], 0
    for m in master:
        dom = norm_domain(m["domain"])
        c = c_dom.get(dom)
        stage = c["deal_stage"].lower() if c else "none"
        if m["list"] != "A" or m["holdout"].lower() == "yes" or dom in routed or stage in ("won", "open"):
            continue
        x = None if is_small(m) else engaged_rows.get(dom)
        keys = [k.strip() for k in m["signals"].split("|") if k.strip()]
        dates = [day(d) for d in m["signal_dates"].split("|") if day(d)]
        # Each A company is written to once. A company you wrote to, or a lost deal, comes back only with a
        # public signal dated after that, and never inside the cooldown.
        last_out = day(c["last_outbound_date"]) if c else None
        lost_on = day(c["stage_date"]) if c and stage == "lost" else None
        since = max([d for d in (last_out, lost_on) if d] or [None]) if (last_out or lost_on) else None
        if since and not any(d > since for d in dates):
            aq_written += 1
            continue
        if last_out and (today - last_out).days < a.cooldown:
            aq_written += 1
            continue
        if last_out:
            status = "new signal since you wrote on %s" % human(last_out)
        elif lost_on:
            status = "lost %s, new signal since" % human(lost_on)
        else:
            status = "not written yet"
        first = key_rank(keys[0]) if keys else (99, "")
        aq.append((first, -(dates[0].toordinal() if dates else 0), -((x or {}).get("pe") or 0), dom, m, x, status))
    aq.sort(key=lambda t: t[:4])
    aq_small = sum(1 for t in aq if is_small(t[4]))
    with open(os.path.join(a.out, "a-queue.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["company", "domain", "status", "paid_engagements", "signals"])
        for t in aq:
            pe = (t[5] or {}).get("pe")
            w.writerow([t[4]["company"], t[3], t[6], "" if pe is None else pe, t[4]["signals"]])

    last = read(a.last_week, ["route", "card_approved_at", "first_message_at"]) if a.last_week else []
    approved = [r for r in last if r["card_approved_at"]]
    firsts = [r for r in approved if r["first_message_at"]]
    lags, same_day = [], 0
    for r in firsts:
        t0, t1 = stamp(r["card_approved_at"]), stamp(r["first_message_at"])
        if t0 and t1:
            lags.append((t1 - t0).total_seconds() / 3600.0)
            same_day += 1 if t1.date() == t0.date() else 0

    placeholder = read(a.placeholder, ["flag", "click_share", "names_to_exclude"]) if a.placeholder else []
    dose = read(a.dose, ["ad_set_name", "verdict"]) if a.dose else []
    card_rows = [r for r in results if r["route"] == "card"]
    notes = [r for r in results if r["route"] == "note to owner"]

    def sig_text(m):
        keys = [k.strip() for k in m["signals"].split("|") if k.strip()]
        dates = [d.strip() for d in m["signal_dates"].split("|") if d.strip()]
        return ". ".join("%s, %s" % (cap1(LABEL.get(k, k)), human(day(d))) for k, d in zip(keys, dates))

    # The hand-off to the CRM: one row a company, keyed on its website domain. The person imports it or pastes
    # each row into a task. This script never writes to a CRM.
    crm_rows = []
    for r in card_rows:
        rl, tm = roles(r["m"])
        crm_rows.append([r["dom"], r["m"]["company"], r["list_after"], "card", str(today), r["owner"],
                         str(today + datetime.timedelta(days=14)),
                         "Why now: %s Public signal: %s. Look for: %s. %s. Name only what is public." % (
                             why(r), sig_text(r["m"]) or "none on file", rl, cap1(tm))])
    for r in notes:
        crm_rows.append([r["dom"], r["m"]["company"], r["m"]["list"], "note to owner", str(today), r["owner"],
                         str(today + datetime.timedelta(days=14)),
                         "Open deal: %s paid engagements in 30 days%s. Tell the owner. No new outreach." % (
                             r["pe"], (", plus " + " and ".join(r["sec"])) if r["sec"] else "")])
    with open(os.path.join(a.out, "crm-update.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["company_domain", "company", "signal_list", "route", "alert_date", "owner", "next_review_date",
                    "card_summary"])
        w.writerows(crm_rows)
    L = ["# Monday brief, %s" % human(today), "",
         "Window: %s. Companies export, %s rows." % (span(w_start, w_end), "{:,}".format(len(export))),
         "", "## The line", "",
         "%s list compan%s hit the alert line. %s card%s to approve. %s note%s. 0 sent." % (
             len(alerts), "y" if len(alerts) == 1 else "ies", len(card_rows), "" if len(card_rows) == 1 else "s",
             len(notes), " to a deal owner" if len(notes) == 1 else "s to deal owners"),
         "", "This week, in order: %s, then a-queue.csv (%s A compan%s with no card or note, in signal order, from day 7 of "
         "serving)%s." % (
             "the %s card%s below" % (len(card_rows), "" if len(card_rows) == 1 else "s") if card_rows else "no cards",
             len(aq), "y" if len(aq) == 1 else "ies",
             ", then unreached.csv from list-dose-check (an ad set is used up)"
             if any(d["verdict"] == "used up" for d in dose) else ""),
         "", "## Weekly chain, printed even at zero", "",
         "| engaged list companies | your plan | alerts | cards approved | first messages | same day as the yes | median hours to first message | replies | meetings |",
         "|---|---|---|---|---|---|---|---|---|",
         "| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
             engaged, a.plan_engaged if a.plan_engaged is not None else "not given", len(alerts), len(approved),
             len(firsts), same_day, "%.0f" % statistics.median(lags) if lags else "no data yet",
             a.replies if a.replies is not None else "not given", a.meetings if a.meetings is not None else "not given"),
         "", "Engaged means a list company outside the holdout with %s or more paid engagements shown. Cards approved, "
         "first messages and hours come from last week's router_output.csv%s." % (
             a.paid_min, "" if a.last_week else " (none given, so they start at zero)"),
         "", "## Checks", ""]
    if placeholder:
        ph = placeholder[0]
        L.append("Placeholder pages: %s, %s%% of paid clicks, %s names to exclude (placeholder-report.md). "
                 "%s export rows struck here." % (ph["flag"], ph["click_share"], ph["names_to_exclude"], struck))
    else:
        L.append("Placeholder pages: %s export rows struck by exclusions.txt." % struck)
    if dose:
        used = [d["ad_set_name"] for d in dose if d["verdict"] == "used up"]
        L.append("Dose: %s of %s ad sets used up%s (dose-report.md)." % (len(used), len(dose), (": " + ", ".join(used)) if used else ""))
    else:
        L.append("Dose: not read this week. Run list-dose-check for it.")
    if holdout_served:
        for m, pi in holdout_served:
            L.append("Holdout: %s was served (%s paid impressions). Check pages that share its name or parent." % (m["company"], pi))
    else:
        L.append("Holdout: no held-out company shows paid impressions.")
    for r, c, pe in excluded_served:
        L.append("Excluded but served: %s, a %s in your CRM, shows %s paid engagements. Check your exclusions." % (
            r["Company name"], "customer" if c["deal_stage"].lower() == "won" else "open deal",
            pe if pe is not None else "under-the-minimum"))
    if customers_on_list:
        L.append("Customers on your list: %s. Remove them at the next refresh." % len(customers_on_list))
    L += ["", "## Cards to approve (%s of %s allowed)" % (len(card_rows), a.cap), ""]
    for r in card_rows:
        m = r["m"]
        rl, tm = roles(m)
        keys = [k.strip() for k in m["signals"].split("|") if k.strip()]
        dates = [d.strip() for d in m["signal_dates"].split("|") if d.strip()]
        sig = ". ".join("%s, %s" % (cap1(LABEL.get(k, k)), human(day(d))) for k, d in zip(keys, dates))
        site = ("visits on %d days, last %s" % (len(vdays[r["dom"]]), human(max(vdays[r["dom"]])))
                if vdays.get(r["dom"]) else "no visits in the window")
        listline = "%s list" % m["list"] + (", moves to %s" % r["list_after"] if r["move"] in ("B to A", "C to B") else "")
        L += ["```",
              "%s · %s · %s · route: card" % (m["company"], listline, r.get("crm_state") or "no deal"),
              "Ads: %s paid engagements, %s paid clicks, %s paid impressions in 30 days. Site: %s." % (
                  r["pe"], r["pc"] if r["pc"] is not None else "under-the-minimum", r["pi"], site),
              "Public signal%s: %s." % ("s" if len(keys) > 1 else "", sig) if sig else
              "Public signal: none on file. Write only if you can name something public. Otherwise wait for one.",
              "Why now: %s" % why(r),
              "Look for, in order: %s. %s." % (rl, tm[0].upper() + tm[1:]),
              "Thread check: not run. Paste who sent the last message to each person, and the date. Not the text.",
              "Write: one message, from your own account. Name only what is public. Never the ads, the clicks or the visit.",
              "Approve? yes / no", "```", ""]
    if not card_rows:
        L += ["None this week.", ""]
    L += ["## Notes to deal owners", ""]
    for r in notes:
        L.append("%s (%s list), %s, owner %s: %s paid engagements in 30 days%s. Tell the owner. No new outreach." % (
            r["m"]["company"], r["m"]["list"], r.get("crm_state", "open deal"), r["owner"] or "not set", r["pe"],
            (", plus " + " and ".join(r["sec"])) if r["sec"] else ""))
    if not notes:
        L.append("None this week.")
    L += ["", "## For your CRM", "",
          "crm-update.csv: %s row%s, one a company (the cards and the notes above), keyed on the website domain. "
          "After your yes or no on each card, delete the rows you said no to. Then import the file into your CRM, or "
          "paste each row into a task on the company record, owned by the person who writes. This check never writes "
          "to your CRM." % (len(crm_rows), "" if len(crm_rows) == 1 else "s")]
    other = [r for r in results if r["route"] in ("park", "cooldown", "card next week")]
    if other:
        L += ["", "## Parked, cooling down or next week", ""]
        for r in other:
            L.append("%s (%s list): %s. %s." % (r["m"]["company"], r["m"]["list"], r["route"],
                                                 r.get("reason", "").rstrip(".")))
    watch = [r for r in results if r["route"] == "watch"]
    L += ["", "## Watch (%s to %s paid engagements, no second signal)" % (a.paid_min, a.paid_alone - 1), ""]
    L.append(", ".join("%s (%s list): %s" % (r["m"]["company"], r["m"]["list"], r["pe"]) for r in watch) + "." if watch else "None.")
    L += ["", "## Other", ""]
    for r in results:
        if r["route"] == "organic":
            L.append("Organic only: %s (%s list), %s organic engagements. Labeled organic, no alert." % (
                r["m"]["company"], r["m"]["list"], r["oe"]))
        if r["route"] == "quiet":
            L.append("Second signal, paid under the minimum: %s (%s list): %s. No alert. Look again next Monday." % (
                r["m"]["company"], r["m"]["list"], " and ".join(r["sec"])))
        if r["route"] == "under 10 staff":
            L.append("Under 10 staff, at the alert line: %s (%s list). No card, no note and no list move: a company "
                     "row this small can point to one person." % (r["m"]["company"], r["m"]["list"]))
    for r in moved:
        L.append("List move: %s %s. Add its row from signals-to-add.csv to your signal file before the next refresh." % (
            r["m"]["company"], r["move"]))
    if careers_only:
        L.append("Visits to careers or jobs pages are not counted as a second signal: %s compan%s had only those." % (
            len(careers_only - set(vdays)), "y" if len(careers_only - set(vdays)) == 1 else "ies"))
    if test_dropped:
        L.append("Test leads dropped: %s." % test_dropped)
    L.append("A list with no card or note this week: %s companies on a-queue.csv, in signal order, paid engagements shown. "
             "Write to each once, from day 7 of serving, and log the date in your CRM: the queue then drops the company "
             "until it has a new dated signal.%s%s" % (len(aq), (" Left out this week, written to or lost with no new "
                                                                "signal since: %s." % aq_written) if aq_written else "",
                                                       (" %s under 10 staff show no paid engagements: their public "
                                                        "signals alone keep them on the queue." % aq_small)
                                                       if aq_small else ""))
    matched = with_numbers - len(not_on_list) - len(excluded_served)
    L.append("Matched: %s of %s export rows with numbers matched your list. A low match share usually means a file "
             "problem: check the page URLs and names in master.csv." % (matched, with_numbers))
    top_off = sorted(not_on_list, key=lambda t: (-(t[1] or 0), t[0]["Company name"]))[:10]
    L.append("Not on your list: %s companies with numbers, %s paid engagements in all. Not routed.%s" % (
        len(not_on_list), sum(pe or 0 for _, pe in not_on_list),
        (" Most paid engagements first: %s. Check that none is a list company under another page URL or name." % (
            ", ".join("%s (%s)" % (r["Company name"], pe if pe is not None else "under the minimum") for r, pe in top_off)))
        if top_off else ""))
    L += ["", "Nothing was sent. Nothing was changed in any account.", "",
          "Checks by Bogdan Liutic, CR8 (cr8.eco). Want the loop run for you? [cr8.eco](https://cr8.eco/?utm_source=signal-loop-plugin)", ""]
    with open(os.path.join(a.out, "weekly-brief.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
