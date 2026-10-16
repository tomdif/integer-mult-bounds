"""Source binding and counterexamples for the quantified Guard.lean lemmas.

Finite executions supplement the kernel proof. Python arithmetic is not
charged as unit-cost, and these checks do not run B1 or a complete multiplier.
"""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import random
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def authenticate():
    checked=[]
    for entry in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if entry['usage']!='input':continue
        raw=(ROOT/entry['path']).read_bytes()
        need(sha256(raw).hexdigest()==entry['sha256'],'changed input '+entry['path'])
        checked.append(entry['path'])
    return checked


def kernel_receipt():
    kernel=json.loads((HERE/'KERNEL.json').read_text())
    source=(HERE/'Guard.lean').read_bytes()
    names=set(re.findall(r'^#print axioms (\w+)$',source.decode(),re.M))
    need(kernel['status']=='PASS_COMPACT_GUARD_REPAIR_KERNEL' and kernel['kernel_checked'] is True,
         'retained successful kernel receipt')
    need(kernel['source_sha256']==sha256(source).hexdigest(),'kernel source authentication')
    need(set(kernel['axioms'])==names and len(names)==19,'nineteen kernel declarations')
    need(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in kernel['axioms'].values()),
         'standard kernel axioms only')
    deps=json.loads((HERE/'lean/lake-manifest.json').read_text())['packages']
    need(kernel['dependencies']=={d['name']:d['rev'] for d in deps},'kernel dependency receipt')
    need(set(kernel['rejected_controls'])=={'scratch_guard_omitted','loaded_maximum_excluded',
         'loaded_parity_omitted','forward_instead_of_inverse'},'four kernel rejection controls')


def literal_operations():
    # Independent transcription of the four arithmetic updates and shuttles.
    F=[('rotate','y',('u','t'),'first_compact',1),
       ('swap','t','b'),('rotate','b',('y',),'selected_y',1),('swap','t','b'),
       ('rotate','y',('u','t'),'second_compact',1),
       ('swap','t','b'),('rotate','b',('u','y'),'original_compact',-1),('swap','t','b')]
    load=[('swap','u','b'),('rotate','b',('y',),'selected_x',1),('swap','u','b')]
    unload=[('swap','u','b'),('rotate','b',('y',),'selected_x',-1),('swap','u','b')]
    return tuple(F+load+F+unload)


def trace(word,layout,state):
    current=dict(state);out=[dict(current)]
    for op in word.operations():
        if op[0]=='swap':current[op[1]],current[op[2]]=current[op[2]],current[op[1]]
        else:current[op[1]]=(current[op[1]]+word.offset(current,op))%(1<<layout.width(op[1]))
        out.append(dict(current))
    return out


def exhaustive(SparseWord,compact):
    results=[]
    for G,K in ((2,6),(3,7)):
        word=SparseWord((0,),(2,),K,G)
        layout=compact.Layout((('u',G),('t',G),('y',K),('b',G)),1)
        word.validate(layout)
        need(word.operations()==literal_operations(),'source word matches formal schedule')
        good=bad=errors=loaded_max=0
        seen=bytearray(layout.records);corrected=bytearray(layout.records)
        B=1<<G;M=1<<(K-1)
        for index in range(layout.records):
            state=layout.decode(index);raw=word.execute(state,layout)
            need(word.execute(raw,layout,True)==state,'inverse uses current controls')
            dest=layout.encode(raw);need(not seen[dest],'raw bijection');seen[dest]=1
            need(word.bad(raw)==word.bad(state),'raw good-set invariance')
            if word.bad(state):
                bad+=1;fixed=word.ideal(word.execute(raw,layout,True))
            else:
                good+=1;need(raw==word.ideal(state),'good-address paired word');fixed=raw
                if state['u']==B-2 and (state['y']>>2)&1:
                    steps=trace(word,layout,state)
                    need(steps[11]['u']==B-1,'loaded maximum permitted')
                    need(steps[19]['t']==state['t'],'second F restores scratch at maximum control')
                    loaded_max+=1
            need(fixed==word.ideal(state),'post-repair endpoint')
            key=layout.encode(fixed);need(not corrected[key],'corrected keys injective');corrected[key]=1
            errors+=raw!=word.ideal(state)
        expected=(B-1)**2*(M-4*B)*2*B
        need(good==expected and good+bad==layout.records,'exact independent guard census')
        need(Q(bad,layout.records)<=Q(2,B)+Q(4*B,M),'single-guard density bound')
        need(all(seen) and all(corrected) and loaded_max>0 and errors>0,'nonvacuous coverage')
        results.append(dict(G=G,K=K,addresses=layout.records,good=good,bad=bad,
                            raw_errors=errors,loaded_maximum_good_cases=loaded_max))
    return results


