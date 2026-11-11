import sys, json, glob; sys.path.insert(0,'/home/claude/bt/scripts')
import lsbt
ARMS = {
 'A_v16_LS':      dict(qb='gem', qb_cap=8300, wrte_salfloor=4500),
 'B_pc_rb':       dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, pc_rb=True),
 'C_stack1':      dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, stack_min=1),
 'D_LS_only':     dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, blend=0.0),
 'E_old_band':    dict(qb='band', qb_hi=7600, wrte_salfloor=4500),
 'F_3x2':         dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, per_qb=2),
 'G_cap8500':     dict(qb='gem', qb_cap=8500, wrte_salfloor=4500),
 'H_nofloor':     dict(qb='gem', qb_cap=8300),
}
arms = sys.argv[1].split(','); sel = sys.argv[2] if len(sys.argv) > 2 else 'all'
slates = []
for f in lsbt.slate_files():
    S = lsbt.load_slate(f)
    if not S: continue
    if sel == '2026' and S['season'] != 2026: continue
    if sel == 'hist' and S['season'] == 2026: continue
    slates.append(S)
print('slates', len(slates), [s['key'] for s in slates][:3], '...', [s['key'] for s in slates][-2:], flush=True)
R = {}
for k in arms:
    R[k] = lsbt.evaluate(k, ARMS[k], slates); lsbt.show(R[k])
    json.dump(R, open(f'/home/claude/bt/ls/res_{sel}_{arms[0]}.json', 'w'), indent=1)
