"""Current native word lowered to a closed primitive alphabet.

The dense dyadic executor is an exact reference, not a tape-machine simulator.
Permanent-role/tape refinement and its cost are specified in PROOF.md.
Apache-2.0; prepared for Thomas DiFiore with OpenAI Codex assistance.
"""
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/recursive-refit-realization'))
from common import inputs, need, canonical, module


def source(data, provider, name):
    return data['base/providers/'+provider+'/'+name]


def compile_native(data, provider, direction):
    recipes = source(data, provider, 'CLIFFORD-RECIPES.json')
    directed = {(x['old'], x['new']):x for x in recipes['children']}
    warps = {(x['sign'], x['op'], x['old'], x['new']):x for x in recipes['warps']}
    endpoints = {(x['role'], x['port']):x for x in recipes['endpoint_adapters']}
    wrappers = source(data, provider, 'RESIDUAL-ADAPTERS.json')['recipes']
    word = source(data, provider, 'LOCAL-PROGRAMS.json.gz')[direction]
    out = []
    def mono(pc, role, recipe, inverse=False):
        need(recipe is not None, 'actual monomial recipe')
        out.append((pc, 'monomial', tuple(role), canonical(recipe).decode(), inverse))
    for pc, e in enumerate(word):
        tag = e[0]
        if tag == 'phase':out.append((pc, 'marker', e[1]))
        elif tag == 'scalar':
            op=e[1];kind=op[0];target=tuple(op[1])
            if kind in ('copy','add'):
                out.append((pc,kind,target,tuple(op[2]),*op[3:]))
            else:
                need(kind in ('clear','scale'),'closed scalar alphabet')
                out.append((pc,kind,target,*op[2:]))
        elif tag == 'zero_buffer':
            need(e[1] in ('alloc','free'),'private lifecycle')
            out.append((pc,e[1],('Z',e[2])))
        elif tag == 'warp':
            _,role,op,old,new=e
            r=warps[(1 if op>0 else -1,abs(op),old,new)]
            need(r['rank']==0 and r['right'] is None,'rank-zero warp')
            mono(pc,role,r['left'])
        elif tag in ('climb','center'):
            old,new,rank=e[-3:];r=directed[old,new]
            need(r['rank']==rank and 0<rank<73,'proper child')
            role=('L',e[2]) if tag=='climb' else ('C',e[1])
            mono(pc,role,r['right'])
            out.append((pc,'child',role,rank))
            mono(pc,role,r['left'])
        elif tag == 'adapter':
            _,direction,role,frame=e
            need(direction in ('old_to_new','new_to_old'),'endpoint orientation')
            if frame in (0,1):out.append((pc,'identity',('L',role)))
            else:
                key=('source',role) if role<112 else ('target',role-112)
                r=endpoints[key];need(r['frame']==frame,'endpoint frame')
                mono(pc,('L',role),r['left'],direction=='new_to_old')
        elif tag == 'residual_adapter':
            _,way,role,entrance,*terminal=e
            key=f'{entrance}:{terminal[0]}' if terminal else str(entrance)
            need(way in ('pre','post'),'wrapper orientation')
            mono(pc,('L',role),wrappers[key]['right' if way=='pre' else 'left'],True)
        else:raise ValueError('unlowered native event '+str(e))
    need(set(x[0] for x in out)==set(range(len(word))),'every actual event lowered')
    return tuple(out)


@dataclass(frozen=True)
class Vec:
    """Gaussian integers divided by 2**exponent; no floating point or rounding."""
    real: tuple
    imag: tuple
    exponent: int = 0

    @classmethod
    def make(cls, real, imag, exponent=0):
        real,imag=tuple(real),tuple(imag)
        need(len(real)==len(imag),'paired components')
        bits=0
        for v in real+imag:bits |= abs(v)
        if not bits:return cls((0,)*len(real),(0,)*len(real),0)
        shift=min(exponent,(bits & -bits).bit_length()-1)
        return cls(tuple(v>>shift for v in real),tuple(v>>shift for v in imag),exponent-shift)

    def scale(self, num, den):
        coefficient=Fraction(num,den);num,den=coefficient.numerator,coefficient.denominator
        need(den>0 and den & (den-1)==0,'dyadic scalar')
        return Vec.make((num*x for x in self.real),(num*x for x in self.imag),
                        self.exponent+den.bit_length()-1)

    def add(self, other, num=1, den=1):
        other=other.scale(num,den);exponent=max(self.exponent,other.exponent)
        a=exponent-self.exponent;b=exponent-other.exponent
        return Vec.make(((x<<a)+(y<<b) for x,y in zip(self.real,other.real,strict=True)),
                        ((x<<a)+(y<<b) for x,y in zip(self.imag,other.imag,strict=True)),exponent)

    def c(self, mask, sign=1):
        need(0<mask<len(self.real) and sign in (-1,1),'elementary C domain')
        r,i=self.real,self.imag
        return Vec.make((r[x]-sign*i[x]+r[x^mask]+sign*i[x^mask] for x in range(len(r))),
                        (i[x]+sign*r[x]+i[x^mask]-sign*r[x^mask] for x in range(len(r))),
                        self.exponent+1)

    def monomial(self, text, inverse=False):
        mapping,phases=monomial_table(text)
        r=[0]*len(self.real);i=[0]*len(r)
        for x,y in enumerate(mapping):
            src,dst=(y,x) if inverse else (x,y)
            phase=(-phases[x] if inverse else phases[x])%4
            a,b=self.real[src],self.imag[src]
            r[dst],i[dst]=((a,b),(-b,a),(-a,-b),(b,-a))[phase]
        return Vec(tuple(r),tuple(i),self.exponent)

    def digest(self):return sha256(canonical([self.real,self.imag,self.exponent])).hexdigest()


