# SPDX-License-Identifier: Apache-2.0
"""Bounded continued owner repair for the unchanged helper408+424 word.
Credit PR2908's same-call exchange / whole-role relocation strategy, and its
credited owner engine. Every result is checked by that independent engine.
"""
import argparse,copy,gzip,importlib.util,json,sys
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as Q
import numpy as np
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--initial',type=Path,required=True);ap.add_argument('--sweeps',type=int,default=20);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
p=a.source;out=a.out;out.mkdir(parents=True,exist_ok=False)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,x):
 b=(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
spec=importlib.util.spec_from_file_location('owner',p/'allocation/vendor/independent_owners.py');owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
base=p/'allocation';order=read(a.initial/'ORDER.json');dispatch=read(a.initial/'DISPATCH.json');fill=read(a.initial/'FILL.json.gz');template=read(base/'vendor/TEMPLATE.json.gz');plan=read(base/'vendor/PLAN.json.gz');T=len(order)//9;N=len(order);providers={}
for tag,pid in [('base','gauge44'),('extra','extra')]:
 w=read(a.words/f'WORD-{tag}.json.gz');hs=sorted(set(range(224,704))-set(w['removed']));providers[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in hs],'actual_paid_profile':w['report']['local_profile']}
widths=providers['gauge44']['widths'];assert widths==providers['extra']['widths']
W=np.array(widths,dtype=np.int16);win=owner.windows(template,order,T);bins=[];caps=[];lo=[];hi=[];families=[]
for(o,c),(cap,l,h)in sorted(win.items()):
 for port in range(112):bins.append((o,c,port));caps.append(cap);lo.append(l);hi.append(h);families.append(o*896+(2*plan['pairs'][str(c)]+plan['sides'][str(c)])*112+port)
bid={b:i for i,b in enumerate(bins)};caps=np.array(caps);lo=np.array(lo);hi=np.array(hi);fam=np.array(families);placement=np.empty((N,408),dtype=np.int32);used=np.zeros(len(bins),dtype=np.int16)
for t,h,o,c,port,z in fill['rows']:
 b=bid[o,c,port];placement[t,h]=b;used[b]+=W[h]
rem=caps-used;assert min(rem)>=0
cost=np.array([r**(1-.0017208)for r in range(49)]);cost[0]=0
moves=[];swaps=[]
for sweep in range(a.sweeps):
 changes=0
 for t in (range(N) if sweep%2==0 else reversed(range(N))):
  # Swap helper identities within this call: windows and family set are preserved.
  bs=placement[t]
  for _ in range(20):
   r=rem[bs];deltaW=W[:,None]-W[None,:]
   # row i receives helper j, so its remainder grows by w_i-w_j.
   ri=r[:,None]+deltaW;rj=r[None,:]-deltaW
   ok=(ri>=0)&(rj>=0)&(ri<=48)&(rj<=48)&(bs[:,None]!=bs[None,:])
   ds=cost[np.clip(ri,0,48)]+cost[np.clip(rj,0,48)]-cost[r][:,None]-cost[r][None,:]
   ds[~ok]=1
   i,j=np.unravel_index(ds.argmin(),ds.shape)
   if ds[i,j]>=-1e-10:break
   bi,bj=int(bs[i]),int(bs[j]);d=int(W[i]-W[j]);rem[bi]+=d;rem[bj]-=d;bs[i],bs[j]=bj,bi;swaps.append([t,int(i),int(j)]);changes+=1
  # Relocate whole roles, respecting source windows and same-call families.
  usedfamilies=set(fam[bs].tolist())
  for h in sorted(range(408),key=lambda h:-rem[bs[h]]):
   src=int(bs[h]);width=int(W[h]);rs=int(rem[src])
   if rs==0:continue
   # Concavity permits improvement only if the destination is more nearly full.
   mask=(rem>=width)&(rem<rs+width)&(lo<t)&(t<=hi)
   dests=np.flatnonzero(mask)
   if not len(dests):continue
   ds=cost[rs+width]+cost[rem[dests]-width]-cost[rs]-cost[rem[dests]]
   for j in np.argsort(ds)[:100]:
    if ds[j]>=-1e-10:break
    dest=int(dests[j]);fd=int(fam[dest]);fs=int(fam[src])
    if dest==src or(fd in usedfamilies and fd!=fs):continue
    usedfamilies.remove(fs);usedfamilies.add(fd);rem[src]+=width;rem[dest]-=width;bs[h]=dest;moves.append([t,h,src,dest]);changes+=1;break
 print('sweep',sweep,'changes',changes,'swaps',len(swaps),'relocations',len(moves),flush=True)
 if changes==0:break
fill['rows']=[];offset=np.zeros(len(bins),dtype=np.int16)
for t in range(N):
 for h,b in enumerate(placement[t]):
  o,c,port=bins[b];fill['rows'].append([t,h,o,c,port,int(offset[b])]);offset[b]+=W[h]
assert np.array_equal(caps-offset,rem)
providers={pid:{'widths':d['widths'],'actual_paid_profile':{int(r):n for r,n in d['actual_paid_profile'].items()}}for pid,d in providers.items()}
res,_,_=owner.check(T,order,fill,{(s,r):pid for s,r,pid in dispatch},None,plan,template,providers)
nbuf=len(w['helper_final']);res['physical']=896*T+408+8+nbuf+2;res['private_buffers']=nbuf
# Floating proposal only; exact moment follows separately.
H={int(r):n for r,n in res['profile'].items()};low,high=0.,.003
for _ in range(60):
 mid=(low+high)/2;moment=sum(n*(r/73)**(1-mid)for r,n in H.items())/(896*T)
 if moment<1:low=mid
 else:high=mid
res['floating_root_proposal']=low;res['swaps']=len(swaps);res['relocations']=len(moves)
for name,d in [('FILL.json.gz',fill),('ORDER.json',order),('DISPATCH.json',dispatch),('PROFILE.json',res['profile']),('PROVIDERS.json',providers),('OWNER-RESULT.json',res),('MOVES.json',{'swaps':swaps,'relocations':moves,'bins':bins})]:save(out/name,d)
print(json.dumps(res,sort_keys=True),flush=True)
