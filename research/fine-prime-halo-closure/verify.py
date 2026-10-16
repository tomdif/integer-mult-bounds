"""Exact finite controls for the scoped halo proof; no numerical eigensolver."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(value,message):
    if not value:raise ValueError(message)


def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def zero(n):return [[Q(0) for _ in range(n)] for _ in range(n)]
def transpose(a):return [list(x) for x in zip(*a)]
def add(a,b,c=1):return [[x+c*y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,c):return [[c*x for x in r] for r in a]
def mul(a,b):return [[sum(x*y for x,y in zip(r,s)) for s in zip(*b)] for r in a]
def maximum_band(a):return max((abs(i-j) for i,r in enumerate(a) for j,x in enumerate(r) if x),default=0)
def encoded(a):return [[str(x) for x in row] for row in a]


def inverse_polynomial(h,gamma,count):
    size=len(h);ht=transpose(h);q=add(eye(size),mul(ht,h),-gamma)
    total=zero(size);power=eye(size)
    for _ in range(count):total=add(total,power);power=mul(q,power)
    return scale(mul(total,ht),gamma),q,power,total


def matrices():
    receipts=[];controls=[];checked=0
    for size in (4,9,17):
        h=[[Q(2)+Q(i%3,16) if i==j else Q(1,4) if j==i+1 else Q(1,8) if i==j+1 else Q(0)
            for j in range(size)] for i in range(size)]
        need(mul(h,transpose(h))!=mul(transpose(h),h),'nonnormal witness')
        for count in (1,2,3):
            gamma=Q(1,16);p,q,power,total=inverse_polynomial(h,gamma,count)
            need(mul(p,h)==add(eye(size),power,-1),'right geometric residual')
            r=add(eye(size),mul(h,transpose(h)),-gamma);rp=eye(size)
            for _ in range(count):rp=mul(r,rp)
            need(mul(h,p)==add(eye(size),rp,-1),'left geometric residual')
            need(maximum_band(p)<=2*count-1,'exact inverse polynomial bandwidth')
            need(max(sum(abs(x) for x in row) for row in power)<=size*Q(15,16)**count,'conservative contraction envelope')
            if size==17:
                lo,hi=2,15;section=[row[lo:hi] for row in h[lo:hi]]
                small,*_=inverse_polynomial(section,gamma,count);radius=2*count-1
                for i in range(lo+radius,hi-radius):
                    need(p[i][lo:hi]==small[i-lo],'finite-section path locality')
                    need(not any(p[i][:lo]+p[i][hi:]),'no omitted exterior contribution')
                    checked+=size
                if count==3:need(maximum_band(p)==radius,'radius is attained')
            wrong=scale(total,gamma)
            need(mul(wrong,h)!=add(eye(size),power,-1),'missing adjoint control')
            wrong=scale(mul(transpose(h),total),gamma)
            if count>1:need(mul(wrong,h)!=add(eye(size),power,-1),'wrong noncommuting order control')
            receipts.append(dict(size=size,iterations=count,bandwidth=maximum_band(p),
                polynomial_sha256=sha256(json.dumps(encoded(p),separators=(',',':')).encode()).hexdigest()))
    controls.extend(['omitted_adjoint_on_nonnormal_matrix','adjoint_in_wrong_order','understated_attained_bandwidth'])
    h=[[Q(2)]];_,q,power,_=inverse_polynomial(h,Q(2),3)
    need(abs(power[0][0])>1,'unscaled Neumann iteration diverges');controls.append('invalid_neumann_scale')
    return dict(cases=receipts,locality_entries=checked,rejection_controls=controls)


def narrow():
    def gap(row,i):return abs(row[i])-sum(abs(x) for j,x in enumerate(row) if j!=i)
    def infinity(a):return max(sum(abs(x) for x in row) for row in a)
    def eliminate(a,k):
        keep=[i for i in range(len(a)) if i!=k]
        return [[a[i][j]-a[i][k]*a[k][j]/a[k][k] for j in keep] for i in keep]
    def inverse(a):
        size=len(a);work=[row[:]+unit for row,unit in zip(a,eye(size))]
        for k in range(size):
            pivot=work[k][k];need(pivot!=0,'gap supplies a pivot')
            work[k]=[x/pivot for x in work[k]]
            for i in range(size):
                if i!=k:
                    c=work[i][k];work[i]=[x-c*y for x,y in zip(work[i],work[k])]
        return [row[size:] for row in work]
    cases=0;stream=sha256()
    for size in (3,5,8):
        original=[[Q(1) if i==j else Q(7,8) if j==i+1 else Q(1,32) if i==j+1 else Q(0)
                   for j in range(size)] for i in range(size)]
        delta=min(gap(row,i) for i,row in enumerate(original));bound=infinity(original)
        for order in ('left','right','middle'):
            a=original
            while a:
                need(min(gap(row,i) for i,row in enumerate(a))>=delta and infinity(a)<=bound,'Schur row gap and row sum')
                ai=inverse(a);band=maximum_band(a)
                need(mul(a,ai)==eye(len(a)),'exact inverse witness')
                need(infinity(ai)<=1/delta,'uniform inverse row bound')
                need(infinity(transpose(ai))<=bound/delta**2+2*band*bound**2/delta**3,'banded inverse column bound')
                stream.update(json.dumps(encoded(a),separators=(',',':')).encode());cases+=1
                k=0 if order=='left' else len(a)-1 if order=='right' else len(a)//2
                a=eliminate(a,k)
    need(Q(8192,4**14)+Q(524288,4**11)<=1,'eventual p^10 spectral umbrella at p=4')
    witnesses=[]
    for size in (2,5,17):
        a=eye(size)
        for i in range(1,size):a[i][0]=Q(-1,2)
        ai=inverse(a);need(infinity(ai)<=2,'row-gap-only witness')
        norm_column_squared=sum(row[0]**2 for row in ai)
        need(norm_column_squared==1+Q(size-1,4),'unbounded spectral lower bound without bandwidth')
        witnesses.append(dict(size=size,first_column_norm_squared=str(norm_column_squared)))
    return dict(schur_sections=cases,section_sha256=stream.hexdigest(),
                norm_umbrella='p^10 from delta=1/(16 p^2), M<=2, b<=p, p>=4',
                row_gap_without_bandwidth_witnesses=witnesses,
                scope='Uniform narrow bound proved in NARROW.md, requiring the stated actual reference rounding and retained bandwidth geometry. Broad matrices are separate.')


def broad():
    """Exact source LDU identities with exp(b/denominator) rational and b<1."""
    from math import prod
    receipts=[];controls=[]
    def symmetric(nodes,degree,elementary):
        values=[Q(1)]+[Q(0)]*degree
        for x in nodes:
            indices=range(degree,0,-1) if elementary else range(1,degree+1)
            for k in indices:values[k]+=x*values[k-1]
        return values[degree]
    for rho,denominator,base in ((Q(3,2),4,Q(17,16)),(Q(5,4),16,Q(65,64))):
        need(denominator*(base-1)<1,'b=denominator log(base)<1')
        for origin in (-2,0,3):
            size=4;indices=list(range(origin,origin+size))
            q={i:(rho*i+Q(1,2)).numerator//(rho*i+Q(1,2)).denominator for i in indices}
            beta={i:rho*i-q[i] for i in indices}
            def exponential(exponent):
                power=denominator*exponent;need(power.denominator==1,'exact exponential grid')
                return base**power.numerator
            x={i:exponential(2*rho*q[i]) for i in indices}
            e={i:exponential(-rho*rho*i*i+beta[i]*beta[i]) for i in indices}
            c={i:prod((1-x[k]/x[i] for k in indices if k<i),start=Q(1)) for i in indices}
            g=[[exponential(-((rho*j-q[i])**2-beta[j]**2)) for j in indices] for i in indices]
            lower=zero(size);upper=zero(size);li=zero(size);ui=zero(size)
            for ii,i in enumerate(indices):
                for jj,j in enumerate(indices):
                    if i>=j:
                        lower[ii][jj]=g[ii][jj]*prod((1-x[k]/x[i] for k in indices if k<j),start=Q(1))/c[j]
                        d=prod((1-x[j]/x[k] for k in indices if j<k<=i),start=Q(1))
                        exponent=-beta[i]**2+beta[j]**2-rho*rho*(i-j)+2*rho*sum(beta[k] for k in indices if j<k<=i)
                        li[ii][jj]=(-1)**(i-j)*exponential(exponent)*c[i]/(c[j]*d)
                    if j>=i:
                        upper[ii][jj]=e[j]/e[i]*symmetric([x[k] for k in indices if k<=i],j-i,False)
                        ui[ii][jj]=(-1)**(j-i)*e[j]/e[i]*symmetric([x[k] for k in indices if k<j],j-i,True)
            diagonal=[[c[i] if i==j else Q(0) for j in indices] for i in indices]
            need(mul(mul(lower,diagonal),upper)==g,'finite Gaussian LDU')
            need(mul(li,lower)==mul(lower,li)==eye(size),'both lower inverse identities')
            need(mul(ui,upper)==mul(upper,ui)==eye(size),'both upper inverse identities')
            if origin==3:
                wrong=[row[:] for row in upper]
                wrong[0][1]=e[origin+1]/e[origin]*sum(exponential(2*rho*((rho*k+Q(1,2)).numerator//(rho*k+Q(1,2)).denominator)) for k in range(origin+1))
                need(mul(mul(lower,diagonal),wrong)!=g,'finite-origin shift control')
                controls.append('unshifted_origin_'+str(rho))
            receipts.append(dict(rho=str(rho),origin=origin,size=size,exponential_base=str(base),exponential_denominator=denominator,
                matrix_sha256=sha256(json.dumps(encoded(g),separators=(',',':')).encode()).hexdigest()))
    return dict(cases=receipts,rejection_controls=controls,
                scope='Finite LDU identities, including b<1 and translated origins. The uniform limits and norm estimates are the written proof, with actual rounding/prefix geometry explicit.')


def ledger():
    raw=json.loads((ROOT/'research/paired-terminal-refit/evidence/OUTER-LEDGER.json').read_text())
    row=raw['rows']['struct_boundary_radix_union'];epsilon=Q(row['epsilon']['rational']);beta=Q(row['beta']['rational']);kappa=Q(row['kappa']['rational'])
    need(raw['geometry_changes']['halo_power']==48 and raw['geometry_changes']['core_power']==128,'actual halo geometry')
    exponent=epsilon+beta+48-128+50
    need(epsilon<1 and beta<1 and exponent<-28 and exponent<1-kappa,'direct face routine fits headline')
    need(beta+48-128<0,'small halo fraction')
    points=[]
    for p in (2,3,5,17,128,1000):
        denominator=1<<((p**20-1).bit_length());gamma=Q(1,denominator);j=2*p**42
        need(gamma*p**20<=1 and 2*gamma*p**20>1,'dyadic scale interval')
        need(j*gamma*Q(1,p**20)>=p*p,'exponential contraction budget')
        need((2*j-1)*(p-1)<=p**48,'actual conservative halo width')
        points.append(dict(p=p,scale_denominator=denominator,iterations=j))
    volume_checks=0
    for g in range(1,8):
        for side in (8,16,32):
            for radius in (1,2):
                total=6*radius*sum(side**j*(side+2*radius)**(g-1-j) for j in range(g))
                need(total==3*((side+2*radius)**g-side**g),'exact duplicated face volume')
                volume_checks+=1
    return dict(face_cost_power=str(exponent),target_power=str(1-kappa),
                margin_to_target=str(1-kappa-exponent),halo_fraction_power=str(beta+48-128),
                dyadic_scale_cases=points,exact_face_volume_cases=volume_checks,
                scope='Exact parameter consequences; the Gaussian norm premises are not proved here.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',type=Path);args=ap.parse_args()
    source=json.loads((HERE/'SOURCES.json').read_text());count=0
    for item in source['files']:
        if item['usage']=='input':
            need(sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256'],'changed ledger');count+=1
    result=dict(status='PASS_SCOPED_FINE_PRIME_HALO',source_files=count,matrices=matrices(),narrow=narrow(),broad=broad(),ledger=ledger(),
                scope='Local inverse and current face budget, plus narrow/broad spectral arguments under explicit reference-rounding and prefix-geometry premises. Full contract T remains open.')
    text=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write_result:
        with args.write_result.open('x') as out:out.write(text)
    else:need(json.loads(text)==json.loads((HERE/'RESULT.json').read_text()),'full deterministic receipt')
    print(text,end='')


if __name__=='__main__':main()
