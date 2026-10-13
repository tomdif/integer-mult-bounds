"""Exact dyadic helper conjugations, followed by commuting scalar simplification.

This is a finite search, not a new construction claim. New scalar words must
still pass the retained geometric model and independent endpoint audit.
"""
import argparse, collections, copy, gzip, hashlib, itertools, json, os, signal, sys, time
from fractions import Fraction as Q
from pathlib import Path
from functools import lru_cache

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[1]
HERE = Path(os.environ.get('BASIS_WORK', '.')).resolve()
OLD = NEW = ROOT
os.environ.setdefault('IMB_ROOT', str(ROOT))
sys.path.insert(0, str(PACKAGE / 'vendor/pr1186'))
FULL = [256,128,64,32,16,8,4,2,1]

def load(p): return json.loads(gzip.decompress(Path(p).read_bytes()))
def canon(w): return json.dumps(w, sort_keys=True, separators=(',', ':')).encode()
def save(p, w): Path(p).write_bytes(gzip.compress(canon(w), mtime=0))
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]
@lru_cache(None)
def fraction(a,b): return Q(a,b)
def coef(e): return fraction(e[3], e[4]) if e[0] == 'add' else fraction(e[2],e[3])
def add(t,s,q):
    assert t != s
    return ['add',t,s,q.numerator,q.denominator,[]]

def conjugate_gate(e, h, d, a):
    """Chronological factorization of S G S^-1; S = I + a E[d,h]."""
    t=e[1]
    if e[0]=='add' and t!=h and e[2]!=d: return [e]
    if e[0]=='scale' and t not in (h,d): return [e]
    q=coef(e)
    if not a: return [e[:-1]+[[]]]
    if e[0]=='scale':
        if t==h: return [add(d,h,a*(q-1)),e[:-1]+[[]]]
        if t==d: return [e[:-1]+[[]],add(d,h,a*(1-q))]
        return [e[:-1]+[[]]]
    s=e[2]
    if t==h and s==d:
        return [add(d,h,-a),add(h,d,q),add(d,h,a)]
    out=[e[:-1]+[[]]]
    if t==h: out.append(add(d,s,a*q))
    if s==d: out.append(add(t,h,-a*q))
    return out

def simplify(seq):
    """Combine equal ADDs only across gates proven to commute with them.

    Last-access positions can be stale after cancellation. This is conservative:
    it can miss a simplification but cannot cross a noncommuting instruction.
    Repeat to expose cancellations hidden by such stale positions.
    """
    old=None
    while old != len(seq):
        old=len(seq); out=[]; previous={}; lastwrite={}; lastread={}
        for e in seq:
            q=coef(e); t=e[1]
            if e[0]=='scale':
                if q==1: continue
                i=len(out); out.append(e); lastwrite[t]=lastread[t]=i
                continue
            if not q: continue
            s=e[2]; key=(t,s); prev=previous.get(key,-1)
            obstruction=max(lastwrite.get(s,-1),lastread.get(t,-1))
            if prev>=0 and out[prev] is not None and obstruction<=prev:
                q+=coef(out[prev]); out[prev]=add(t,s,q) if q else None
                if not q: previous.pop(key,None)
            else:
                i=len(out); out.append(e); previous[key]=i
                lastwrite[t]=i; lastread[s]=i
        seq=[e for e in out if e is not None]
    return seq

def transform(w,h,d,a,quick=False):
    assert h>=224 and d>=224 and h!=d
    assert all(h not in regs(e) and d not in regs(e) for e in w['A']+w['cut'])
    conv=lambda seq: simplify([f for e in seq for f in conjugate_gate(e,h,d,a)])
    out=dict(w); out['B']=conv(w['B'])
    early={i for i,U in w['early_cleanup']}
    tail=conv([w['cleanup'][i] for i,U in w['early_cleanup']])
    if quick:
        out['early_cleanup']=tail
        return out
    out['precondition']=conv(w['precondition'])
    rest=conv([e for i,e in enumerate(w['cleanup']) if i not in early])
    out['cleanup']=[e[:-1]+[FULL.copy()] for e in tail+rest]
    out['early_cleanup']=[[i,[]] for i in range(len(tail))]
    return out

def groups(w):
    import frames as F
    touched={r for e in w['A']+w['cut'] for r in regs(e)}
    groups=collections.defaultdict(list)
    for r in range(224,224+w['report']['R']):
        if r in touched: continue
        key=(F.basis(tuple(w['start_extra'].get(str(r),[]))), F.basis(tuple(w['helper_final'].get(str(r),FULL))))
        groups[key].append(r)
    return [rs for rs in groups.values() if len(rs)>1]

def apply(seq,n):
    rows=[{i:Q(1)} for i in range(n)]
    for e in seq:
        t=e[1];q=coef(e)
        if e[0]=='scale': rows[t]={k:v*q for k,v in rows[t].items() if v*q}
        else:
            for k,v in list(rows[e[2]].items()):
                z=rows[t].get(k,0)+q*v
                if z: rows[t][k]=z
                else: rows[t].pop(k,None)
    return rows

