import sys, json; sys.path.insert(0,'/home/claude/bt/scripts')
from v4 import *
ARMS = {
 'V16_C2_strict':   dict(qb='gem', qb_cap=8300, wrte_salfloor=4500),
 'PC_rec3':         dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, pc_rb=3.0),
 'PC_rec25':        dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, pc_rb=2.5),
 'PC_any_rb':       dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, pc_rb=0.01),
}
R={}
for k,c in ARMS.items():
    R[k]=evaluate4(k,c); show4(R[k]); sys.stdout.flush()
    # count how often a same-team RB was actually used
    n=0
    for wk,v in R[k]['per'].items():
        for L in v['lineups']:
            q=[p for p in L if p['pos']=='QB']
            if q and any(p['pos']=='RB' and p['team']==q[0]['team'] for p in L): n+=1
    print(f"   same-team RB used in {n} lineups"); sys.stdout.flush()
    json.dump(R, open('/home/claude/bt/v4_pcrb.json','w'), indent=1)
