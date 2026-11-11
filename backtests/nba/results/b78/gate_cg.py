"""ChatGPT round, pre-lock replays (8 dates). Every arm uses ONLY the named snapshot's projections, starter flags and injury tags.
Arms on the last pre-lock snapshot: v1.3; LS x CAL crossed with exposure 3 x none (overlap 6); four-distinct (overlap 8); final v1.4
structure (no contrarian / cheap-teammate caps). Diagnostics, labelled: final projections with the PRE-LOCK pool fixed; final pool too.
Also the same 2x2 at the EARLIER snapshot on dates with two pulls 30 minutes apart.
Scoring: exact rank and exact payout in the slate's primary contest when we hold its standings (6 dates), field-model estimate otherwise (2)."""
import pandas as pd, numpy as np, warnings, io, contextlib, pickle, sys
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy import sparse
warnings.filterwarnings('ignore'); pd.set_option('display.width',260); pd.set_option('display.max_columns',60)
with contextlib.redirect_stdout(io.StringIO()): import live_build as LB
A=pd.read_pickle('live_vs_final.pkl'); T=pd.read_pickle('live_pulls.pkl'); M=pd.read_pickle('master.pkl'); k=LB.k; C18=pickle.load(open('contests18.pkl','rb'))
R='/home/claude/luctuhuynh-source/mlb-api-mcp/backtests/nba/'; ATT='/mnt/user-data/attachments/6b87524e-2daf-575b-8b1e-b163002da830/'
PRIM={'2026-11-04':'08ad4fb1','2026-11-05':'d62a48dc','2026-11-06':'23632d04','2026-11-07':'79523267','2026-11-09':'86ee8b01','2026-11-10':'eb8ea2d9'}
G=pd.concat([pd.read_csv(R+f'nba_player_games_{s}.csv') for s in ['2025-26','2026-27']]); G=G[~G.did_not_play.astype(str).eq('True')&(G.minutes>0)].copy(); G['k']=G.athlete_display_name.map(k); G=G.sort_values('game_date')
SL=LB.SL; NEED=LB.NEED; slots=LB.slots
def solve(d,obj,extra=(),ban=(),sub5k=True):
    n=len(d); sl=[slots(p) for p in d.pos]; pairs=[(i,kk) for i in range(n) for kk,x in enumerate(SL) if x in sl[i]]
    pi=np.array([p[0] for p in pairs]); pk=np.array([p[1] for p in pairs]); nv=len(pairs); rows=[];lo=[];hi=[]
    for kk in range(8):
        r=np.zeros(n+nv); r[n:][pk==kk]=1; rows.append(r); lo.append(NEED[kk]); hi.append(NEED[kk])
    Lm=np.zeros((n,n+nv)); Lm[pi,n+np.arange(nv)]=1; Lm[np.arange(n),np.arange(n)]=-1; rows+=list(Lm); lo+=[0]*n; hi+=[0]*n
    r=np.zeros(n+nv); r[:n]=d.salary.values; rows.append(r); lo.append(0); hi.append(60000)
    for t in d.team.unique():
        a=np.zeros(n+nv); a[:n]=(d.team.values==t); rows.append(a); lo.append(0); hi.append(3)
        b=np.zeros(n+nv); b[:n]=(d.team.values==t)&(d.salary.values<5000)
        if sub5k and b.sum()>2: rows.append(b); lo.append(0); hi.append(2)
    for a,c in extra:
        v=np.zeros(n+nv); v[:n]=a; rows.append(v); lo.append(0); hi.append(c)
    ub=np.ones(n+nv)
    if len(ban): ub[list(ban)]=0
    c=np.zeros(n+nv); c[:n]=-obj; integ=np.zeros(n+nv); integ[:n]=1
    r=milp(c,constraints=LinearConstraint(sparse.csr_matrix(np.array(rows)),lo,hi),integrality=integ,bounds=Bounds(0,ub),options={'mip_rel_gap':1e-7,'time_limit':30})
    return None if r.x is None else list(np.where(r.x[:n]>0.5)[0])
