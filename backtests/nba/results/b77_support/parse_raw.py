"""Parse LineStar raw history into enriched tables for the v1.3 review (B77)."""
import gzip, json, os, re, pandas as pd, numpy as np
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/linestar/raw/'
rows=[]; crow=[]; orow=[]
for fn in sorted(os.listdir(R)):
    if not fn.endswith('.json.gz'): continue
    d=fn[:10]; r=json.load(gzip.open(R+fn))
    sc=json.loads(r.get('SalaryContainerJson') or '{}'); ow=r.get('Ownership') or {}
    slates=ow.get('Slates') or []
    main=[s for s in slates if s.get('SlateName')=='Main']
    ms=main[0] if main else None
    mg=set(g['GameId'] for g in ms['SlateGames']) if ms else set()
    pj={}
    if ms:
        for o in (ow.get('Projected') or {}).get(str(ms['Id']),[]): pj[o['SalaryId']]=o['Owned']
    # contests on the main slate
    best=None; du=None
    for c in ow.get('ContestResults') or []:
        C=c['Contest']
        if not ms or C['SlateId']!=ms['Id']: continue
        crow.append(dict(date=d,contest=C['ContestName'],ctype=C['ContestType'],fee=C['EntryFee'],entries=C['EntryCount'],purse=C['Purse'],tracked=C['OwnershipTracked'],cid=C['ContestId'],group=C['GroupId']))
        for o in c['OwnershipData']: orow.append((d,C['ContestId'],o['SalaryId'],o['Owned']))
    for s in sc.get('Salaries',[]):
        notes=json.loads(s.get('Notes') or '[]'); st=0
        for n in notes:
            if 'Confirmed Starter' in n['Note']: st=2
            elif 'Expected Starter' in n['Note'] and st==0: st=1
        b2b=any('2nd game of B2B' in n['Note'] and n['Note'].startswith(str(s.get('PTEAM'))) for n in notes)
        m=re.search(r'\((\d+)',s.get('GT') or ''); gt=int(m.group(1)) if m else None
        rows.append(dict(date=d,salary_id=s['Id'],player_id=s.get('PID'),name=s.get('Name'),pos=s.get('POS'),team=s.get('PTEAM'),opp=s.get('OTEAM'),
            salary=s.get('SAL'),ls_proj=s.get('PP'),agg=s.get('AggProj'),floor=s.get('Floor'),ceil=s.get('Ceil'),actual=s.get('PS'),stat=s.get('STAT'),
            starter=st,gid=s.get('GID'),gt=gt,in_main=int(s.get('GID') in mg),main_games=(ms['Games'] if ms else np.nan),
            main_start=(ms['SlateStartUtc'] if ms else None),pown=pj.get(s['Id'],np.nan),ppg=s.get('PPG'),b2b=int(b2b)))
P=pd.DataFrame(rows); C=pd.DataFrame(crow); O=pd.DataFrame(orow,columns=['date','cid','salary_id','own'])
P.to_csv('hist_players.csv',index=False); C.to_csv('hist_contests.csv',index=False); O.to_csv('hist_own.csv',index=False)
print(len(P),len(C),len(O)); print(P.groupby('date').starter.apply(lambda x:(x>0).sum()).describe())
print('agg>0 first date',P[P['agg']>0].date.min(),'share of proj rows with agg',(P[P.ls_proj>0]['agg']>0).groupby(P[P.ls_proj>0].date.str[:7]).mean().round(2).to_dict())
print(C.ctype.value_counts().to_dict()); print(C.groupby('ctype').entries.describe())
print(C[C.date>='2026-11-06'].to_string())