def controls():
    # Exhaust every ADD/SCALE register case and chosen coefficient. Also test
    # simplification against an independently evaluated exact rational matrix.
    import random
    rng=random.Random(20261013); count=0
    coeff=[Q(-4),Q(-2),Q(-1),Q(-1,2),Q(-1,4),Q(1,4),Q(1,2),Q(1),Q(2),Q(4)]
    gates=[add(t,s,q) for t in range(4) for s in range(4) if t!=s for q in coeff]
    gates += [['scale',t,q.numerator,q.denominator,[]] for t in range(4) for q in coeff]
    for a in coeff:
        for e in gates:
            expected=apply([add(1,0,-a),e,add(1,0,a)],4)
            assert expected==apply(conjugate_gate(e,0,1,a),4),(e,a)
            count+=1
    words=0
    for j in range(100):
        seq=[copy.deepcopy(rng.choice(gates)) for _ in range(150)]
        # Add cancellations separated by genuinely commuting operations.
        seq+= [add(2,0,Q(3)),add(2,1,Q(2)),add(2,0,Q(-3))]
        assert apply(seq,4)==apply(simplify(seq),4)
        words+=1
    bad=conjugate_gate(add(0,1,Q(2)),0,1,Q(1));bad[0][3]*=-1
    assert apply(bad,4)!=apply([add(1,0,Q(-1)),add(0,1,Q(2)),add(1,0,Q(1))],4)
    return dict(gate_conjugations=count,random_word_simplifications=words,negative_controls=1)

class Limit(Exception): pass
def alarm(*_): raise Limit()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['census','price']);ap.add_argument('--limit',type=int,default=200);ap.add_argument('--offset',type=int,default=0);ap.add_argument('--input');a=ap.parse_args()
    import frames as F
    from word import inline
    from model import cone_caps
    from writeback import write_back, audit
    w=load(a.input or PACKAGE/'inputs/BASE.json.gz')
    if a.mode=='census':
        ctl=controls(); (HERE/'CONTROLS.json').write_text(json.dumps(ctl,indent=2)+'\n'); print(ctl,flush=True)
        gs=groups(w); candidates=[]; coefficients=[Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2)]
        before=len(w['B'])+len(w['early_cleanup']); n=0
        for group in gs:
            for h,d in itertools.permutations(group,2):
                for x in coefficients:
                    v=transform(w,h,d,x,quick=True)
                    bdelta=len(v['B'])-len(w['B']);tdelta=len(v['early_cleanup'])-len(w['early_cleanup'])
                    candidates.append(dict(h=h,d=d,a=str(x),delta=bdelta+tdelta,B_delta=bdelta,tail_delta=tdelta))
                    n+=1
            print('group',len(group),'candidates',n,flush=True)
        candidates.sort(key=lambda c:(c['delta'],c['B_delta'],c['h'],c['d'],Q(c['a'])))
        out=dict(input_sha256=hashlib.sha256(canon(w)).hexdigest(),groups=gs,pairs=sum(len(g)*(len(g)-1)//2 for g in gs),candidates=candidates)
        (HERE/'CENSUS.json').write_text(json.dumps(out,indent=2)+'\n')
        print('CENSUS',len(candidates),'best',candidates[:15],flush=True)
        return
    from harness import DEFAULT_B
    c=F.Costs(DEFAULT_B); caps,comp=cone_caps(w)
    g=F.Graph(inline(w,True),check_literal=True,tail_mutable=True,caps=caps,cut_equality=True)
    base=F.optimal_frames(inline(w,True),c,graph=g)
    print('BASE',base['cost'],base['certified'],dict(base['profile']),flush=True)
    cs=json.loads((HERE/'CENSUS.json').read_text())['candidates'][a.offset:a.offset+a.limit]
    fout=(HERE/f'PRICE-{a.offset}-{a.limit}.jsonl').open('w')
    signal.signal(signal.SIGALRM,alarm)
    for i,r0 in enumerate(cs,a.offset):
        r=dict(r0,index=i);v=transform(w,r['h'],r['d'],Q(r['a']));t=time.monotonic()
        signal.alarm(45)
        try:
            # Cheap necessary geometric screen before the exact scalar cones.
            g=F.Graph(inline(v,True),check_literal=False,tail_mutable=True,cut_equality=True)
            cap,comp=cone_caps(v)
            residual=set(map(int,v['start_extra']))|set(map(int,v['helper_final']))
            if any(e[2] in residual for e in comp):
                r['status']='residual-compensation'
            else:
                g=F.Graph(inline(v,True),check_literal=False,tail_mutable=True,caps=cap,cut_equality=True)
                z=F.optimal_frames(inline(v,True),c,check_literal=False,graph=g)
                r.update(status='priced',certified=z['certified'],cost_delta=z['cost']-base['cost'],profile=dict(z['profile']))
                if z['cost']<=base['cost']:
                    vv=write_back(v,g,z['assign']);p=HERE/f"candidate-{i}.json.gz";save(p,vv)
                    signal.alarm(0)
                    ok,receipt,sha=audit(vv);r.update(audit_ok=ok,audit=receipt,sha256=sha,word=str(p))
        except F.Infeasible as e:r.update(status='frame-infeasible',why=str(e))
        except Limit:r.update(status='timeout')
        except Exception as e:r.update(status='error',why=repr(e))
        finally:signal.alarm(0)
        r['seconds']=time.monotonic()-t;fout.write(json.dumps(r,sort_keys=True)+'\n');fout.flush()
        print(i,r['h'],r['d'],r['a'],r['status'],r.get('cost_delta',''),round(r['seconds'],2),flush=True)
    fout.close()

if __name__=='__main__':main()
