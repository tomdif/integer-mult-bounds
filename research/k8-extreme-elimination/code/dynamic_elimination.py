"""Exact one-hole elimination with dyadic pivoting; single and joint screens.

When the direct substitution is singular or introduces a forbidden scale,
move the eliminated logical coordinate into another cold FULL helper. A
checked final permutation restores the physical register interface. Frame
feasibility, scalar audits, and global admission remain separate requirements.
"""
import eliminate_register as E
from eliminate_register import *

def unit(q):
    return bool(q) and not(abs(q.numerator)&(abs(q.numerator)-1)) and not(q.denominator&(q.denominator-1))

def eliminate_dynamic(base,h):
    excluded=set(map(int,base['start_extra']))|set(map(int,base['helper_final']))|set(base['centers'])
    pool=set(range(224,224+base['report']['R']))-excluded
    assert h in pool
    missing=h;a={};mapping={r:r-(r>h)for r in range(224+base['report']['R'])if r!=h};original=dict(mapping)
    pivots=[];peak=0;ngates=0
    def put(j,q):
        if q:a[j]=q
        else:a.pop(j,None)
    def gate(e,frame):
        nonlocal missing,a,peak,ngates
        t=e[1];q=Q(e[3],e[4])if e[0]=='add'else Q(e[2],e[3]);f=None if frame is None else list(frame)
        if t==missing:
            if e[0]=='add':put(e[2],a.get(e[2],Q(0))+q)
            else:
                for j in list(a):put(j,a[j]*q)
            out=[]
        elif e[0]=='add' and e[2]==missing:
            at=a.get(t,Q(0));c=1+q*at;pt=mapping[t]
            if unit(c):
                out=[] if c==1 else [['scale',pt,c.numerator,c.denominator,f]]
                out += [['add',pt,mapping[j],(q*x).numerator,(q*x).denominator,f]for j,x in sorted(a.items())if j!=t]
                a={j:x/c for j,x in a.items()}
            elif t in pool and unit(at):
                # Compute the missing coordinate in t's physical slot.
                out=[] if at==1 else [['scale',pt,at.numerator,at.denominator,f]]
                out += [['add',pt,mapping[j],x.numerator,x.denominator,f]for j,x in sorted(a.items())if j!=t]
                old=missing;mapping[old]=mapping.pop(t);missing=t
                a={j:-x/at for j,x in a.items()if j!=t}
                if c:a[old]=c/at
                pivots.append(dict(old_hole=old,new_hole=t,coefficient=str(at)))
            else:raise Rejected(('no_legal_dyadic_pivot',missing,t,str(at),str(c)))
        else:
            z=list(e);z[1]=mapping[t];z[-1]=f
            if e[0]=='add':
                z[2]=mapping[e[2]];put(e[2],a.get(e[2],Q(0))-q*a.get(t,Q(0)))
            elif t in a:a[t]/=q
            out=[z]
        peak=max(peak,len(a));ngates+=len(out)
        if ngates>60000 or peak>256:raise Rejected(('compiler_budget',ngates,peak))
        return out
    z=copy.deepcopy(base)
    for sec in ['precondition','A','cut','B']:
        z[sec]=[x for e in base[sec]for x in gate(e,e[-1]if sec=='cut'else[])]
    ids={i for i,U in base['early_cleanup']}
    tail=[x for i,U in base['early_cleanup']for x in gate(base['cleanup'][i],[])]
    rest=[x for i,e in enumerate(base['cleanup'])if i not in ids for x in gate(e,FULL)]
    if missing!=h or a:raise Rejected(('wrong_final_hole',missing,h,len(a)))
    inverse={p:r for r,p in mapping.items()};swaps=[]
    for r in sorted(mapping):
        p=mapping[r];target=original[r]
        if p==target:continue
        other=inverse[target]
        assert r in pool and other in pool
        rest += [['add',p,target,1,1,FULL],['add',target,p,-1,1,FULL],['add',p,target,1,1,FULL],['scale',target,-1,1,FULL]]
        mapping[r],mapping[other]=target,p;inverse[p],inverse[target]=other,r;swaps.append([p,target])
    assert mapping==original
    z['cleanup']=tail+rest;z['early_cleanup']=[[i,[]]for i in range(len(tail))]
    for field in ['start_extra','helper_final']:z[field]={str(original[int(r)]):f for r,f in base[field].items()}
    z['centers']=[original[r]for r in base['centers']];z['report']['R']-=1
    lower=set(map(int,z['helper_final']))
    for e in rest:
        if any(r in lower for r in H.regs(e)):raise Rejected(('full_cleanup_reads_low_end',e[:5]))
    return z,dict(removed_helper=h,pivots=pivots,final_swaps=swaps,peak_relation_support=peak,scalar_gates=ngates+4*len(swaps))

