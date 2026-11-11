import sys, json; sys.path.insert(0,'/home/claude/bt/scripts')
import lsbt
ARMS = {
 'LS_blend':   dict(qb='gem', qb_cap=8300, wrte_salfloor=4500),
 'v16_props':  dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, proj='v16'),
 'v17_hybrid': dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, proj='v17'),
 'props_only': dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, proj='props'),
 'v17_3x2':    dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, proj='v17', per_qb=2),
 'v17_pc_rb':  dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, proj='v17', pc_rb=True),
}
arms = sys.argv[1].split(',')
slates = [S for S in (lsbt.load_slate(f) for f in lsbt.slate_files()) if S and S['season']==2025 and 3<=S['week']<=12]
print('slates', [s['key'] for s in slates], flush=True)
R={}
for k in arms:
    R[k]=lsbt.evaluate(k, ARMS[k], slates); lsbt.show(R[k])
    json.dump(R, open(f'/home/claude/bt/ls/res_props_{arms[0]}.json','w'), indent=1)
