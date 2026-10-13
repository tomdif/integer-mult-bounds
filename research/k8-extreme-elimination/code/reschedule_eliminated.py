"""Try global commuting reorderings after whole-register elimination.

Keep every pair of noncommuting gates in its original order. Propagate
necessary frame bounds, add order constraints when sharing a register forces
one frame before another, then try four deterministic scheduling priorities.
Cleanup-tail gates participate in B scheduling. A bound rejection applies
only to this compiled gate trace and its stated phase boundaries.
"""
import dynamic_elimination as D
import eliminate_register as E
from eliminate_register import *
import heapq

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

def trial_reorder(row):
    hs=row['helpers'];rec=dict(helpers=hs,attempts=[]);t=time.monotonic()
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(75)
    try:
        w=E.base
        for h in sorted(hs,reverse=True):w,_=D.eliminate_dynamic(w,h)
        for mode in range(4):
            try:
                z,order=transform(w,mode);caps,comp=cone_caps(z)
                if any(e[2]in set(map(int,z['start_extra']))|set(map(int,z['helper_final']))for e in comp):raise OrderRejected('residual_compensation')
                g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
                r=F.optimal_frames(inline(z,True),E.C,check_literal=False,graph=g);word=write_back(z,g,r['assign'])
                profile={int(k):v for k,v in word['report']['local_profile'].items()};delta=E.C.profile_cost(profile)-E.oldcost
                attempt=dict(mode=mode,status='certified'if r['certified']else'uncertified',profile=profile,delta_with_idle9=delta+len(hs)*E.C.c[9],relaxed_delta48=48*delta+9*len(hs)*E.C.c[48])
                if r['certified']:
                    ok,a,ident=audit(word);attempt.update(exact_audit_pass=ok,exact_audit=a)
                    if ok:
                        name='h-'+'-'.join(map(str,hs))+f'-mode{mode}';path=W/'reorder'/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));attempt['word']=str(path)
                        (W/'reorder'/(name+'-order.json')).write_text(json.dumps(order)+'\n')
                rec['attempts'].append(attempt)
            except (OrderRejected,F.Infeasible,ValueError)as e:
                rec['attempts'].append(dict(mode=mode,status=type(e).__name__,reason=str(e)[:500]))
                if 'necessary_'in str(e) and "'A'"in str(e):break
        rec['status']='completed'
    except H.Timeout:rec['status']='timeout'
    except Rejected as e:rec.update(status='compiler_rejected',reason=str(e))
    finally:signal.alarm(0)
    rec['seconds']=round(time.monotonic()-t,3);return rec

if __name__=='__main__':
    import eliminate_register as E
    rows=json.loads((W/'dynamic/RESULTS.json').read_text());rows=[r for r in rows if'compilation'in r]
    rows=sorted(rows,key=lambda r:(-len(r['helpers']),r['helpers']))
    out=W/'reorder';out.mkdir(exist_ok=True);results=[];print('CASES',len(rows),flush=True)
    with mp.get_context('fork').Pool(3,initializer=D.init_dynamic,maxtasksperchild=30)as pool:
        for r in pool.imap_unordered(trial_reorder,rows,chunksize=1):
            results.append(r)
            if any(a.get('exact_audit_pass')for a in r['attempts']):print('NOMINATION',r,flush=True)
            if len(results)%10==0:print('PROGRESS',len(results),dict(Counter(x['status']for x in results)),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),flush=True)
