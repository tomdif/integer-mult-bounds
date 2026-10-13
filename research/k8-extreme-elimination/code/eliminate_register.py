"""Compile away a cold FULL helper by tracking its exact linear relation.

Maintain x_h=sum(a_j*x_j) with x_h initially zero. Remove writes of h,
expand reads of h, and update the relation under every other gate. Reject a
singular pivot or a non-dyadic-unit scale. This is a restricted elimination
compiler, not a claim that other helpers or pivot strategies are impossible.
"""
from fractions import Fraction as Q
from collections import Counter
import copy,json,gzip,sys,os,time,signal,multiprocessing as mp
from pathlib import Path
W=Path(__import__('os').environ['EXTREME_WORK']).resolve()
ROOT=Path(__file__).resolve().parents[3]
os.environ['IMB_ROOT']=str(ROOT)
sys.path.insert(0,str(ROOT/'research/x54-mixed-allocation/vendor/pr1186'))
import frames as F,harness as H
from word import inline
from model import cone_caps
from writeback import write_back,audit
FULL=[256,128,64,32,16,8,4,2,1]

class Rejected(Exception):pass

def eliminate(base,h):
    assert h>=224 and h not in base['centers']
    assert str(h) not in base['start_extra'] and str(h) not in base['helper_final']
    a={};expanded=0;events=0;largest=0
    def put(j,q):
        if q:a[j]=q
        else:a.pop(j,None)
    def compile_gate(e,frame):
        nonlocal expanded,events,largest
        events+=1;t=e[1];q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
        if t==h:
            if e[0]=='add':put(e[2],a.get(e[2],Q(0))+q)
            else:
                for j in list(a):put(j,q*a[j])
            largest=max(largest,len(a));return []
        if e[0]=='add' and e[2]==h:
            c=1+q*a.get(t,Q(0))
            if not c:raise Rejected(('singular_elimination_pivot',events,t,len(a)))
            if abs(c.numerator)&(abs(c.numerator)-1) or c.denominator&(c.denominator-1):
                raise Rejected(('non_dyadic_unit_pivot',events,str(c)))
            gates=[]
            if c!=1:gates.append(['scale',t,c.numerator,c.denominator,list(frame)])
            for j,x in sorted(a.items()):
                if j!=t:
                    z=q*x;gates.append(['add',t,j,z.numerator,z.denominator,list(frame)])
            for j in list(a):a[j]/=c
            expanded+=len(gates)-1
            return gates
        if e[0]=='add':put(e[2],a.get(e[2],Q(0))-q*a.get(t,Q(0)))
        elif t in a:a[t]/=q
        largest=max(largest,len(a))
        return [list(e[:-1])+[None if frame is None else list(frame)]]
    z=copy.deepcopy(base)
    for sec in ['precondition','A','cut','B']:
        z[sec]=[g for e in base[sec] for g in compile_gate(e, e[-1] if sec=='cut' else [])]
    early=base['early_cleanup'];ids={i for i,U in early}
    tail=[g for i,U in early for g in compile_gate(base['cleanup'][i],[])]
    rest=[g for i,e in enumerate(base['cleanup'])if i not in ids for g in compile_gate(e,FULL)]
    if a:raise Rejected(('nonzero_final_relation',len(a)))
    z['cleanup']=tail+rest;z['early_cleanup']=[[i,[]]for i in range(len(tail))]
    lower=set(map(int,base['helper_final']))
    for e in rest:
        if any(r in lower for r in H.regs(e)):raise Rejected(('full_cleanup_reads_low_end',e[:5]))
    for sec in ['precondition','A','cut','B','cleanup']:
        for e in z[sec]:
            for i in [1,2]if e[0]=='add'else[1]:
                assert e[i]!=h;e[i]-=e[i]>h
    for field in ['start_extra','helper_final']:
        z[field]={str(int(r)-(int(r)>h)):f for r,f in z[field].items()}
    z['centers']=[r-(r>h)for r in z['centers']]
    z['report']['R']-=1
    return z,dict(expanded_gate_delta=expanded,max_relation_support=largest,removed_helper=h)

