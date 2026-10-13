"""Screen one-helper entrance demotions against one existing idle rank-one axis.

Exact-frame optimization from PR1186. A positive result is a nomination only;
physical helper relabeling, all-column/native and global admission are separate.
"""
import os,sys,json,gzip,copy,time,signal,multiprocessing as mp
from pathlib import Path
from collections import Counter
W=Path(__file__).resolve().parent
os.environ['IMB_ROOT']='/Users/thomasdifiore/integer-mult-next-construction'
sys.path.insert(0,str(W/'research/exact-frame-toolkit'))
import harness as H,frames as F
from word import inline
from model import cone_caps
from writeback import write_back

def spaces(E):
    def lift(v):
        x=0
        for i,e in enumerate(E):
            if v>>i&1:x^=e
        return x
    return sorted({tuple(F.basis(tuple(lift(v) for v in range(32) if (v&a).bit_count()%2==0))) for a in range(1,32)})

def init():
    global bases,costs,oldcost
    bases={p:H.load(str(W/'x54'/f'{p}.json.gz')) for p in ('demote3','demote4')}
    costs=F.Costs(H.DEFAULT_B)
    oldcost={p:costs.profile_cost({int(k):v for k,v in w['report']['local_profile'].items()}) for p,w in bases.items()}

def run(case):
    pid,h,E=case;w=copy.deepcopy(bases[pid]);w['start_extra'][str(h)]=list(E)
    t=time.monotonic();out=dict(provider=pid,helper=h,entrance=E)
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(30)
    try:
        caps,_=cone_caps(w);g=F.Graph(inline(w,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
        r=F.optimal_frames(inline(w,True),costs,check_literal=False,graph=g)
        z=write_back(w,g,r['assign']);profile={int(k):v for k,v in z['report']['local_profile'].items()}
        delta=costs.profile_cost(profile)-oldcost[pid]-costs.c[1]
        out.update(status='certified' if r['certified'] else 'uncertified',delta_with_one_idle=delta,profile=profile)
        if r['certified'] and delta<0:
            ident='-'.join(map(str,E));path=W/'single-demotions'/f'{pid}-{h}-{ident}.json.gz'
            path.write_bytes(gzip.compress(json.dumps(z,sort_keys=True,separators=(',',':')).encode(),mtime=0));out['word']=str(path)
    except (F.Infeasible,ValueError,H.Timeout) as e:out.update(status=type(e).__name__,reason=str(e)[:200])
    finally:signal.alarm(0)
    out['seconds']=round(time.monotonic()-t,3);return out

if __name__=='__main__':
    out=W/'single-demotions';out.mkdir(exist_ok=True)
    cases=[]
    for pid in ('demote3','demote4'):
        w=H.load(str(W/'x54'/f'{pid}.json.gz'))
        helpers=[h for h in (627,629,630,631,619,621,622,623) if len(w['start_extra'].get(str(h),[]))==5]
        for h in helpers:
            for E in spaces(w['start_extra'][str(h)]):cases.append((pid,h,E))
    results=json.loads((out/'RESULTS.json').read_text()) if (out/'RESULTS.json').exists() else []
    done={(r['provider'],r['helper'],tuple(r['entrance'])) for r in results}
    cases=[c for c in cases if (c[0],c[1],tuple(c[2])) not in done]
    print('REMAINING',len(cases),'retained',len(results),flush=True)
    with mp.get_context('fork').Pool(3,initializer=init,maxtasksperchild=40) as pool:
        for r in pool.imap_unordered(run,cases,chunksize=1):
            results.append(r)
            if r.get('delta_with_one_idle',0)<0:print('GAIN',r,flush=True)
            if len(results)%20==0:print('PROGRESS',len(results),Counter(x['status'] for x in results),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),'gains',sum(r.get('delta_with_one_idle',0)<0 for r in results),flush=True)
