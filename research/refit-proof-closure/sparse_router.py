"""Unequal-gap support shear using the retained sequential compact interpreter.

The algebra and support construction are credited to PR1673. This connects
its sparse target/source lists to the already joined PR2250 / PR2899 seam.
Upper descriptors remain mathematical integers; their tape cost is discussed
in ROUTER.md, not inferred from Python time or from the reduced payload test.
"""
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/recursive-refit-realization'))
from common import need, module

directory=ROOT/'research/selected-complex-compact-adapters'
sys.path.insert(0,str(directory))
streams=module('streams',directory/'streams.py')
compact=module('compact',directory/'compact.py')


@dataclass(frozen=True)
class SparseWord:
    targets: tuple
    sources: tuple
    K: int
    G: int
    target: str='y'
    source: str='y'
    late: bool=True

    @property
    def n(self):return len(self.targets)

    def validate(self,layout):
        need(self.n>0 and len(self.sources)==self.n,'nonempty paired sparse lists')
        need(self.G>=1 and self.K>=1,'positive digit and guard widths')
        need(tuple(sorted(self.targets))==self.targets and len(set(self.targets))==self.n,
             'ordered distinct targets')
        need(all(a+self.K<=b for a,b in zip(self.targets,self.targets[1:])),
             'disjoint target guards')
        need(self.targets[0]>=0 and self.targets[-1]+self.K<=layout.width('y'),
             'all target guards inside field')
        need(len(set(self.sources))==self.n and not set(self.sources)&set(self.targets)
             and all(0<=s<layout.width('y') for s in self.sources),
             'distinct sources outside target set')
        need(layout.names==('u','t','y','b') and layout.width('u')>=self.n*self.G
             and all(layout.width(z)==layout.width('u') for z in ('t','b')),
             'complete preceding controls and following shuttle')

    def operations(self):
        return compact.Compact.operations(self)

    def packed(self,value,positions):
        return sum(((value>>j)&1)<<(i*self.G) for i,j in enumerate(positions))

    def offset(self,state,op):
        _,target,controls,kind,sign=op
        if kind=='selected_x':return sign*self.packed(state['y'],self.sources)
        if kind=='selected_y':return sign*self.packed(state['y'],self.targets)
        bits=[(state['u']>>(i*self.G))&1 for i in range(self.n)]
        if kind.startswith('original'):
            recovered=state['y']^sum(z<<j for z,j in zip(bits,self.targets))
            return sign*self.packed(recovered,self.targets)
        B=1<<self.G
        return sign*sum(z*(2*((state['t']>>(i*self.G))&(B-1)) if kind.startswith('first')
                           else 1-2*((state['t']>>(i*self.G))&(B-1)))<<j
                        for i,(z,j) in enumerate(zip(bits,self.targets)))

    def execute(self,state,layout,inverse=False):
        return compact.Compact.execute(self,state,layout,inverse)

    def ideal(self,state):
        out=dict(state)
        out['y']^=sum(((state['y']>>s)&1)<<j for s,j in zip(self.sources,self.targets))
        return out

    def bad(self,state):
        B=1<<self.G;mask=(1<<(self.K-1))-1
        return any(((state['u']>>(i*self.G))&(B-1))==B-1
                   or ((state['t']>>(i*self.G))&(B-1))==B-1
                   or not 2*B<=((state['y']>>(j+1))&mask)<(1<<(self.K-1))-2*B
                   for i,j in enumerate(self.targets))


def execute(source,layout,word,wrong_inverse=False,omit_repair=False):
    word.validate(layout)
    need(len(source.data)==layout.records*layout.record_bits,'complete sparse-router stream')
    for op in word.operations():
        source=(compact.ordinary(source,layout,op[1],op[2]) if op[0]=='swap'
                else compact.rotate(source,layout,word,op))
    if not omit_repair:source=compact.repair(source,layout,word,wrong_inverse)
    need(source.head==0,'completed sparse output origin')
    return source


def algebra():
    cases=[]
    for targets,sources,K,G,width,capacity in [((0,),(2,),5,1,5,1),
            ((0,),(2,),5,1,5,2),((0,6),(2,8),5,1,11,2)]:
        word=SparseWord(targets,sources,K,G)
        layout=compact.Layout((('u',capacity*G),('t',capacity*G),('y',width),('b',capacity*G)),1)
        word.validate(layout);good=bad=changed=0
        seen=bytearray(layout.records)
        for index in range(layout.records):
            state=layout.decode(index);raw=word.execute(state,layout)
            need(word.execute(raw,layout,True)==state,'raw inverse uses current controls')
            need(word.bad(raw)==word.bad(state),'raw word preserves exceptional set')
            if word.bad(state):bad+=1
            else:
                good+=1;need(raw==word.ideal(state),'guarded sparse word is simultaneous shear')
            corrected=word.ideal(word.execute(raw,layout,True))
            dest=layout.encode(corrected)
            need(not seen[dest],'corrected keys are injective');seen[dest]=1
            changed+=raw!=corrected
        need(good>0 and bad>0 and changed>0 and all(seen),'nonvacuous good, bad and repair coverage')
        cases.append(dict(targets=targets,sources=sources,capacity=capacity,addresses=layout.records,
                          good=good,bad=bad,raw_errors=changed))
    return cases