def build(d,obj,games,mode,ov=None,caps=True):
    n=len(d); own=d.own.values
    if mode=='tiers': cap=np.where(own>=35,3,np.where(own>=15,2,1)); ov0=4 if games>=6 else (5 if games>=4 else 8)
    else: cap=np.full(n,3 if mode=='free' else 4); ov0=6 if games>=4 else 8
    ov=ov0 if ov is None else ov; ex0=[((own<10).astype(float),1 if games>=4 else 2)] if caps else []; built=[]; cnt=np.zeros(n,int)
    for j in range(4):
        ids=solve(d,obj,ex0+[(np.isin(np.arange(n),L).astype(float),ov) for L in built],ban=np.where(cnt>=cap)[0],sub5k=caps)
        if ids is None: break
        built.append(ids); cnt[ids]+=1
    return built
def frame(dt,pull):
    L=T[(T.date==dt)&(T.pull==pull)&(T.in_main==1)].copy(); L['kk']=L.name.map(k)
    if dt in set(A.date):
        f=A[A.date==dt][['salary_id','l5','min3','stat_fin','actual','ls_proj_fin','agg_fin','pown_fin','tip']]; L=L.merge(f,on='salary_id',how='inner')
        L=L.merge(M[M.date==dt][['salary_id','ceil']].rename(columns={'ceil':'ceil_fin'}),on='salary_id',how='left')
    else:
        f=G[G.game_date<dt].groupby('k').agg(l5=('fd_pts',lambda x:x.tail(5).mean()),min3=('minutes',lambda x:x.tail(3).mean())); L=L.merge(f,left_on='kk',right_index=True,how='left')
        L['stat_fin']=1; L['actual']=np.nan; L['ls_proj_fin']=np.nan; L['agg_fin']=np.nan; L['pown_fin']=np.nan; L['ceil_fin']=np.nan; L['tip']=np.nan
    return L.reset_index(drop=True)