def init_dynamic():
    E.init()

def trial_dynamic(hs):
    start=time.monotonic();rec=dict(helpers=hs);signal.signal(signal.SIGALRM,H._alarm);signal.alarm(60)
    try:
        word=E.base;details=[]
        for h in sorted(hs,reverse=True):
            old=word;word,detail=eliminate_dynamic(old,h);check_elimination(old,word,h);details.append(detail)
        rec.update(compilation=details,modular_compiler_checks=2*len(hs))
        F.Graph(inline(word,True),check_literal=False,tail_mutable=True,cut_equality=True)
        caps,comp=cone_caps(word)
        if any(e[2]in set(map(int,word['start_extra']))|set(map(int,word['helper_final']))for e in comp):raise Rejected('residual_compensation')
        g=F.Graph(inline(word,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
        r=F.optimal_frames(inline(word,True),E.C,check_literal=False,graph=g);word=write_back(word,g,r['assign'])
        profile={int(k):v for k,v in word['report']['local_profile'].items()};d=E.C.profile_cost(profile)-E.oldcost
        rec.update(status='certified'if r['certified']else'uncertified',profile=profile,delta_with_idle9=d+len(hs)*E.C.c[9],
                   relaxed_delta48=48*d+9*len(hs)*E.C.c[48])
        if r['certified'] and rec['relaxed_delta48']<0:
            ok,receipt,ident=audit(word);rec.update(exact_audit_pass=ok,exact_audit=receipt,identity=ident)
            if ok:
                path=W/'dynamic'/('helpers-'+'-'.join(map(str,hs))+'.json.gz');path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));rec['word']=str(path)
    except Rejected as e:rec.update(status='compiler_rejected',reason=str(e))
    except F.Infeasible as e:rec.update(status='frame_infeasible',reason=str(e)[:240])
    except H.Timeout:rec.update(status='timeout')
    except ValueError as e:rec.update(status='solver_limit',reason=str(e)[:240])
    finally:signal.alarm(0)
    rec['seconds']=round(time.monotonic()-start,3);return rec

if __name__=='__main__':
    base=H.load(str(ROOT/'research/x54-mixed-allocation/data/THREE-WORD.json.gz'))
    excluded=set(map(int,base['start_extra']))|set(map(int,base['helper_final']))|set(base['centers'])
    helpers=sorted(set(range(224,704))-excluded);cases=[(h,)for h in helpers]
    # Deterministic joint deletions, up to the entire 237-helper cold set.
    for n in [2,4,8,16,32,64,len(helpers)]:
        for start in range(0,len(helpers)-n+1,n):cases.append(tuple(helpers[start:start+n]))
    cases=list(dict.fromkeys(cases));out=W/'dynamic';out.mkdir(exist_ok=True)
    (out/'CASES.json').write_text(json.dumps(cases,indent=2)+'\n');results=[];print('CASES',len(cases),flush=True)
    with mp.get_context('fork').Pool(3,initializer=init_dynamic,maxtasksperchild=40)as pool:
        for r in pool.imap_unordered(trial_dynamic,cases,chunksize=1):
            results.append(r)
            if r.get('exact_audit_pass'):print('NOMINATION',r,flush=True)
            if len(results)%10==0:print('PROGRESS',len(results),dict(Counter(x['status']for x in results)),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),dict(Counter(x['status']for x in results)),flush=True)
