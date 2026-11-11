import sys, json; sys.path.insert(0,'/home/claude/bt/scripts')
from v4 import *
ARMS = {
 'V16_stack2':  dict(qb='gem', qb_cap=8300, wrte_salfloor=4500),
 'V16_stack1':  dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, stack_min=1),
 'V16_stack0':  dict(qb='gem', qb_cap=8300, wrte_salfloor=4500, stack_min=0),
}
R={}
for k,c in ARMS.items():
    R[k]=evaluate4(k,c); show4(R[k]); sys.stdout.flush()
    json.dump(R, open('/home/claude/bt/v4_stack.json','w'), indent=1)
