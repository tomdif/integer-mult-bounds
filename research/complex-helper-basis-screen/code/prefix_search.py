"""Prefix changes of basis with explicit undo and final dirty restoration.

For helper-only S and a cut-free prefix M, replace M by S M S^-1,
append S^-1 at the seam, and S after the complete program. This yields
S P S^-1 = P because P fixes every helper. Every inserted gate is charged
by the existing native frame rules; there is no free internal basis change.
"""
import argparse,collections,itertools,json,signal,time
from fractions import Fraction as Q
import basis_search as b

def transform(w,shears,seam):
    touched={r for e in w['A']+w['cut']+w['precondition'] for r in b.regs(e)}
    assert not touched & {r for h,d,a in shears for r in (h,d)}
    prefix=w['B'][:seam]
    for h,d,a in shears:
        prefix=b.simplify([f for e in prefix for f in b.conjugate_gate(e,h,d,a)])
    undo=[b.add(d,h,-a) for h,d,a in reversed(shears)]
    restore=[b.add(d,h,a) for h,d,a in shears]
    out=dict(w);out['B']=b.simplify(prefix+undo+w['B'][seam:])
    out['cleanup']=[e.copy() for e in w['cleanup']]
    out['early_cleanup']=[e.copy() for e in w['early_cleanup']]
    # Restore before FULL cleanup when a selected helper has a low final frame.
    # All such gates are in the priced tail and must pass the cone conditions.
    low=set(map(int,w['helper_final']))
    for e in restore:
        i=len(out['cleanup']);out['cleanup'].append(e[:-1]+[b.FULL.copy()])
        if low & set(b.regs(e)):out['early_cleanup'].append([i,[]])
    return out

def seams(w,hs):
    # An incoming data/helper write can force the two paths apart. Consider
    # every such boundary, plus the end of B, capped by deterministic sampling.
    ins=[i for i,e in enumerate(w['B']) if e[1] in hs]
    ins += [len(w['B'])]
    return sorted(set(ins))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pairs',type=int,default=92);ap.add_argument('--blocks',action='store_true');ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    import frames as F
    from word import inline
    from model import cone_caps
    from harness import DEFAULT_B
    from writeback import write_back,audit
    from cached_frames import optimal
    w=b.load(b.PACKAGE/'inputs/BASE.json.gz')
    cost=F.Costs(DEFAULT_B);caps,_=cone_caps(w)
    graph=F.Graph(inline(w,True),check_literal=True,tail_mutable=True,caps=caps,cut_equality=True)
    base=optimal(inline(w,True),cost,graph=graph)
    print('BASE',base['cost'],base['certified'],dict(base['profile']),flush=True)
    specs=[]
    if not a.blocks:
        cs=json.loads((b.HERE/'CENSUS.json').read_text())['candidates'][:a.pairs]
        for c in cs:
            h,d=c['h'],c['d']
            for seam in seams(w,{h,d}):specs.append(([(h,d,Q(c['a']))],seam))
    else:
        # Joint rank-two updates. Intermediate shear words need not be feasible.
        # Use each natural 4-register warm block from the equal-interface groups.
        gs=b.groups(w)
        quartets=[]
        for group in gs:
            if len(group)==4:quartets.append(group)
            else:
                byoct=collections.defaultdict(list)
                for r in group:byoct[r//8].append(r)
                quartets += [v for v in byoct.values() if len(v)==4]
        for block in quartets:
            h0,h1,d0,d1=block
            for p,q in ((Q(1),Q(1)),(Q(-1),Q(-1)),(Q(1),Q(-1)),(Q(-1),Q(1))):
                for sh in ([(h0,d0,p),(h1,d1,q)],[(h0,h1,p),(d0,d1,q)],[(h0,d1,p),(h1,d0,q)]):
                    for seam in seams(w,set(block)):specs.append((sh,seam))
    # Deduplicate entire new scalar programs. Baseline is a zero-shear control.
    specs.insert(0, ([(593,594,Q(0))],1053))
    tag='blocks' if a.blocks else f'pairs-{a.pairs}'
    path=b.HERE/f'PREFIX-{tag}.jsonl'
    previous=[json.loads(s) for s in path.read_text().splitlines()] if a.resume and path.exists() else []
    last=max((r['index'] for r in previous),default=-1)
    fout=path.open('a' if a.resume else 'w');signal.signal(signal.SIGALRM,b.alarm)
    seen=set();cone_cache={}
    for i,(sh,seam) in enumerate(specs):
        r=dict(index=i,shears=[(h,d,str(q)) for h,d,q in sh],seam=seam);t=time.monotonic()
        try:v=transform(w,sh,seam)
        except AssertionError:r['status']='precondition-touched';fout.write(json.dumps(r)+'\n');continue
        key=b.hashlib.sha256(b.canon([v['B'],v['early_cleanup'],v['cleanup']])).hexdigest()
        if key in seen:continue
        seen.add(key)
        if i<=last:continue
        signal.alarm(45)
        try:
            g=F.Graph(inline(v,True),check_literal=False,tail_mutable=True,cut_equality=True)
            # With a fixed S, the complete rewritten B map is B_original*S^-1
            # for every seam. Therefore its scalar prefix cones and derived
            # compensation are identical; only the gate/frame paths differ.
            skey=tuple(sh)
            if skey not in cone_cache:cone_cache[skey]=cone_caps(v)
            cap,comp=cone_cache[skey]
            residual=set(map(int,v['start_extra']))|set(map(int,v['helper_final']))
            if any(e[2] in residual for e in comp):r['status']='residual-compensation'
            else:
                g=F.Graph(inline(v,True),check_literal=False,tail_mutable=True,caps=cap,cut_equality=True)
                z=optimal(inline(v,True),cost,check_literal=False,graph=g)
                r.update(status='priced',certified=z['certified'],cost_delta=z['cost']-base['cost'],profile=dict(z['profile']))
                if z['cost']<base['cost'] or i==0:
                    vv=write_back(v,g,z['assign']);p=b.HERE/f'prefix-{tag}-{i}.json.gz';b.save(p,vv)
                    signal.alarm(0);ok,receipt,sha=audit(vv)
                    r.update(audit_ok=ok,audit=receipt,sha256=sha,word=str(p))
        except F.Infeasible as e:r.update(status='frame-infeasible',why=str(e))
        except b.Limit:r['status']='timeout'
        except Exception as e:r.update(status='error',why=repr(e))
        finally:signal.alarm(0)
        r['seconds']=time.monotonic()-t;fout.write(json.dumps(r,sort_keys=True)+'\n');fout.flush()
        print(i,sh,seam,r['status'],r.get('cost_delta',''),round(r['seconds'],2),flush=True)
    fout.close();print('DONE',len(specs),len(seen),flush=True)

if __name__=='__main__':main()