def packed_cases(SparseWord,compact):
    rng=random.Random(2745);out=[]
    for G in (2,3,5):
        B=1<<G;K=2*G+4;M=1<<(K-1)
        targets=(0,K+3,2*K+7)
        sources=(targets[1]+1,targets[2]+2,targets[0]+3)
        word=SparseWord(targets,sources,K,G)
        layout=compact.Layout((('u',4*G),('t',4*G),('y',targets[-1]+K+2),('b',4*G)),1)
        word.validate(layout);maximum=0
        for case in range(1024):
            state={name:rng.randrange(1<<layout.width(name)) for name in layout.names}
            for name in ('u','t'):
                state[name]=sum((B-2 if case%3==0 else rng.randrange(B-1))<<(i*G)
                                for i in range(3)) | (rng.randrange(B)<<(3*G))
            for j in targets:
                h=2*B if case%3==0 else M-2*B-1 if case%3==1 else rng.randrange(2*B,M-2*B)
                state['y']=(state['y']&~(((1<<K)-1)<<j))|((2*h+rng.randrange(2))<<j)
            need(not word.bad(state),'constructed entry satisfies guards')
            steps=trace(word,layout,state)
            need(steps[-1]==word.ideal(state),'uneven-guard endpoint')
            need(word.execute(steps[-1],layout,True)==state,'uneven-guard inverse')
            for end in (8,19):
                need(steps[end]['t']==state['t'] and steps[end]['b']==state['b'],'dirty scratch restored')
                for j in targets:
                    need(((steps[end]['y']>>(j+1))&(M-1))==((state['y']>>(j+1))&(M-1)),
                         'completed F fixes higher guard bits')
                need(word.packed(steps[end]['y'],sources)==word.packed(state['y'],sources),
                     'cross-guard sources preserved')
            for i in range(3):
                loaded=(steps[11]['u']>>(i*G))&(B-1)
                expected=((state['u']>>(i*G))&(B-1))+((state['y']>>sources[i])&1)
                need(loaded==expected,'load causes no inter-digit carry')
                maximum+=loaded==B-1
            need(steps[11]['u']>>(3*G)==state['u']>>(3*G),'inactive high digit untouched')
        need(maximum>0,'maximum transient controls exercised')
        out.append(dict(G=G,K=K,targets=targets,sources=sources,states=1024,
                        maximum_transient_controls=maximum,active_digits=3,capacity_digits=4))
    return out


def counterexamples(SparseWord,compact):
    word=SparseWord((0,6),(2,8),6,2)
    layout=compact.Layout((('u',4),('t',4),('y',12),('b',4)),1)
    fixtures={
        'omit_guard_margin':dict(u=1,t=2,y=63,b=9),
        'allow_control_overflow':dict(u=3,t=0,y=1044,b=11),
        'allow_scratch_overflow':dict(u=1,t=3,y=1045,b=11)}
    out={}
    for name,state in fixtures.items():
        raw=word.execute(state,layout);ideal=word.ideal(state)
        need(raw!=ideal,'necessary hypothesis counterexample: '+name)
        need(word.bad(state),'counterexample excluded by entry predicate')
        out[name]=dict(input=state,raw=raw,ideal=ideal)
    S=(1,2,0);Sinv=(2,0,1);T=(0,1,2)
    need(T[Sinv[S[0]]]==T[0] and T[S[S[0]]]!=T[0],'forward map fails repair')
    out['forward_in_place_of_inverse']=dict(S=S,T=T,input=0,current=S[0],wrong=T[S[S[0]]])
    S=(1,0,2);T=(1,2,0);good={0};Sinv=(1,0,2)
    need(S[0]==T[0] and T[0] not in good,'dropped invariant premise')
    current=S[1];wrong=current if current in good else T[Sinv[current]]
    need(wrong!=T[1],'noninvariant good set fails selective repair')
    out['omit_ideal_good_invariance']=dict(S=S,T=T,good=[0],input=1,current=current,wrong=wrong)
    return out


def main():
    sources=authenticate()
    kernel_receipt()
    sys.path.insert(0,str(ROOT/'research/refit-proof-closure'))
    from sparse_router import SparseWord,compact
    result=dict(status='PASS_COMPACT_GUARD_SOURCE_SEAMS',sources=sources,
                exhaustive=exhaustive(SparseWord,compact),packed=packed_cases(SparseWord,compact),
                counterexamples=counterexamples(SparseWord,compact),
                scope='Finite binding of the retained sparse word to the quantified guard and repair proof. No new tape execution or full multiplier formalization.')
    # Normalize tuples before the complete JSON receipt comparison.
    result=json.loads(json.dumps(result))
    encoded=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--emit' in sys.argv:
        need(not (HERE/'RESULT.json').exists(),'refuse to overwrite frozen receipt')
        (HERE/'RESULT.json').write_text(encoded)
    else:need(result==json.loads((HERE/'RESULT.json').read_text()),'complete receipt equality')
    print(encoded,end='')


if __name__=='__main__':main()
