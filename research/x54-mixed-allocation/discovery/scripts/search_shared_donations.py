"""One reversible donation shared by several target reads of a stable holder.

For every target t in a contiguous read batch, replace a_t*A + c_t*H by
c_t*(H+q*A), requiring a_t/c_t=q for the whole batch. Restore H once.
Exact local frame pricing nominates words; native/global admission is separate.
"""
import os,sys,json,gzip,time,itertools,multiprocessing as mp
from pathlib import Path
from fractions import Fraction as Q
W=Path(__file__).resolve().parent;ROOT=Path('/Users/thomasdifiore/integer-mult-next-construction')
os.environ['IMB_ROOT']=str(ROOT);sys.path.insert(0,str(W/'research/exact-frame-toolkit'))
import harness as C
from fusion import index,dyadic,any_in
BASE=W/'x54/demote3.json.gz';OUT=W/'shared-donations'
def candidates(w):
    I=index(w);B=w['B'];reads={};holder_reads={}
    for j,e in enumerate(B):
        if e[0]=='add':
            holder_reads.setdefault(e[2],[]).append(j)
            if 112<=e[1]<224:reads.setdefault(e[1],[]).append((j,e[2],Q(e[3],e[4])))
    seen=set();result=[]
    for holder,rr in holder_reads.items():
        if 112<=holder<224:continue
        for start in range(len(rr)):
            for length in range(2,len(rr)-start+1):
                batch=rr[start:start+length];first,last=batch[0],batch[-1]
                if any(not 112<=B[j][1]<224 for j in batch):break
                if any_in(I['W'][holder],first,last+1):break
                if len({B[j][1]for j in batch})!=length:continue
                t0=B[first][1];c0=Q(B[first][3],B[first][4])
                for aj,source,a0 in reads[t0]:
                    if source==holder or 112<=source<224:continue
                    q=a0/c0
                    if not dyadic(q):continue
                    options=[]
                    for j in batch:
                        t=B[j][1];c=Q(B[j][3],B[j][4])
                        opts=[i for i,s,a in reads[t]if s==source and a/c==q and not any_in(I['RD'][t]+I['SC'][t],min(i,j),max(i,j)+1)]
                        if not opts:break
                        options.append(opts)
                    if len(options)!=length:continue
                    for dels in itertools.product(*options):
                        if len(set(dels))!=length:continue
                        lo=min(first,*dels);hi=max(last,*dels)
                        if any_in(I['W'][source],lo,hi+1):continue
                        key=(holder,source,str(q),first,last,tuple(dels))
                        if key in seen:continue
                        seen.add(key)
                        ed=dict(delete=list(dels),insert=[[first,['add',holder,source,q.numerator,q.denominator,[]]],
                            [last+1,['add',holder,source,-q.numerator,q.denominator,[]]]],tail=[],prepend=[])
                        result.append(dict(holder=holder,source=source,q=str(q),reads=batch,ed=ed))
    return result
def init():
    global P
    P=C.Pricer(str(BASE))
def price(item):
    n,c=item;r=P.price(c['ed'],want_word=True,timeout=20);word=r.pop('word',None)
    if r.get('status')=='ok'and r.get('delta',0)<0:
        path=OUT/(f'candidate-{n}.json.gz');path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));r['word']=path.name
    return dict(index=n,**c,**r)
if __name__=='__main__':
    OUT.mkdir(exist_ok=True);cs=candidates(C.load(str(BASE)));print('CANDIDATES',len(cs),flush=True)
    (OUT/'CANDIDATES.json').write_text(json.dumps(cs,indent=2)+'\n');results=[];t=time.monotonic()
    with mp.get_context('fork').Pool(2,initializer=init,maxtasksperchild=100)as pool:
        for r in pool.imap_unordered(price,enumerate(cs),chunksize=1):
            results.append(r)
            if r.get('delta',0)<0:print('GAIN',json.dumps({k:v for k,v in r.items()if k!='ed'}),flush=True)
            if len(results)%50==0:print('PROGRESS',len(results),'of',len(cs),'seconds',time.monotonic()-t,flush=True)
    (OUT/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n');print('DONE',len(results),'gains',sum(r.get('status')=='ok'and r.get('delta',0)<0 for r in results),flush=True)
