"""Commuting reorder screen; scheduler functions copied unchanged from
research/k8-extreme-elimination/code/reschedule_eliminated.py at b7af4fa.
Only this import header and the input/driver are new.
"""
import copy,heapq,json,signal,time
import basis_search as H
import frames as F
from word import inline
from model import cone_caps
from writeback import write_back,audit
class OrderRejected(Exception):pass

def meet_many(fs):
    s=set(range(512))
    for f in fs:s.intersection_update(F.span(tuple(f)))
    return F.basis(tuple(s))

def join_many(fs):return F.basis(tuple(x for f in fs for x in f))

def bounds(gates,starts,ends):
    n=len(gates);regs=[tuple(H.regs(e))for e in gates];touch={}
    pred=[set()for _ in gates];succ=[set()for _ in gates];pairs=set()
    for i,rr in enumerate(regs):
        for j in {j for r in rr for j in touch.get(r,[])}:
            if not F.commute(gates[j],gates[i]):pred[i].add(j);succ[j].add(i)
            else:pairs.add((j,i))
        for r in rr:touch.setdefault(r,[]).append(i)
    L0=[join_many(starts[r]for r in rr)for rr in regs]
    U0=[meet_many(ends[r]for r in rr)for rr in regs]
    def order():
        deg=[len(p)for p in pred];ready=[i for i,d in enumerate(deg)if d==0];heapq.heapify(ready);out=[]
        while ready:
            i=heapq.heappop(ready);out.append(i)
            for j in succ[i]:
                deg[j]-=1
                if deg[j]==0:heapq.heappush(ready,j)
        if len(out)!=n:raise OrderRejected(('necessary_order_cycle',len(out),n))
        return out
    added=0
    for iteration in range(4):
        seq=order();L=list(L0);U=list(U0)
        for i in seq:L[i]=join_many([L0[i],*[L[j]for j in pred[i]]])
        for i in reversed(seq):U[i]=meet_many([U0[i],*[U[j]for j in succ[i]]])
        for i in range(n):
            if not F.leq(L[i],U[i]):raise OrderRejected(('necessary_frame_bounds',i,regs[i],list(L[i]),list(U[i]),iteration))
        changes=0
        for i,j in sorted(pairs):
            for a,b in [(i,j),(j,i)]:
                if not F.leq(L[a],U[b]) and b not in pred[a]:
                    pred[a].add(b);succ[b].add(a);changes+=1
        added+=changes
        if not changes:break
    order()
    return regs,pred,succ,U,touch,added

def schedule(gates,starts,ends,fixed,mode,prepared):
    regs,pred,succ,U,touch,added=prepared
    deg=[len(p)for p in pred];ready={i for i,d in enumerate(deg)if d==0};cur=list(starts)
    remaining={r:len(v)for r,v in touch.items()};out=[];indices=[]
    while ready:
        options=[]
        for i in ready:
            f=join_many([*(cur[r]for r in regs[i]),*(fixed[r]for r in regs[i]if r in fixed and remaining[r]==1)])
            if not F.leq(f,U[i]):raise OrderRejected(('greedy_frame_pollution',i,mode))
            keys=[(len(f),len(U[i]),i),(len(U[i]),len(f),i),(-len(succ[i]),len(f),i),(len(f),(i*2654435761)%4294967296,i)]
            options.append((keys[mode],i,f))
        _,i,f=min(options);ready.remove(i);indices.append(i);out.append(list(gates[i][:-1])+[list(f)])
        for r in regs[i]:cur[r]=f;remaining[r]-=1
        for j in succ[i]:
            deg[j]-=1
            if deg[j]==0:ready.add(j)
    assert len(out)==len(gates)
    position={j:i for i,j in enumerate(indices)}
    assert all(position[j]<position[i]for i,p in enumerate(pred)for j in p)
    assert all(F.leq(c,e)for c,e in zip(cur,ends))
    return out,cur,dict(order=indices,added_frame_precedences=added)

