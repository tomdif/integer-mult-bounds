"""Screen commuting moves that change event order on a shared register."""
import os,sys,json,gzip,copy,time,signal,multiprocessing as mp
from pathlib import Path
W=Path(__file__).resolve().parent;ROOT=Path('/Users/thomasdifiore/integer-mult-next-construction')
os.environ['IMB_ROOT']=str(ROOT)
sys.path.insert(0,str(W/'research/exact-frame-toolkit'))
import harness as H,frames as F
from word import inline
from writeback import write_back
BASE=W/'x54/demote3.json.gz';OUT=W/'retiming'
def init():
    global p,caps
    p=H.Pricer(str(BASE));caps=p.caps
def trial(case):
    sec,i,j=case;w=copy.deepcopy(p.base);w[sec]=F.moved(w[sec],i,j)
    crossed=p.base[sec][min(i,j):max(i,j)+1]
    assert all(F.commute(p.base[sec][i],g)for g in crossed)
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(20)
    try:
        g=F.Graph(inline(w,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
        r=F.optimal_frames(inline(w,True),p.costs,check_literal=False,graph=g)
        result=dict(case=case,status='certified'if r['certified']else'uncertified',delta=r['cost']-p.base_cost,profile=r['profile'])
        if r['certified'] and result['delta']<0:
            word=write_back(w,g,r['assign']);path=OUT/(f'{sec}-{i}-{j}.json.gz')
            path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));result['word']=path.name
        return result
    except F.Infeasible:return dict(case=case,status='infeasible')
    except H.Timeout:return dict(case=case,status='timeout')
    finally:signal.alarm(0)
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);w=H.load(str(BASE));cases=set()
    for sec in ['A','B']:
        gates=w[sec]
        for i,e in enumerate(gates):
            lo,hi=F.move_window(gates,i);registers=set(F.regs_of(e))
            for j in range(lo,hi+1):
                if j!=i and registers.intersection(F.regs_of(gates[j])):cases.add((sec,i,j))
    cases=sorted(cases);print('CASES',len(cases),flush=True);res=[];t=time.monotonic()
    with mp.get_context('fork').Pool(2,initializer=init,maxtasksperchild=100)as pool:
        for r in pool.imap_unordered(trial,cases,chunksize=1):
            res.append(r)
            if r.get('delta',0)<0:print('GAIN',json.dumps(r),flush=True)
            if len(res)%100==0:print('PROGRESS',len(res),'of',len(cases),'seconds',time.monotonic()-t,flush=True)
            if len(res)%100==0:(OUT/'RESULTS.json').write_text(json.dumps(res,indent=2)+'\n')
    (OUT/'RESULTS.json').write_text(json.dumps(res,indent=2)+'\n');print('DONE',len(res),'gains',sum(r.get('delta',0)<0 for r in res),flush=True)