rows=[]
for dt in sorted(A.date.unique())+['2026-11-10']:
    pulls=sorted(T[T.date==dt].pull.unique()); last=pulls[-1]; early=[p for p in pulls if int(last[:2])*60+int(last[2:])-(int(p[:2])*60+int(p[2:])) in (30,)]
    games=int(T[T.date==dt].main_games.iloc[0]); hasfin=dt in set(A.date)
    fdout=LB.FDOUT.get(dt,set()) if dt!='2026-11-10' else set(map(k,['Tyler Herro',"Kel'el Ware",'Tristan da Silva','Max Christie']))
    if dt in PRIM:
        c=C18[C18.file.str.startswith(PRIM[dt])].iloc[0]; pa=c.pts[::-1]; wa=c.w[::-1]; fee=c.fee; exact=True
        pct=lambda x:100*np.searchsorted(pa,x,side='left')/len(pa); pay=lambda x:float(wa[np.searchsorted(pa,x,side='right')-1]) if np.searchsorted(pa,x,side='right')>0 else 0.0
        d0=pd.read_csv(ATT+[f for f in LB.__dict__.get('_x',[])] [0]) if False else None
        cs=pd.read_csv([ATT+f for f in __import__('os').listdir(ATT) if f.startswith(PRIM[dt])][0],encoding='utf-8-sig',low_memory=False); p=cs[cs.Player.notna()].copy(); p['kk']=p.Player.str.replace(r' \(.*','',regex=True).map(k); fp=pd.to_numeric(p.set_index('kk').FPTS)
        q999=c.q999; cashline=c.cash
    else:
        mu,sd=LB.field(dt); zp=np.load('z_pool.npy'); exact=False; fee=np.nan; pct=lambda x:100*np.searchsorted(zp,(x-mu)/sd,side='left')/len(zp); pay=lambda x:np.nan; q999=mu+2.74*sd; cashline=mu+0.72*sd
    for pull in ([last]+early[:1]):
        a=frame(dt,pull)
        if not hasfin: a['actual']=a.kk.map(fp).fillna(0)
        a['l5f']=a.l5.fillna(a.ls_proj)
        pre=((a.ls_proj>0)&(a.stat!=4)&~a.kk.isin(fdout)&((a.stat==1)|(a.min3>=18))).values
        d=a[pre].reset_index(drop=True); ls=d.ls_proj.values; ag=np.where(d['agg']>0,d['agg'],ls); po=d.pown.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95); up=np.nan_to_num(np.clip(d.ceil.values-ls,0,None))
        act=d.actual.where(d.stat_fin!=4,0).fillna(0).values
        P={'ls':ls,'cal':-0.26+0.136*ls+0.856*ag,'blend':0.7*ls+0.3*d.l5f.values}
        arms=[('LS_cap3','ls','free',{}),('LS_nocap','ls','c4',{}),('CAL_cap3','cal','free',{}),('CAL_nocap','cal','c4',{})]
        if pull==last: arms=[('v1.3','blend','tiers',{})]+arms+[('CAL_nocap_ov8','cal','c4',dict(ov=8)),('CAL_nocap_nocaps','cal','c4',dict(caps=False))]
        tag='last' if pull==last else 'early'
        def rec(name,Ls,dd,ac):
            sc=[float(ac[L].sum()) for L in Ls]
            rows.append(dict(date=dt,games=games,snap=tag,pull=pull,arm=name,exact=exact,fee=fee,s=sc,pct=[pct(x) for x in sc],pay=[pay(x) for x in sc],cash=sum(x>=cashline for x in sc),gap999=max(sc)-q999,dead=sum(int((dd.stat_fin.values[L]==4).sum()) for L in Ls)))
        for name,pr,mode,kw in arms: rec(name,build(d,P[pr]+0.1*up,games,mode,**kw),d,act)
        if pull==last and hasfin:
            # diagnostic 1: FINAL projections, PRE-LOCK pool and status fixed
            lsf=np.where(d.ls_proj_fin>0,d.ls_proj_fin,0.0); agf=np.where(d.agg_fin>0,d.agg_fin,lsf); upf=np.nan_to_num(np.clip(d.ceil_fin.fillna(d.ceil).values-lsf,0,None))
            rec('DIAG finalproj+prepool CAL_nocap',build(d,-0.26+0.136*lsf+0.856*agf+0.1*upf,games,'c4'),d,act); rec('DIAG finalproj+prepool LS_nocap',build(d,lsf+0.1*upf,games,'c4'),d,act)
            # diagnostic 2: FINAL projections and FINAL pool (what B77 sees)
            fin=((a.ls_proj_fin>0)&(a.stat_fin!=4)&((a.stat_fin==1)|(a.min3>=18))).values; e=a[fin].reset_index(drop=True); l2=e.ls_proj_fin.values; a2=np.where(e.agg_fin>0,e.agg_fin,l2); po=e.pown_fin.fillna(0); e['own']=(po*900/po.sum()).clip(upper=95); u2=np.nan_to_num(np.clip(e.ceil_fin.fillna(e.ceil).values-l2,0,None)); ac2=e.actual.fillna(0).values
            rec('DIAG final all CAL_nocap',build(e,-0.26+0.136*l2+0.856*a2+0.1*u2,games,'c4'),e,ac2); rec('DIAG final all LS_nocap',build(e,l2+0.1*u2,games,'c4'),e,ac2)
    print(dt,'done',flush=True)
X=pd.DataFrame(rows); X['fp']=X.s.map(np.mean); X['mpct']=X.pct.map(np.mean); X['won']=X['pay'].map(np.sum); X['fees']=4*X.fee; pickle.dump(X,open('gate_cg.pkl','wb'))
def tab(sub,arms,lab):
    print(f'\n{lab}')
    for arm in arms:
        g=sub[sub.arm==arm]; ex=g[g.exact]
        print(f'  {arm:34} slates {len(g)} | FP {g.fp.mean():6.1f} | percentile {g.mpct.mean():5.1f} (exact-standings dates {ex.mpct.mean():5.1f}, n={len(ex)}) | cashes {int(g.cash.sum())}/{4*len(g)} | exact payouts: ${ex.won.sum():.0f} on ${ex.fees.sum():.0f} fees = {ex.won.sum()/ex.fees.sum():.2f} per $1 | dead {int(g.dead.sum())} | best score vs top-0.1% line {g.gap999.mean():+.0f}')
