"""Exact finite assembly seams, not a verification of the whole machine.

Thomas DiFiore, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import prod
from pathlib import Path
import argparse
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok: raise ValueError(message)

def digest(x):return sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()
def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(x) for x in zip(*a)]
def add(a,b,c=1):return [[x+c*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,c):return [[c*x for x in r] for r in a]
def mul(a,b):return [[sum((x*y for x,y in zip(r,s) if x and y),Q(0)) for s in zip(*b)] for r in a]
def section(a,rows,cols=None):return [[a[i][j] for j in (rows if cols is None else cols)] for i in rows]
def norm(a):return max(sum(abs(x) for x in r) for r in a)

def inverse(a):
    n=len(a);w=[r[:]+u for r,u in zip(a,eye(n))]
    for k in range(n):
        pivot=next((i for i in range(k,n) if w[i][k]),None)
        need(pivot is not None,'invertible exact test matrix')
        w[k],w[pivot]=w[pivot],w[k];d=w[k][k];w[k]=[x/d for x in w[k]]
        for i in range(n):
            if i!=k and w[i][k]:
                c=w[i][k];w[i]=[x-c*y for x,y in zip(w[i],w[k])]
    return [r[n:] for r in w]

def schur(a,keep,eliminated):
    if not eliminated:return section(a,keep)
    return add(section(a,keep),mul(mul(section(a,keep,eliminated),inverse(section(a,eliminated))),section(a,eliminated,keep)),-1)

def polynomial(h,count):
    gamma=Q(1,16);ht=transpose(h);q=add(eye(len(h)),mul(ht,h),-gamma)
    power=eye(len(h));total=scale(power,0)
    for _ in range(count):total=add(total,power);power=mul(power,q)
    p=scale(mul(total,ht),gamma)
    need(mul(p,h)==add(eye(len(h)),power,-1),'noncommuting residual order')
    return p,q

def nonstationary(n,phase):
    h=scale(eye(n),0)
    for i in range(n):
        h[i][i]=Q(2)+Q((i+phase)%3,16)
        h[i][(i+1)%n]=Q(1+(i+phase)%2,16)
        h[i][(i-1)%n]=-Q(1+(i+phase)%3,32)
    return h

def apply_axis(data,axis,inputs,outputs,matrix):
    others=sorted({x[:axis]+x[axis+1:] for x in data});out={}
    for other in others:
        values=[data[other[:axis]+(j,)+other[axis:]] for j in inputs]
        for i,row in zip(outputs,matrix):
            out[other[:axis]+(i,)+other[axis:]]=sum((c*x for c,x in zip(row,values) if c),Q(0))
    return out

def face_cases():
    receipts=[];rejected=set()
    for periods,side,count in [((16,24),8,1),((32,48),16,2)]:
        radius=2*count-1;hs=[nonstationary(n,i) for i,n in enumerate(periods)]
        ps=[polynomial(h,count)[0] for h in hs]
        data={x:Q((x[0]*13+x[1]*7+x[0]*x[1])%29-14,16) for x in product(*(range(n) for n in periods))}
        oracle=data
        for i,n in enumerate(periods):oracle=apply_axis(oracle,i,range(n),range(n),ps[i])
        assembled={};copied=0;face_outputs=0;bad_recycled=False;bad_constant=False;bad_wrap=False;cache={}
        def local(axis,indices,constant=False):
            key=(axis,tuple(indices),constant)
            if key not in cache:
                h=hs[axis];n=periods[axis]
                small=[[h[0][(j-i)%n] if constant else h[i%n][j%n] for j in indices] for i in indices]
                cache[key]=polynomial(small,count)[0]
            return cache[key]
        def process(rect,outrect,original,constant=False):
            current=original
            for axis,(indices,outputs) in enumerate(zip(rect,outrect)):
                full=local(axis,indices,constant)
                current=apply_axis(current,axis,indices,outputs,[full[indices.index(j)] for j in outputs])
            return current
        for origin in product(*(range(0,n,side) for n in periods)):
            core=[list(range(o,o+side)) for o in origin]
            block={x:data[x] for x in product(*core)};dense=process(core,core,block)
            for x in product(*(range(o+radius,o+side-radius) for o in origin)):
                need(dense[x]==oracle[x] and x not in assembled,'deep finite-core polynomial equals global')
                assembled[x]=dense[x]
            for first in range(2):
                for high in (False,True):
                    rect=[];outrect=[]
                    for axis,o in enumerate(origin):
                        if axis<first:
                            rect.append(list(range(o,o+side)));outrect.append(list(range(o+radius,o+side-radius)))
                        elif axis==first:
                            rect.append(list(range(o+side-2*radius,o+side+radius)) if high else list(range(o-radius,o+2*radius)))
                            outrect.append(list(range(o+side-radius,o+side)) if high else list(range(o,o+radius)))
                        else:
                            rect.append(list(range(o-radius,o+side+radius)));outrect.append(list(range(o,o+side)))
                    raw={x:data[tuple(j%n for j,n in zip(x,periods))] for x in product(*rect)}
                    result=process(rect,outrect,raw);copied+=len(raw);face_outputs+=len(result)
                    for x,y in result.items():
                        need(x not in assembled and y==oracle[x],'disjoint variable-coefficient wrapped faces')
                        assembled[x]=y
                    if not bad_recycled:bad_recycled=process(rect,outrect,{x:dense.get(x,raw[x]) for x in raw})!=result
                    if not bad_constant:bad_constant=process(rect,outrect,raw,True)!=result
                    if not bad_wrap:
                        clipped={x:raw[x] if all(0<=j<n for j,n in zip(x,periods)) else Q(0) for x in raw}
                        bad_wrap=process(rect,outrect,clipped)!=result
        need(assembled==oracle,'complete corrected tensor polynomial')
        need(copied==3*prod(n//side for n in periods)*((side+2*radius)**2-side**2),'exact corner duplication')
        need(bad_recycled and bad_constant and bad_wrap,'all face mutations have witnesses')
        rejected.update(['recycle_dense_edge_values','replace_varying_coefficients_by_constant_stencil','drop_periodic_halo_inputs'])
        bounds=[]
        for axis,n in enumerate(periods):
            h=hs[axis];hi=inverse(h);qn=norm(polynomial(h,count)[1]);need(qn<1,'exact contraction in fixture')
            for o in range(0,n,side):
                hc=section(h,range(o,o+side));ci=inverse(hc);pc,qc=polynomial(hc,count)
                bound=qn**count*norm(hi)+norm(qc)**count*norm(ci)
                error=max(sum(abs(hi[o+i][j]-(ci[i][j-o] if o<=j<o+side else 0)) for j in range(n)) for i in range(radius,side-radius))
                need(error<=bound,'core inverse comparison from two residual bounds')
                need(all(pc[i]==ps[axis][o+i][o:o+side] for i in range(radius,side-radius)),'same local polynomial')
                bounds.append(dict(axis=axis,origin=o,error=str(error),bound=str(bound)))
        receipts.append(dict(periods=periods,side=side,iterations=count,radius=radius,outputs=len(oracle),face_outputs=face_outputs,copies=copied,output_sha256=digest(sorted(oracle.items())),inverse_comparisons=bounds))
    return dict(cases=receipts,rejection_controls=sorted(rejected))

def separator_cases():
    receipts=[];cut_witness=False
    for lengths in [(2,4,3,5,2,4,2),(3,5,2,4,3)]:
        groups=[];interiors=[];cursor=0
        for k,length in enumerate(lengths):
            (groups if k%2==0 else interiors).append(list(range(cursor,cursor+length)));cursor+=length
        n=cursor;h=[[Q(2+i%3,2) if i==j else Q(1+(i+2*j)%3,64) if 0<abs(i-j)<=2 else Q(0) for j in range(n)] for i in range(n)]
        boundary=sum(groups,[]);eliminated=sum(interiors,[]);s=schur(h,boundary,eliminated);checked=0
        for k,group in enumerate(groups):
            keep=sum(groups[:k+1],[]);end=interiors[k][-1]+1 if k<len(interiors) else n
            prefix=schur(h,keep,[i for i in eliminated if i<end])
            need(prefix==section(s,range(len(keep))),'whole-group prefix Schur identity')
            need(inverse(prefix)==section(inverse(section(h,range(end))),keep),'inverse Schur block identity')
            checked+=len(keep)**2
            if k<len(interiors) and len(group)>=2:
                partial=keep[:-1];wrong=schur(h,partial,[i for i in eliminated if i<partial[-1]+1])
                cut_witness|=section(s,range(len(partial)))!=wrong
        a=section(h,eliminated);b=section(h,eliminated,boundary);c=section(h,boundary,eliminated);ai=inverse(a)
        rhs=[[Q((i*7+j*3)%17-8,8) for j in range(4)] for i in range(n)]
        x=section(rhs,eliminated,range(4));y=section(rhs,boundary,range(4))
        x=mul(ai,x);y=add(y,mul(c,x),-1);y=mul(inverse(s),y);x=mul(a,x);x=add(x,mul(b,y),-1);x=mul(ai,x)
        answer=[None]*n
        for indices,values in ((eliminated,x),(boundary,y)):
            for i,value in zip(indices,values):answer[i]=value
        need(answer==mul(inverse(h),rhs),'six-stage inverse with dirty inputs')
        receipts.append(dict(lengths=lengths,checked_entries=checked,matrix_sha256=digest(h),output_sha256=digest(answer)))
    need(cut_witness,'cutting a separator invalidates prefix identification')
    return dict(cases=receipts,rejection_controls=['cut_separator_and_drop_adjacent_interior'])

def strassen(a,b):
    n=len(a)
    if n==1:return [[a[0][0]*b[0][0]]]
    m=n//2;lo=range(m);hi=range(m,n);blocks=((lo,lo),(lo,hi),(hi,lo),(hi,hi))
    aa,ab,ac,ad=[section(a,r,c) for r,c in blocks];ba,bb,bc,bd=[section(b,r,c) for r,c in blocks]
    p1=strassen(add(aa,ad),add(ba,bd));p2=strassen(add(ac,ad),ba);p3=strassen(aa,add(bb,bd,-1));p4=strassen(ad,add(bc,ba,-1));p5=strassen(add(aa,ab),bd);p6=strassen(add(ac,aa,-1),add(ba,bb));p7=strassen(add(ab,ad,-1),add(bc,bd))
    cc=[add(add(add(p1,p4),p5,-1),p7),add(p3,p5),add(p2,p4),add(add(add(p1,p2,-1),p3),p6)]
    return [cc[0][i]+cc[1][i] for i in range(m)]+[cc[2][i]+cc[3][i] for i in range(m)]

def algebra_and_precision():
    entries=0;identities=0
    for n in (1,2,4,8):
        a=[[Q((i*3-j*5)%13-6,8) for j in range(n)] for i in range(n)];b=[[Q((i*7+j*2)%11-5,4) for j in range(n)] for i in range(n)]
        need(strassen(a,b)==mul(a,b),'explicit seven-product circuit');entries+=n*n
    need(7**16<2**45,'strict Strassen exponent')
    for theta in (Q(1,4),Q(1,16),Q(1,64)):
        rho=1+theta;lam=1/rho
        for delta,x,y in product((Q(-1,2),Q(1,3),Q(1,2)),(Q(-3,2),Q(0),Q(5,2)),(Q(-2),Q(1),Q(3))):
            shift=-delta*(1-theta)
            left=(x-lam*y+delta)**2-lam*(x-y-shift)**2
            right=(1-lam)*x*x-lam*(1-lam)*y*y+delta*delta-lam*shift*shift+2*(delta+lam*shift)*x-2*lam*(delta+shift)*y
            need(left==right and 1-2*abs(shift)>=theta,'broad identity and strict shift gap')
            h=y-x;bi=delta+theta*x;bj=delta+theta*y
            need((rho*h+bi)**2-bj**2==rho*h*h+2*delta*h-theta*(x*x-y*y),'narrow chirp identity');identities+=1
    cases=[]
    for p in (8,16,32):
        c=8;weight=Q(3,1<<(p*p+2));old_bits=c*p;setup=c*p+64*p*p*(p-1).bit_length()
        old=weight*(1<<old_bits);old_int=old.numerator//old.denominator
        new=weight*(1<<setup);new=Q(new.numerator//new.denominator,1<<setup)
        need(new>0 and abs(new/weight-1)<=Q(1,1<<(c*p)),'positive relative setup weights')
        if p>c:need(old_int==0,'Cp absolute rounding underflows')
        cases.append(dict(p=p,old_bits=old_bits,setup_bits=setup,old_zero=old_int==0))
    return dict(strassen_entries=entries,exact_shift_identities=identities,underflow_cases=cases,rejection_controls=['Cp_only_absolute_cell_weights'])

class Cyclotomic:
    def __init__(self,s,module):
        self.s=s;self.modulus=module.cyclotomic(s);self.degree=len(self.modulus)-1
        self.reduce=lambda a:tuple(Q(x) for x in module.reduce_poly(a,self.modulus))
        self.roots=[self.reduce([0]*k+[1]) for k in range(s)];self.zero=(Q(0),)*self.degree
    def scalar(self,x):return (Q(x),)+(Q(0),)*(self.degree-1)
    def add(self,a,b):return tuple(x+y for x,y in zip(a,b))
    def scale(self,a,x):return tuple(y*x for y in a)
    def multiply(self,a,b):
        out=[Q(0)]*(2*self.degree-1)
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b):
                    if y:out[i+j]+=x*y
        return self.reduce(out)
    def root_times(self,a,e):return self.multiply(a,self.roots[e%self.s])

def recovery_cases():
    prior=ROOT/'research/refit-proof-closure';sys.path.insert(0,str(prior))
    spec=importlib.util.spec_from_file_location('retained_exact_fourier',prior/'check_crt.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    receipts=[];rejected=set()
    for moduli,units in [((3,5),(4,8)),((3,7),(4,8))]:
        crt=old.TriangularCRT(moduli);s=prod(moduli);ring=Cyclotomic(s,old);addresses=list(product(*(range(m) for m in moduli)))
        def transform(values,sign):
            out={}
            for k in addresses:
                total=ring.zero
                for j in addresses:
                    exponent=sign*sum(t*x*y*(s//m) for t,x,y,m in zip(units,k,j,moduli))
                    total=ring.add(total,ring.root_times(values[j],exponent))
                out[k]=ring.scale(total,Q(1,s))
            return out
        def digits(k):return tuple((k//p)%m for p,m in zip(crt.prefix,moduli))
        for bits in ((4,6) if s<16 else (5,6)):
            need(s<1<<bits,'recovery fixture obeys S < 2^b')
            e=Q(1,1<<(10*bits));a=[(3*i+5)%(1<<bits) for i in range(4)];b=[(7*i+1)%(1<<bits) for i in range(4)]
            true=[sum(a[i]*b[k-i] for i in range(4) if 0<=k-i<4) for k in range(s)];si=Q(1,1<<(bits+2))
            ea={crt.execute(digits(k)):ring.scalar((a[k] if k<4 else 0)*si) for k in range(s)}
            eb={crt.execute(digits(k)):ring.scalar((b[k] if k<4 else 0)*si) for k in range(s)}
            for noisy in (False,True):
                aa={j:ring.add(v,ring.scalar(e*((j[0]+j[1])%3-1) if noisy else 0)) for j,v in ea.items()}
                bb={j:ring.add(v,ring.scalar(-e if noisy else 0)) for j,v in eb.items()}
                fa=transform(aa,-1);fb=transform(bb,-1)
                if noisy:
                    fa={j:ring.add(v,ring.scalar(e)) for j,v in fa.items()};fb={j:ring.add(v,ring.scalar(-e)) for j,v in fb.items()}
                point={j:ring.add(ring.multiply(fa[j],fb[j]),ring.scalar(e if noisy else 0)) for j in addresses}
                result=transform(point,1)
                if noisy:result={j:ring.add(v,ring.scalar(e)) for j,v in result.items()}
                w={j:ring.scale(v,s) for j,v in result.items()};ordinary=[]
                for k in range(s):
                    v=ring.add(w[crt.execute(digits(k))],ring.scalar(e if noisy else 0))
                    need(not any(v[1:]),'three labelled transforms cancel to rational output');ordinary.append(v[0])
                final=[x*(1<<(2*bits+4))*s for x in ordinary];error=max(abs(x-y) for x,y in zip(final,true))
                need(error<=80*Q(1,1<<(6*bits))<Q(1,4),'explicit full recovery bound')
                rounded=[(x+Q(1,2)).numerator//(x+Q(1,2)).denominator for x in final]
                need(rounded==true,'unique integer recovery')
                need(sum(x<<(bits*i) for i,x in enumerate(rounded))==sum(x<<(bits*i) for i,x in enumerate(a))*sum(x<<(bits*i) for i,x in enumerate(b)),'exact radix carry value')
                if not noisy:
                    need(any(x/s!=y for x,y in zip(final,true)),'omitting either S changes result')
                    need(all(abs(x)<Q(1,2) for x in ordinary) and any(true),'rounding bounded values early loses product')
                    rejected.update(['omit_first_S','omit_second_S','round_before_inverse_CRT_and_final_scale'])
                receipts.append(dict(moduli=moduli,frequency_units=units,bits=bits,noisy=noisy,coefficients=s,max_error=str(error),output_sha256=digest(rounded)))
    for d in (2,4,8,16,32,64):
        for width in (1<<k for k in range(1,d.bit_length())):
            targets=sum(min(d,lo+width)-min(d,lo+width//2) for lo in range(0,d,width))
            need(targets==d//2,'balanced CRT level retains d/2 targets')
    return dict(cases=receipts,rejection_controls=sorted(rejected))

def ledger():
    row=json.loads((ROOT/'research/paired-terminal-refit/evidence/OUTER-LEDGER.json').read_text())['rows']['struct_boundary_radix_union']
    eps,beta,xi,q,a,kappa=[Q(row[k]['rational']) for k in ('epsilon','beta','xi','q','a','kappa')]
    powers={'main':1-eps*q,'global_router':1-a,'dense_gaussian':eps-q*beta,'group_router':eps-a*beta,'group_scan':eps-beta,'boundary':eps-xi+Q(29,32),'union':eps+Q(1,2)-xi,'polynomial_products':1-eps,'direct_faces':eps+beta-30}
    margins={k:1-kappa-v for k,v in powers.items()};need(all(x>0 for x in margins.values()),'all constructed costs below target')
    need(Q(1,2)<xi<eps<1 and beta<eps and beta+2*(1-eps)<1 and beta+2*xi-2<1,'cap, guard, membership and spectator conditions')
    need(Q(17270071,10**10)>a>q>kappa and powers['direct_faces']<-28,'primitive savings and explicit face cost')
    return dict(powers={k:str(v) for k,v in powers.items()},margins={k:str(v) for k,v in margins.items()},rho=str(min(margins.values())/2),kappa=str(kappa),scope='Exact consequences of algorithmic rows; not proofs of the algorithms.')

def authenticate():
    count=0
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'changed input '+item['path']);count+=1
    refs=json.loads((HERE/'REFERENCES.json').read_text());raw=(HERE/'evidence/RETAINED-SOURCE-MANIFEST.json').read_bytes()
    claim=json.loads((ROOT/'research/paired-terminal-refit/CLAIM.json').read_text())
    need(sha256(raw).hexdigest()==refs['source_manifest_sha256']==claim['source_manifest_sha256'],'authenticated export manifest')
    manifest=json.loads(raw)
    for item in refs['files']:need(sha256((HERE/item['local_path']).read_bytes()).hexdigest()==item['sha256']==manifest[item['source_path']],'unchanged reference member')
    return dict(inputs=count,reference_files=len(refs['files']),source_manifest=refs['source_manifest_sha256'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',type=Path);args=parser.parse_args()
    inputs=authenticate()
    result=dict(status='PASS_EXACT_OUTER_ASSEMBLY_SEAMS',inputs=inputs,cores_and_faces=face_cases(),separator_pivots=separator_cases(),algebra_and_precision=algebra_and_precision(),recovery=recovery_cases(),ledger=ledger(),scope='Exact finite seams. All-size analytic/machine composition is a written theorem relative to the named primitive proofs, not established by these tests.')
    out=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write_result:
        with args.write_result.open('x') as f:f.write(out)
    else:need(json.loads(out)==json.loads((HERE/'RESULT.json').read_text()),'entire deterministic receipt')
    print(out,end='')

if __name__=='__main__':main()
