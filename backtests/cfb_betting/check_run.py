#!/usr/bin/env python3
"""CFB betting run check. Reads a filled checklist, prints the status block that goes at the very top of the reply to Phong.
Usage: python3 check_run.py <filled_checklist.json>
It verifies that every rule was answered. It cannot verify the answers. Only this script prints FULL."""
import json, sys, os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINES = {"2H": ("CFB 2H v2.3b", "run_checklist_cfb_2h.json", "RULES_CFB_2H_CURRENT.md")}
NOT_PACKAGED = {"1H": "CFB 1H v2.0e"}
def main():
    if len(sys.argv) != 2: sys.exit("PROTOCOL RUN: STOPPED - no checklist file given")
    try: d = json.load(open(sys.argv[1]))
    except Exception as e: sys.exit("PROTOCOL RUN: STOPPED - checklist unreadable (%s)" % e)
    eng = d.get("engine")
    if eng in NOT_PACKAGED: sys.exit("PROTOCOL RUN: NOT RUN - %s has no checklist in the repo yet; run it from the doc tab and say so at the top" % NOT_PACKAGED[eng])
    if eng not in ENGINES: sys.exit("PROTOCOL RUN: STOPPED - checklist needs engine = 2H")
    ver, tplf, rulesf = ENGINES[eng]
    want = {i["id"]: i for i in json.load(open(os.path.join(HERE, tplf)))["items"]}
    got = {i.get("id"): i for i in d.get("items", [])}; bad, done = [], 0
    for k, t in want.items():
        g = got.get(k); st = (g or {}).get("status", "").strip().lower(); note = (g or {}).get("note", "").strip()
        if g is None: bad.append("%s missing from the checklist: %s (%s)" % (k, t["check"], t["rules"]))
        elif st == "done" or (st == "na" and note): done += 1
        elif st == "na": bad.append("%s marked not applicable with no reason: %s (%s)" % (k, t["check"], t["rules"]))
        elif st == "skipped": bad.append("%s SKIPPED: %s (%s)%s" % (k, t["check"], t["rules"], " - " + note if note else ""))
        else: bad.append("%s not answered: %s (%s)" % (k, t["check"], t["rules"]))
    if not d.get("games"): bad.append("no games listed")
    if not d.get("run_time_pt"): bad.append("run time (Pacific) not given")
    rh = hashlib.sha256(open(os.path.join(HERE, rulesf), "rb").read()).hexdigest()[:16]; bar = "=" * 100
    print(bar)
    if bad:
        print("PROTOCOL RUN: NOT FULL - %d item(s). This block goes at the very top of the reply to Phong, word for word." % len(bad))
        for n, b in enumerate(bad, 1): print("  %d. %s" % (n, b))
    else:
        print("PROTOCOL RUN: FULL - %s, %d of %d checks answered. This line goes at the very top of the reply to Phong." % (ver, done, len(want)))
    print("Engine %s | %s | games: %s | run %s PT | rule list %s hash %s" % (eng, ver, ", ".join(d.get("games", [])) or "-", d.get("run_time_pt") or "-", rulesf, rh))
    print("This check confirms each rule was answered by the chat. It does not verify the answers, grading, or closing lines.")
    print(bar)
if __name__ == "__main__": main()