def pair(sub,a,b,lab):
    x=sub[sub.arm==a].set_index('date'); y=sub[sub.arm==b].set_index('date'); i=x.index.intersection(y.index); d=x.fp[i]-y.fp[i]; q=x.mpct[i]-y.mpct[i]
    print(f'  {lab}: {d.mean():+.1f} FP (se {d.std()/np.sqrt(len(d)):.1f}), percentile {q.mean():+.1f} (se {q.std()/np.sqrt(len(q)):.1f}), better on {int((d>0).sum())} of {len(d)} dates')
Lx=X[X.snap=='last']
tab(Lx,['v1.3','LS_cap3','LS_nocap','CAL_cap3','CAL_nocap','CAL_nocap_ov8','CAL_nocap_nocaps'],'LAST PRE-LOCK SNAPSHOT (8 dates)')
print('  2x2 effects:'); pair(Lx,'CAL_cap3','LS_cap3','projection, cap 3'); pair(Lx,'CAL_nocap','LS_nocap','projection, no cap'); pair(Lx,'LS_nocap','LS_cap3','exposure, LS'); pair(Lx,'CAL_nocap','CAL_cap3','exposure, CAL'); pair(Lx,'CAL_nocap_ov8','CAL_nocap','overlap 8 vs 6 (no cap)'); pair(Lx,'CAL_nocap_nocaps','CAL_nocap','drop contrarian + cheap-teammate caps'); pair(Lx,'CAL_nocap_nocaps','v1.3','final v1.4 structure vs v1.3')
F=Lx[Lx.date.isin(Lx[Lx.arm=='DIAG final all CAL_nocap'].date)]
tab(F,['CAL_nocap','DIAG finalproj+prepool CAL_nocap','DIAG final all CAL_nocap','LS_nocap','DIAG finalproj+prepool LS_nocap','DIAG final all LS_nocap'],'LOOK-AHEAD DECOMPOSITION (7 dates with a final record; DIAG rows are not executable)')
pair(F,'DIAG finalproj+prepool CAL_nocap','CAL_nocap','projection revisions after the snapshot (pool fixed), CAL'); pair(F,'DIAG final all CAL_nocap','DIAG finalproj+prepool CAL_nocap','eligibility/status changes after the snapshot, CAL'); pair(F,'DIAG finalproj+prepool LS_nocap','LS_nocap','projection revisions, LS'); pair(F,'DIAG final all LS_nocap','DIAG finalproj+prepool LS_nocap','eligibility changes, LS')
E=X[X.date.isin(X[X.snap=='early'].date)&X.arm.isin(['LS_cap3','LS_nocap','CAL_cap3','CAL_nocap'])]
for sn in ('early','last'): tab(E[E.snap==sn],['LS_cap3','LS_nocap','CAL_cap3','CAL_nocap'],f'TWO-SNAPSHOT DATES ({E.date.nunique()} dates), snapshot = {sn} ({"30 min before the last" if sn=="early" else "last pre-lock"})')
for arm in ['LS_cap3','LS_nocap','CAL_cap3','CAL_nocap']:
    x=E[(E.snap=='last')&(E.arm==arm)].set_index('date'); y=E[(E.snap=='early')&(E.arm==arm)].set_index('date'); d=x.fp-y.fp; print(f'  fresher snapshot, {arm}: {d.mean():+.1f} FP (se {d.std()/np.sqrt(len(d)):.1f}), better on {int((d>0).sum())}, worse on {int((d<0).sum())} of {len(d)}')
print('\nPER DATE (last snapshot): mean FP / mean percentile / $ won');
for arm in ['v1.3','LS_nocap','CAL_cap3','CAL_nocap','CAL_nocap_nocaps']:
    g=Lx[Lx.arm==arm]; print(f'  {arm:18} '+' | '.join(f'{r.date[5:]} {r.fp:.0f}/{r.mpct:.0f}/{"$%.0f"%r.won if r.exact else "est"}' for _,r in g.iterrows()))
