"""Late-swap rules priced on the real pre-lock lineups (7 live slates), one tip window at a time, KEEPING the portfolio rules
(overlap <=6 between our lineups, exposure cap) during every re-optimisation, so gains come from information and not from dropping
diversification. At window w we know the FINAL view of games tipping at w and still only the PRE-LOCK view of later games.
Rule = (k max new players per lineup per window, t min projection gain, trigger required, max windows acted on, use_new_info)."""
import pandas as pd, numpy as np, warnings, io, contextlib, sys
warnings.filterwarnings('ignore'); pd.set_option('display.width',250); pd.set_option('display.max_columns',60)
with contextlib.redirect_stdout(io.StringIO()): import live_build as LB
A=pd.read_pickle('live_vs_final.pkl'); T=pd.read_pickle('live_pulls.pkl'); k=LB.k
AGE={'2026-10-31':45,'2026-11-02':45,'2026-11-04':15,'2026-11-05':135,'2026-11-06':15,'2026-11-07':105,'2026-11-09':15}
def buildx(d,obj,games,mode):
    n=len(d); own=d.own.values; cap=np.full(n,3 if mode=='free' else 4); ov=6 if games>=4 else 8
    contra=((own<10).astype(float),1 if games>=4 else 2); built=[]; cnt=np.zeros(n,int)
    for j in range(4):
        ids=LB.solve(d,obj,[contra]+[(np.isin(np.arange(n),L).astype(float),ov) for L in built],ban=np.where(cnt>=cap)[0])
        if ids is None: break
        built.append(ids); cnt[ids]+=1
    return built
RULES={'frozen':None,'out-only (v1.3 17a)':(0,0,True,9,True),'trig k2 t5.0 (Gemini)':(2,5.0,True,9,True),'trig k1 t3.5 (v1.3 17b)':(1,3.5,True,9,True),'any k2 t3.5':(2,3.5,False,9,True),'any k9 t3.5':(9,3.5,False,9,True),
       'full':(9,0.0,False,9,True),'full, first 2 windows':(9,0.0,False,2,True),'CONTROL full, no new info':(9,0.0,False,9,False)}
det=[]
for dt in sorted(A.date.unique()):
    a=A[A.date==dt].copy().reset_index(drop=True); a['kk']=a.name_live.map(k); fdout=LB.FDOUT.get(dt,set()); games=int(T[T.date==dt].main_games.iloc[0]); N=len(a); idx=np.arange(N)
    lsl=a.ls_proj_live.values; agl=np.where(a.agg_live>0,a.agg_live,lsl); call=-0.26+0.136*lsl+0.856*agl
    lsf=a.ls_proj_fin.values; agf=np.where(a.agg_fin>0,a.agg_fin,lsf); calf=-0.26+0.136*lsf+0.856*agf
    el_pre=((a.ls_proj_live>0)&(a.stat_live!=4)&~a.kk.isin(fdout)&((a.stat_live==1)|(a.min3>=18))).values
    el_fin=((a.ls_proj_fin>0)&(a.stat_fin!=4)&((a.stat_fin==1)|(a.min3>=18))).values
    act=a.actual.where(a.stat_fin!=4,0).fillna(0).values; tip=a.tip.values; out=(a.stat_fin==4).values
    newst=((a.stat_live!=1)&(a.stat_fin==1)).values; newout=((a.stat_live==1)&(a.stat_fin==4)).values
    d=a[el_pre].reset_index(); po=d.pown_live.fillna(0); d['own']=(po*900/po.sum()).clip(upper=95); up=(d.ceil-d.ls_proj_live).clip(lower=0).fillna(0).values
    wins=sorted(set(tip[tip>=30])); ov=6 if games>=4 else 8
    for mode in ('free','c4'):
        cap=3 if mode=='free' else 4
        Ls=[list(d['index'].values[L]) for L in buildx(d,call[el_pre]+0.1*up,games,mode)]
        for rn,rp in RULES.items():
            cur=[list(L) for L in Ls]; nsw=[0]*4; nact=[0]*4
            if rp is not None:
                kmax,thr,needtrig,maxw,info=rp
                for wi,w in enumerate(wins):
                    if info: proj=np.where(tip==w,np.where(out,0,calf),call); cand=np.where(tip==w,el_fin,el_pre)&(tip>=w)
                    else: proj=call.copy(); cand=el_pre&(tip>=w)
                    for j in range(4):
                        oth=[cur[m] for m in range(4) if m!=j]; cnt=np.zeros(N,int)
                        for L in oth: cnt[L]+=1
                        ovc=[(np.isin(idx,L).astype(float),ov) for L in oth]; expo=(cnt>=cap)&~np.isin(idx,cur[j])
                        locked=[i for i in cur[j] if tip[i]<w]; dead=[i for i in cur[j] if tip[i]==w and out[i]] if info else []
                        if dead:
                            keep=[i for i in cur[j] if i not in dead]; ban=np.where(~(cand|np.isin(idx,keep))|expo)[0]
                            r=LB.solve(a,proj,extra=ovc,ban=ban,force=keep)
                            if r is None:
                                v=(~np.isin(idx,cur[j])).astype(float); r=LB.solve(a,proj,extra=ovc+[(v,len(dead)+1)],ban=ban,force=locked)
                            if r is not None: cur[j]=list(r)
                        trig=bool(((newst|newout)&(tip==w)&~np.isin(idx,cur[j])).any())
                        if kmax>0 and wi<maxw and (trig or not needtrig):
                            ban=np.where(~(cand|np.isin(idx,cur[j]))|expo)[0]; v=(~np.isin(idx,cur[j])).astype(float)
                            r=LB.solve(a,proj,extra=ovc+[(v,kmax)],ban=ban,force=[i for i in cur[j] if tip[i]<w])
                            if r is not None and proj[r].sum()-proj[cur[j]].sum()>=max(thr,0.05):
                                nsw[j]+=len(set(r)-set(cur[j])); nact[j]+=1; cur[j]=list(r)
            for j in range(4): det.append(dict(date=dt,age=AGE[dt],mode=mode,lu=j+1,rule=rn,score=float(act[cur[j]].sum()),swaps=nsw[j],acts=nact[j]))
    print(dt,'done',flush=True)
D=pd.DataFrame(det); D.to_csv('swap_q7c_detail.csv',index=False)
for mode in ('free','c4'):
    X=D[D['mode']==mode]; P=X.pivot_table(index=['date','lu'],columns='rule',values='score')[list(RULES)]; S=P.groupby('date').mean()
    print(f'\n=== pre-lock CAL lineups, structure {mode}: {len(P)} lineups, {len(S)} slates (SE across slates) ===')
    for r in RULES:
        g=(S[r]-S['frozen']); x=X[X.rule==r]
        fresh=g[[q for q in g.index if AGE[q]<=15]].mean(); stale=g[[q for q in g.index if AGE[q]>15]].mean()
        print(f'  {r:27} mean {P[r].mean():6.1f} | vs frozen {g.mean():+5.1f} (slate se {g.std()/np.sqrt(len(g)):.1f}; better {int((g>0.05).sum())}, worse {int((g<-0.05).sum())}) | fresh-pull slates {fresh:+5.1f}, stale-pull {stale:+5.1f} | players swapped {int(x.swaps.sum())}, re-uploads {int(x.acts.sum())} in {int((x.acts>0).sum())} lineups')
    print(S.round(1).to_string())
