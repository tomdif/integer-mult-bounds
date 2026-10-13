"""Diagonalize each four-helper correction matrix with exact dyadic row shears.

This tries noncommuting, dense changes of basis as well as disjoint pair moves.
The chosen pivot order changes the explicit undo circuit. No elimination step
is treated as free: prefix_search emits the inverse and dirty restoration.
"""
import itertools,json,signal,time
from fractions import Fraction as Q
import basis_search as b
import prefix_search as p
import frames as F
from word import inline
from model import cone_caps
from harness import DEFAULT_B
from writeback import write_back,audit
from cached_frames import optimal

def eliminate(matrix,order):
    m=[r.copy() for r in matrix];ops=[]
    def step(h,d,q):
        assert q.denominator&(q.denominator-1)==0
        if q:
            m[d]=[x+q*y for x,y in zip(m[d],m[h])];ops.append((h,d,q))
    for pos,j in enumerate(order):
        if not m[j][j]:
            r=next((r for r in order[pos+1:] if m[r][j]),None)
            if r is None:return None
            step(r,j,Q(1))
        for i in order:
            if i!=j and m[i][j]:
                q=-m[i][j]/m[j][j]
                if q.denominator&(q.denominator-1):return None
                step(j,i,q)
    assert all(not m[i][j] for i in range(4) for j in range(4) if i!=j)
    assert all(m[i][i] for i in range(4))
    return ops,m

def main():
    w=b.load(b.PACKAGE/'inputs/BASE.json.gz');cost=F.Costs(DEFAULT_B)
    caps,_=cone_caps(w);g=F.Graph(inline(w,True),check_literal=True,tail_mutable=True,caps=caps,cut_equality=True)
    base=optimal(inline(w,True),cost,graph=g)
    touched={r for e in w['A']+w['cut']+w['precondition'] for r in b.regs(e)}
    specs=[];matrices=[]
    for start in range(592,704,8):
        hs=[start+i for i in (0,1,2,4)];ds=[start+i for i in (3,5,6,7)]
        if set(hs)&touched:continue
        assert len({tuple(w['start_extra'].get(str(h),[])) for h in hs})==1
        assert all(str(h) not in w['helper_final'] for h in hs)
        matrix=[[Q(0) for _ in range(4)] for _ in range(4)];indices=[]
        for i,e in enumerate(w['B']):
            if e[0]=='add' and e[1] in hs and e[2] in ds and len(e[-1])<=5:
                matrix[hs.index(e[1])][ds.index(e[2])]+=b.coef(e);indices.append(i)
        stop=max(indices)+1
        later=[i for i,e in enumerate(w['B']) if i>=stop and e[1] in hs]
        cuts=sorted({stop,min(later),min(later)+2,len(w['B'])})
        matrices.append(dict(helpers=hs,sources=ds,matrix=[[str(q) for q in row] for row in matrix],cuts=cuts))
        for order in itertools.permutations(range(4)):
            answer=eliminate(matrix,order)
            if answer is None:continue
            ops,diagonal=answer
            sh=[(hs[h],hs[d],q) for h,d,q in ops]
            for cut in cuts:specs.append((sh,cut,hs,order,diagonal))
    (b.HERE/'DENSE-MATRICES.json').write_text(json.dumps(matrices,indent=2)+'\n')
    out=(b.HERE/'DENSE.jsonl').open('w');seen=set();signal.signal(signal.SIGALRM,b.alarm);positive=False
    print('SPECS',len(specs),'MATRICES',len(matrices),flush=True)
    for i,(sh,cut,hs,order,diagonal) in enumerate(specs):
        z=p.transform(w,sh,cut);key=b.hashlib.sha256(b.canon([z['B'],z['cleanup']])).hexdigest()
        if key in seen:continue
        seen.add(key);r=dict(index=i,helpers=hs,pivot_order=order,seam=cut,shears=[(h,d,str(q)) for h,d,q in sh],B_delta=len(z['B'])-len(w['B']))
        t=time.monotonic();signal.alarm(45)
        try:
            g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,cut_equality=True)
            cap,comp=cone_caps(z);residual=set(map(int,z['start_extra']))|set(map(int,z['helper_final']))
            if any(e[2] in residual for e in comp):r['status']='residual-compensation'
            else:
                g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=cap,cut_equality=True)
                rr=optimal(inline(z,True),cost,graph=g)
                r.update(status='priced',certified=rr['certified'],cost_delta=rr['cost']-base['cost'],profile=dict(rr['profile']))
                if not positive or rr['cost']<base['cost']:
                    vv=write_back(z,g,rr['assign']);name=f'dense-{i}.json.gz';b.save(b.HERE/name,vv)
                    signal.alarm(0);ok,receipt,sha=audit(vv);r.update(audit_ok=ok,audit=receipt,word=name)
                    positive=True
        except F.Infeasible as e:r.update(status='frame-infeasible',why=str(e))
        except b.Limit:r['status']='timeout'
        except Exception as e:r.update(status='error',why=repr(e))
        finally:signal.alarm(0)
        r['seconds']=time.monotonic()-t;out.write(json.dumps(r,sort_keys=True)+'\n');out.flush()
        print(i,hs,order,cut,r['status'],r.get('cost_delta',''),round(r['seconds'],2),flush=True)
    out.close();print('DONE',len(specs),len(seen),flush=True)

if __name__=='__main__':main()