def literal_program(w):
    ids={i for i,U in w['early_cleanup']}
    return w['precondition']+w['A']+w['cut']+w['B']+[w['cleanup'][i]for i,U in w['early_cleanup']]+[e for i,e in enumerate(w['cleanup'])if i not in ids]

def replay_mod(w,x):
    p=H.PR;x=list(x)
    for e in literal_program(w):
        q=Q(e[3],e[4])if e[0]=='add'else Q(e[2],e[3]);c=q.numerator*pow(q.denominator,p-2,p)%p
        if e[0]=='add':x[e[1]]=(x[e[1]]+c*x[e[2]])%p
        else:x[e[1]]=x[e[1]]*c%p
    return x

def check_elimination(base,z,h):
    import random
    rng=random.Random(20261013+h)
    for _ in range(2):
        x=[rng.randrange(H.PR)for _ in range(224+base['report']['R'])];x[h]=0
        y=replay_mod(base,x);yy=replay_mod(z,x[:h]+x[h+1:])
        assert y[h]==0 and y[:h]+y[h+1:]==yy,'Compiler map mismatch'

def init():
    global base,C,oldcost
    base=H.load(str(ROOT/'research/x54-mixed-allocation/data/THREE-WORD.json.gz'))
    C=F.Costs(H.DEFAULT_B);oldcost=C.profile_cost({int(r):n for r,n in base['report']['local_profile'].items()})

def trial(h):
    start=time.monotonic();rec=dict(helper=h)
    signal.signal(signal.SIGALRM,H._alarm);signal.alarm(40)
    try:
        z,detail=eliminate(base,h);rec.update(detail);check_elimination(base,z,h);rec['modular_compiler_checks']=2
        # First reject unavoidable boundary violations before expensive cones.
        F.Graph(inline(z,True),check_literal=False,tail_mutable=True,cut_equality=True)
        caps,comp=cone_caps(z)
        if any(e[2]in set(map(int,z['start_extra']))|set(map(int,z['helper_final']))for e in comp):raise Rejected('residual_compensation')
        g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
        r=F.optimal_frames(inline(z,True),C,check_literal=False,graph=g);word=write_back(z,g,r['assign'])
        profile={int(k):v for k,v in word['report']['local_profile'].items()};delta=C.profile_cost(profile)-oldcost+C.c[9]
        rec.update(status='certified'if r['certified']else'uncertified',profile=profile,delta_with_idle9=delta,
                   relaxed_delta_with_idle48_ninths=48*(C.profile_cost(profile)-oldcost)+9*C.c[48])
        if r['certified'] and rec['relaxed_delta_with_idle48_ninths']<0:
            ok,receipt,ident=audit(word);rec.update(exact_audit=receipt,exact_audit_pass=ok,word_identity=ident)
            if ok:
                path=W/'elimination'/f'helper-{h}.json.gz';path.write_bytes(gzip.compress(json.dumps(word,sort_keys=True,separators=(',',':')).encode(),mtime=0));rec['word']=str(path)
    except Rejected as e:rec.update(status='compiler_rejected',reason=str(e))
    except F.Infeasible as e:rec.update(status='frame_infeasible',reason=str(e)[:240])
    except H.Timeout:rec.update(status='timeout')
    except ValueError as e:rec.update(status='solver_limit',reason=str(e)[:240])
    finally:signal.alarm(0)
    rec['seconds']=round(time.monotonic()-start,3);return rec

if __name__=='__main__':
    w=H.load(str(ROOT/'research/x54-mixed-allocation/data/THREE-WORD.json.gz'))
    excluded=set(map(int,w['start_extra']))|set(map(int,w['helper_final']))|set(w['centers'])
    cases=sorted(set(range(224,224+w['report']['R']))-excluded)
    out=W/'elimination';out.mkdir(exist_ok=True);results=[];print('CASES',len(cases),flush=True)
    with mp.get_context('fork').Pool(3,initializer=init,maxtasksperchild=50)as pool:
        for r in pool.imap_unordered(trial,cases,chunksize=1):
            results.append(r)
            if r.get('exact_audit_pass'):print('NOMINATION',r,flush=True)
            if len(results)%10==0:print('PROGRESS',len(results),dict(Counter(x['status']for x in results)),flush=True)
            (out/'RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
    print('DONE',len(results),dict(Counter(x['status']for x in results)),flush=True)
