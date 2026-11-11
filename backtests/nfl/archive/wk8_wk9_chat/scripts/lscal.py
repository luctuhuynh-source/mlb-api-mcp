import sys, csv, re, json; sys.path.insert(0,'/home/claude/bt/scripts')
import lsbt
REAL = {2:'/mnt/user-data/uploads/134251-280648284.csv', 3:'/mnt/user-data/uploads/134503-280745135.csv', 4:'/mnt/user-data/uploads/134747-280845253.csv',
        5:'/mnt/user-data/uploads/135023-280945043.csv', 7:'/home/claude/bt/wk7/standings/million.csv'}
def real_pts(f):
    pts=[]
    with open(f, encoding='utf-8-sig', newline='') as fh:
        r=csv.reader(fh); next(r)
        for row in r:
            if row[0].strip() and row[3].strip() not in ('','null'): pts.append(float(row[3]))
    return sorted(pts)
files = {2:'2026-09-17_409',3:'2026-09-24_409',4:'2026-10-01_410',5:'2026-10-08_411',6:'2026-10-15_412',7:'2026-10-22_413'}
import glob
out=[]
for wk in (2,3,4,5,6,7):
    f=[x for x in glob.glob(lsbt.RAW+'2026-*') if lsbt.load_slate(x) and lsbt.load_slate(x)['week']==wk]
    if not f: print('no LS file wk',wk); continue
    S=lsbt.load_slate(f[0]); sp=lsbt.field_for(S)
    q=lambda a,p: a[min(len(a)-1,int(len(a)*p))]
    sim=[q(sp,.5),q(sp,.77),q(sp,.95),q(sp,.99)]
    if wk in REAL: rp=real_pts(REAL[wk]); real=[q(rp,.5),q(rp,.77),q(rp,.95),q(rp,.99)]
    elif wk==6: real=[112.1,128.8,144.7,157.9]
    print(f"wk{wk} {S['own_src']:9} games {len(S['games'])//2} | SIM med {sim[0]:.1f} cash {sim[1]:.1f} top5 {sim[2]:.1f} top1 {sim[3]:.1f} | REAL med {real[0]:.1f} cash {real[1]:.1f} top5 {real[2]:.1f} top1 {real[3]:.1f}")
    out.append((wk,sim,real))
json.dump(out, open('/home/claude/bt/ls/calib.json','w'))
