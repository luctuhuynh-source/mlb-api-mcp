#!/usr/bin/env python3
"""NFL betting run check. Reads a filled checklist, prints the status block.
Usage: python3 check_run.py <filled_checklist.json>
The block it prints goes at the very top of the reply to Phong, word for word.
This check verifies that every rule of the profile was answered. It cannot verify the answers."""
import json, sys, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VERSIONS = {"v05": {"1H": "NFL FG+1H v0.5", "2H": "NFL 2H v0.5"},
            "current": {"1H": "NFL FG+1H v0.6c", "2H": "NFL 2H v0.6a"}}

def main():
    if len(sys.argv) != 2:
        sys.exit("PROTOCOL RUN: STOPPED - no checklist file given")
    try:
        d = json.load(open(sys.argv[1]))
    except Exception as e:
        sys.exit("PROTOCOL RUN: STOPPED - checklist unreadable (%s)" % e)
    eng, prof = d.get("engine"), d.get("profile")
    if eng not in ("1H", "2H") or prof not in VERSIONS:
        sys.exit("PROTOCOL RUN: STOPPED - checklist needs engine = 1H or 2H and profile = v05 or current")
    tpl = json.load(open(os.path.join(HERE, "run_checklist_template.json")))
    want = {i["id"]: i for i in tpl["items"] if eng in i["engine"] and prof in i["profiles"]}
    got = {i.get("id"): i for i in d.get("items", [])}
    bad, done = [], 0
    for k, t in want.items():
        g = got.get(k)
        st = (g or {}).get("status", "").strip().lower()
        note = (g or {}).get("note", "").strip()
        if g is None:
            bad.append("%s missing from the checklist: %s (%s)" % (k, t["check"], t["rules"]))
        elif st == "done":
            done += 1
        elif st == "na" and note:
            done += 1
        elif st == "na":
            bad.append("%s marked not applicable with no reason: %s (%s)" % (k, t["check"], t["rules"]))
        elif st == "skipped":
            bad.append("%s SKIPPED: %s (%s)%s" % (k, t["check"], t["rules"], " - " + note if note else ""))
        else:
            bad.append("%s not answered: %s (%s)" % (k, t["check"], t["rules"]))
    if not d.get("games"):
        bad.append("no games listed")
    if not d.get("run_time_pt"):
        bad.append("run time (Pacific) not given")
    rules = os.path.join(HERE, "RULES_v05_baseline.md")
    rh = hashlib.sha256(open(rules, "rb").read()).hexdigest()[:16]
    ver = VERSIONS[prof][eng]
    bar = "=" * 100
    print(bar)
    if bad:
        print("PROTOCOL RUN: NOT FULL - %d item(s). This block goes at the very top of the reply to Phong, word for word." % len(bad))
        for n, b in enumerate(bad, 1):
            print("  %d. %s" % (n, b))
    else:
        print("PROTOCOL RUN: FULL - %s, profile %s, %d of %d checks answered. This line goes at the very top of the reply to Phong."
              % (ver, prof, done, len(want)))
    print("Engine %s | %s | games: %s | run %s PT | rule list hash %s" %
          (eng, ver, ", ".join(d.get("games", [])) or "-", d.get("run_time_pt") or "-", rh))
    print("This check confirms each rule was answered by the chat. It does not verify the answers, grading, or closing lines.")
    print(bar)

if __name__ == "__main__":
    main()
