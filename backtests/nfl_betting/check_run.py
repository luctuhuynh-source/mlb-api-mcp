#!/usr/bin/env python3
"""NFL betting run check. Reads a filled checklist, prints the status block.
Usage: python3 check_run.py <filled_checklist.json>
The block it prints goes at the very top of the reply to Phong, word for word.
This check verifies that every rule of the profile was answered. It cannot verify the answers."""
import json, sys, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
VERSIONS = {"v05": {"1H": "NFL FG+1H v0.5", "2H": "NFL 2H v0.5"},
            "current": {"1H": "NFL FG+1H v0.6d", "2H": "NFL 2H v0.6c", "TOTALS": "NFL Totals v0.3"}}
# Phong, 11/12/2026: "Current but make this can fire by any books instead of dsb only."
PROFILE_IN_FORCE = "current"
# The flat rule list each profile is run from. Its hash is printed so two runs can be shown to have used the same text.
RULE_FILES = {"v05": "RULES_v05_baseline.md", "current": "RULES_CURRENT.md"}
RULES_TEXT_DATE = {"v05": "frozen 2026-10-11", "current": "rules text 2026-11-12, 6:55 PM"}

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
    rules = os.path.join(HERE, RULE_FILES[prof])
    rh = hashlib.sha256(open(rules, "rb").read()).hexdigest()[:16]
    ver = "%s (%s)" % (VERSIONS[prof][eng], RULES_TEXT_DATE[prof])
    if prof == "current" and eng == "2H":
        ver += " + " + VERSIONS[prof]["TOTALS"]
    bar = "=" * 100
    print(bar)
    if bad:
        print("PROTOCOL RUN: NOT FULL - %d item(s). This block goes at the very top of the reply to Phong, word for word." % len(bad))
        for n, b in enumerate(bad, 1):
            print("  %d. %s" % (n, b))
    else:
        print("PROTOCOL RUN: FULL - %s, profile %s, %d of %d checks answered. This line goes at the very top of the reply to Phong."
              % (ver, prof, done, len(want)))
    print("Engine %s | %s | games: %s | run %s PT | rule list %s hash %s" %
          (eng, ver, ", ".join(d.get("games", [])) or "-", d.get("run_time_pt") or "-", RULE_FILES[prof], rh))
    if prof != PROFILE_IN_FORCE:
        print("NOTE: the profile in force is '%s' (Phong, 11/12/2026). This run used '%s'. Say so at the top of the reply." % (PROFILE_IN_FORCE, prof))
    print("This check confirms each rule was answered by the chat. It does not verify the answers, grading, or closing lines.")
    print(bar)

if __name__ == "__main__":
    main()