@lru_cache(maxsize=None)
def monomial_table(text):
    recipe=json.loads(text);n=len(recipe['matrix_rows']);mapping=[];phases=[]
    for x in range(1<<n):
        mapping.append(recipe['offset']^sum(((v&x).bit_count()%2)<<i for i,v in enumerate(recipe['matrix_rows'])))
        phase=recipe['phase']+sum(a for i,a in enumerate(recipe['linear_Z4']) if x>>i&1)
        phase+=2*sum(((q>>(i+1))&(x>>(i+1))).bit_count() for i,q in enumerate(recipe['quadratic_rows']) if x>>i&1)
        phases.append(phase%4)
    need(len(set(mapping))==len(mapping),'bijection')
    return tuple(mapping),tuple(phases)


def execute(program, live, *, omit=None):
    roles={('L',i):v for i,v in enumerate(live)}
    zero=Vec.make((0,)*512,(0,)*512);allocated=set();children=Counter()
    maximum_denominator=maximum_numerator=0;events=Counter()
    for step,op in enumerate(program):
        pc,kind,*args=op
        if omit is not None and step==omit:continue
        events[kind]+=1
        if kind in ('marker','identity'):continue
        role=args[0]
        if kind=='alloc':
            need(role not in roles and role not in allocated,'unique zero allocation')
            roles[role]=zero;allocated.add(role)
        elif kind=='free':
            need(roles[role]==zero,'zero buffer returned to zero')
            del roles[role]
        elif kind=='clear':roles[role]=zero
        elif kind=='copy':roles[role]=roles[args[1]]
        elif kind=='scale':roles[role]=roles[role].scale(*args[1:])
        elif kind=='add':roles[role]=roles[role].add(roles[args[1]],*args[2:])
        elif kind=='monomial':roles[role]=roles[role].monomial(*args[1:])
        elif kind=='child':
            need(not any(r[0]=='Z' for r in roles),'child only outside zero-buffer cleanup')
            rank=args[1];children[rank]+=1
            for axis in range(rank):roles[role]=roles[role].c(1<<axis)
        else:raise ValueError('unknown primitive')
        if role in roles:
            z=roles[role];maximum_denominator=max(maximum_denominator,z.exponent)
            maximum_numerator=max(maximum_numerator,max((abs(x).bit_length() for x in z.real+z.imag),default=0))
    need(len(allocated)==82 and not any(r[0]=='Z' for r in roles),'all actual private Z lifecycles')
    need(all(roles.get(('C',i))==zero for i in range(8)),'eight centres cleared')
    return [roles['L',i] for i in range(632)],dict(children=dict(sorted(children.items())),
           primitives=dict(sorted(events.items())),maximum_denominator=maximum_denominator,
           maximum_numerator=maximum_numerator,private_zero_buffers=82,cleared_centres=8)


def fixture(seed=0):
    return [Vec.make(((37*x+19*j+11*x*j+seed)%127-63 for x in range(512)),
                     ((13*x*x+29*j+7*x*j+3*seed)%131-65 for x in range(512))) for j in range(632)]


def reference(data,provider,direction,live):
    """Whole-word endpoint using the original convolution kernels alone.

    No directed, warp, wrapper or endpoint adapter recipe is used here.
    The input source label is C_q; the output target label is C_all C_q^-1.
    """
    c=source(data,provider,'CANONICAL-WORD.json.gz')
    def full(value):
        for axis in range(9):value=value.c(1<<axis)
        return value
    out=list(live)
    for port in range(112):
        q=c['ports'][port];a=live[port].c(q,-1)
        b=live[112+port]
        if direction=='forward':b=b.add(a)
        else:a=a.add(b,-1,1)
        out[port]=full(a)
        out[112+port]=full(b.c(q,-1))
    for role in range(224,632):
        rank=len(c['frames'][c['final'][role]])-len(c['frames'][c['start'][role]])
        for axis in range(rank):out[role]=out[role].c(1<<axis)
    return out
