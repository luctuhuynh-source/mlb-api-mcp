import sys, json; sys.path.insert(0,'/home/claude/bt/scripts')
from v4 import *
ARMS = {
 'V16_base':      dict(qb='gem', qb_cap=8300, wrte_salfloor=4500),
 'DS1_blend':     dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, ds=1),
 'DS1_props':     dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, ds=1, ds_by='props'),
 'DS2_blend':     dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, ds=2),
 'DS5_all':       dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, ds=5),
}
R={}
for k,c in ARMS.items():
    R[k]=evaluate4(k,c); show4(R[k]); sys.stdout.flush()
    json.dump(R, open('/home/claude/bt/v4_ds.json','w'), indent=1)
