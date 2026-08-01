# Q3 ADDENDUM — Opener-Aware Side Rule (added 7/31, frozen pre-run)
Motivation: 7/30 loss — side rule compared listed starters (Lowder 1.57 > Ramírez
1.38 → PIT) but Ramírez was a 1-inning opener before a bullpen day; winner took
the CIN side of our own stack game. 7/31 counter-case: Holton opened for DET but
Springs (1.88) was so bad both lenses agreed — rule must handle both.

## Definition
OPENER := listed starter whose trailing-window IP per appearance ≤ 3.0
(same window as the WHIP calc; require ≥2 appearances, else not classified).

## Q3 rule (TEST-C)
Within the selected stack game (top consensus total, per v1.5):
- If exactly ONE side's listed starter is an OPENER:
    stack the side FACING the opener (bats vs opener + bullpen),
    UNLESS the non-opener starter's trailing WHIP ≥ 1.75
    (historically-awful starter overrides; stack against him as usual).
- If both or neither are openers: standard v1.5 side rule (worse trailing WHIP).

## Measurement
Same slate set as Q1. CONTROL = standard side rule. TEST-C = rule above.
Report overall AND the FIRED subset (slates where picks differ): n, mean, p90,
disaster (<10 pts / 4 slots).

## Pass criteria (frozen)
- Fired subset n ≥ 8 AND TEST-C fired-subset mean ≥ CONTROL fired-subset
  mean + 3.0 AND overall disaster rate(TEST-C) ≤ overall disaster rate(CONTROL).
- If fired n < 8: verdict = INSUFFICIENT-N — no adoption, opener situations
  remain a logged judgment flag at build time (status quo), revisit at season end.

## Decision wiring (unchanged elsewhere)
Q3 is additive: it modifies only the side-selection step of whatever survives
Q1/Q2. Q1/Q2 criteria and decision table remain exactly as frozen 7/27.
