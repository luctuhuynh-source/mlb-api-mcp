"""Fill the FanDuel entries-upload template from lineups_<mode>.csv; also write an xlsx with a readable tab."""
import pandas as pd, csv, sys
WK='/home/claude/wk9'; MODE = sys.argv[1] if len(sys.argv)>1 else 'v17'
TPL='/mnt/user-data/attachments/d96743da-8be9-5bb5-9072-0f05208cdafb/9e8c48a8-FanDuel-NFL-2026-11-08-136184-entries-upload-template-1.csv'
L = pd.read_csv(f'{WK}/lineups_{MODE}.csv')
SLOTS=['QB','RB','RB','WR','WR','WR','TE','FLEX','DEF']
rows = list(csv.reader(open(TPL, newline='')))
hdr = rows[0][:13]
entries = [r for r in rows[1:] if r and r[0].strip()]
n = L['lineup'].nunique()
out=[hdr]
for k,e in enumerate(entries):
    lu = L[L['lineup']==(k % n)+1].copy()
    ids = []
    for s in SLOTS:
        r = lu[lu['slot']==s].iloc[0]; ids.append(f"{r['id']}:{r['name']}"); lu = lu.drop(r.name)
    out.append(e[:4]+ids)
fn=f'{WK}/FanDuel-NFL-2026-11-08-upload-{MODE}.csv'
with open(fn,'w',newline='') as f: csv.writer(f).writerows(out)
# xlsx
with pd.ExcelWriter(fn.replace('.csv','.xlsx')) as xw:
    pd.DataFrame(out[1:], columns=out[0]).to_excel(xw, sheet_name='upload', index=False)
    L[['lineup','slot','name','pos','team','opp','salary','proj','fp_props','ls_proj','proj_sal','ls_own']].round(1).to_excel(xw, sheet_name='readable', index=False)
print(fn, len(out)-1, 'entries; contests:', sorted(set(e[2] for e in entries)))
