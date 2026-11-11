"""Parse every live LineStar pull (pre-lock snapshots) into one table."""
import gzip, json, os, re, pandas as pd, numpy as np
L='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/live/'
rows=[]
for fn in sorted(os.listdir(L)):
    if not fn.endswith('_raw.json.gz'): continue
    d,tm=fn[:10],fn[11:15]
    try: r=json.load(gzip.open(L+fn))
    except Exception as e: print('bad',fn,e); continue
    sc=json.loads(r.get('SalaryContainerJson') or '{}'); ow=r.get('Ownership') or {}
    ms=[s for s in (ow.get('Slates') or []) if s.get('SlateName')=='Main']; ms=ms[0] if ms else None
    mg=set(g['GameId'] for g in ms['SlateGames']) if ms else set()
    pj={o['SalaryId']:o['Owned'] for o in (ow.get('Projected') or {}).get(str(ms['Id']),[])} if ms else {}
    for s in sc.get('Salaries',[]):
        notes=json.loads(s.get('Notes') or '[]'); st=0
        for n in notes:
            if 'Confirmed Starter' in n['Note']: st=2
            elif 'Expected Starter' in n['Note'] and st==0: st=1
        m=re.search(r'\((\d+)',s.get('GT') or '')
        rows.append(dict(date=d,pull=tm,salary_id=s['Id'],player_id=s.get('PID'),name=s.get('Name'),pos=s.get('POS'),team=s.get('PTEAM'),salary=s.get('SAL'),
            ls_proj=s.get('PP'),agg=s.get('AggProj'),ceil=s.get('Ceil'),stat=s.get('STAT'),starter=st,gid=s.get('GID'),gt=int(m.group(1)) if m else None,
            in_main=int(s.get('GID') in mg),pown=pj.get(s['Id'],np.nan),main_start=(ms['SlateStartUtc'] if ms else None),main_games=(ms['Games'] if ms else np.nan),trunc=sc.get('IsTruncated')))
T=pd.DataFrame(rows); T.to_pickle('live_pulls.pkl')
print(T.groupby(['date','pull']).agg(n=('name','size'),proj=('ls_proj',lambda x:(x>0).sum()),main=('in_main','sum'),agg=('agg',lambda x:(x>0).sum()),conf=('starter',lambda x:(x==2).sum()),exp=('starter',lambda x:(x==1).sum()),stat1=('stat',lambda x:(x==1).sum()),own=('pown',lambda x:x.notna().sum()),games=('main_games','first'),trunc=('trunc','first')).to_string())