def physical():
    from common import ordinary_sources
    ordinary_sources()
    from compact_bridge import CompactBinary
    from binary import Binary
    from check_engine import fixture_engine
    from encoded import Profile
    from check_support import no_decode
    from physical_words import PhysicalWord
    from words import Word
    from unittest.mock import patch
    native=fixture_engine();native.profile=Profile(numerator=173,denominator=100000)
    bridge=CompactBinary(Binary(native),compact,streams)
    word=SparseWord((0,),(2,),5,1)
    layout=compact.Layout((('u',1),('t',1),('y',5),('b',1)),8)
    raw=bytes(bit for i in range(layout.records) for bit in streams.bit_key(i,8))
    expected=bytearray(len(raw))
    for i in range(layout.records):
        dest=layout.encode(word.ideal(layout.decode(i)))
        expected[8*dest:8*dest+8]=raw[8*i:8*i+8]
    def forbidden(*args,**kwargs):raise ValueError('forbidden binary numerical decoder')
    meter=streams.Meter()
    with bridge.installed(),no_decode(),patch.object(Word,'__init__',forbidden),patch.object(PhysicalWord,'inspect',forbidden):
        result=execute(streams.Tape(meter,raw),layout,word)
    need(result.data==expected,'actual sparse/compact/B1 payload endpoint')
    need(len(bridge.calls)==12,'complete late-source shuttle calls')
    bridge.close()
    return dict(records=layout.records,payload_bits=len(raw),ordinary_calls=len(bridge.calls),
                source_inside_guard=True,work_erased=True,
                scope='Reduced actual B1 payload fixture; all calls use its elementary branch. Upper descriptor costs require the written refinement proof.')


def unequal_gaps():
    import random
    rng=random.Random(2745)
    word=SparseWord((0,10,23),(2,12,25),8,3)
    layout=compact.Layout((('u',12),('t',12),('y',31),('b',12)),1)
    word.validate(layout)
    good=bad=changed=0
    for sample in range(4000):
        state={name:rng.randrange(1<<layout.width(name)) for name in layout.names}
        if sample>=2000:
            for name in ('u','t'):
                state[name]=sum(rng.randrange(7)<<(3*i) for i in range(3)) | (rng.randrange(8)<<9)
            for j in word.targets:
                state['y']&=~(((1<<8)-1)<<j)
                state['y']|=(rng.randrange(2)|(rng.randrange(16,112)<<1))<<j
            need(not word.bad(state),'constructed nonbinary compact digits are good')
        raw=word.execute(state,layout)
        need(word.execute(raw,layout,True)==state,'unequal-gap raw inverse')
        need(word.bad(raw)==word.bad(state),'unequal-gap bad-set invariance')
        if word.bad(state):bad+=1
        else:
            good+=1;need(raw==word.ideal(state),'unequal-gap good endpoint')
        changed+=raw!=word.ideal(state)
    need(good>=2000 and bad>0 and changed>0,'nonvacuous unequal-gap checks')
    return dict(targets=word.targets,sources=word.sources,K=8,G=3,capacity=4,
                addresses=4000,good=good,bad=bad,raw_errors=changed,
                scope='Deterministic sampled and constructed-good states, not exhaustive; gaps 10 and 13, nonbinary dirty digits and inactive high digits.')


def controls():
    word=SparseWord((0,),(2,),5,1)
    layout=compact.Layout((('u',1),('t',1),('y',5),('b',1)),8)
    raw=bytes(bit for i in range(layout.records) for bit in streams.bit_key(i,8))
    expected=bytearray(len(raw))
    for i in range(layout.records):
        dest=layout.encode(word.ideal(layout.decode(i)))
        expected[8*dest:8*dest+8]=raw[8*i:8*i+8]
    rejected=[]
    for name,kwargs in [('omit_repair',{'omit_repair':True}),
                        ('wrong_inverse_current_controls',{'wrong_inverse':True})]:
        result=execute(streams.Tape(streams.Meter(),raw),layout,word,**kwargs)
        need(result.data!=expected,'mutated sparse endpoint must fail: '+name)
        rejected.append(name)
    for name,bad in [('source_is_target',SparseWord((0,),(0,),5,1)),
                     ('guard_outside_field',SparseWord((2,),(0,),5,1))]:
        try:bad.validate(layout)
        except ValueError:rejected.append(name)
        else:raise ValueError('malformed sparse call accepted: '+name)
    return rejected


if __name__=='__main__':
    import json
    print(json.dumps({'algebra':algebra(),'unequal_gaps':unequal_gaps(),
                      'physical':physical(),'rejecting_controls':controls()},indent=2))
    print('PASS_SPARSE_ROUTER_JOIN')