def transform(w,mode):
    n=224+w['report']['R'];z=copy.deepcopy(w);ii=inline(w,True)
    starts=[F.basis(tuple(x))for x in ii['_start_frames']];ends=[F.basis(tuple(x))for x in ii['_final_frames']]
    ids={i for i,U in w['early_cleanup']}
    bgates=w['B']+[list(w['cleanup'][i][:-1])+[[]]for i,U in w['early_cleanup']]
    # Every B/tail gate sharing r and s forces end(A,r) inside final(s).
    acaps=list(ends)
    for e in bgates:
        rr=H.regs(e);cap=meet_many(ends[r]for r in rr)
        for r in rr:acaps[r]=meet_many([acaps[r],cap])
    fixed={r:F.basis(tuple(f))for r,f in zip(w['centers'],w['center_frames'])}
    fixed.update({112+t:F.basis(tuple(w.get('target_levels',{}).get(str(t),[])))for t in range(112)})
    for r,f in fixed.items():acaps[r]=meet_many([acaps[r],f])
    try:
        prep=bounds(w['A'],starts,acaps);z['A'],cur,ra=schedule(w['A'],starts,acaps,fixed,mode,prep)
    except OrderRejected as e:raise OrderRejected(('A',e.args))
    # Force the cut interfaces. Other cur entries are the actual A end frames.
    assert all(cur[r]==f for r,f in fixed.items())
    try:
        prep=bounds(bgates,cur,ends);z['B'],cur,rb=schedule(bgates,cur,ends,{},mode,prep)
    except OrderRejected as e:raise OrderRejected(('B',e.args))
    z['cleanup']=[e for i,e in enumerate(w['cleanup'])if i not in ids];z['early_cleanup']=[]
    return z,dict(A=ra,B=rb)


if __name__=='__main__':
    from harness import DEFAULT_B
    w=H.load(H.PACKAGE/'inputs/BASE.json.gz')
    costs=F.Costs(DEFAULT_B);caps,_=cone_caps(w)
    g=F.Graph(inline(w,True),check_literal=True,tail_mutable=True,caps=caps,cut_equality=True)
    base=F.optimal_frames(inline(w,True),costs,graph=g)
    cs=json.loads((H.HERE/'CENSUS.json').read_text())['candidates'][:11]
    signal.signal(signal.SIGALRM,H.alarm)
    out=[]
    for i,c in enumerate(cs):
        v=H.transform(w,c['h'],c['d'],H.Q(c['a']))
        for mode in range(4):
            t=time.monotonic();r=dict(index=i,mode=mode,candidate=c);signal.alarm(75)
            try:
                z,order=transform(v,mode);cap,comp=cone_caps(z)
                residual=set(map(int,z['start_extra']))|set(map(int,z['helper_final']))
                assert not any(e[2] in residual for e in comp)
                g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=cap,cut_equality=True)
                rr=F.optimal_frames(inline(z,True),costs,check_literal=False,graph=g)
                vv=write_back(z,g,rr['assign']);signal.alarm(0)
                ok,receipt,sha=audit(vv)
                r.update(status='priced',certified=rr['certified'],cost_delta=rr['cost']-base['cost'],audit_ok=ok,audit=receipt)
                H.save(H.HERE/f'reorder-{i}-{mode}.json.gz',vv)
            except (OrderRejected,F.Infeasible) as e:r.update(status='rejected',why=str(e))
            except H.Limit:r['status']='timeout'
            except Exception as e:r.update(status='error',why=repr(e))
            finally:signal.alarm(0)
            r['seconds']=time.monotonic()-t;out.append(r)
            (H.HERE/'REORDER.json').write_text(json.dumps(out,indent=2)+'\n')
            print(i,mode,r['status'],r.get('cost_delta',r.get('why','')),round(r['seconds'],2),flush=True)
            if "'A'" in r.get('why','') and 'necessary_' in r['why']:break
