# SPDX-License-Identifier: Apache-2.0
"""Cross-call two-role exchange search for the unchanged helper408+424 word.
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
# General two-role exchange may involve different calls, unlike round one.
import time
cost=np.array([r**(1-.0017208)for r in range(49)]);cost[0]=0
moves=[];swaps=[];flat=placement.reshape(-1);tw=np.tile(W,N);tc=np.repeat(np.arange(N),408)
familysets=[set(fam[placement[t]].tolist())for t in range(N)]
bywidth={w:np.flatnonzero(tw==w)for w in set(W.tolist())}
deadline=time.monotonic()+240
for sweep in range(a.sweeps):
 changes=0;examined=0
 # Start with anomalous residual ranks. Later scan every nonempty residual.
 roles=np.flatnonzero(rem[flat]>0)
 roles=roles[np.argsort(-rem[flat[roles]],kind='stable')]
 for rid in roles:
  if time.monotonic()>deadline:break
  rid=int(rid);src=int(flat[rid]);rs=int(rem[src]);wa=int(tw[rid]);t=int(tc[rid]);fs=int(fam[src])
  if rs==0:continue
  examined+=1
  best=None
  for wb,ids in bywidth.items():
   d=wa-wb
   if d<=0:continue
   bs=flat[ids];rsb=rem[bs];us=tc[ids]
   ok=(rsb>=d)&(rsb<rs+d)&(lo[bs]<t)&(t<=hi[bs])&(lo[src]<us)&(us<=hi[src])&(bs!=src)
   cand=ids[ok]
   if not len(cand):continue
   bs=flat[cand];delta=cost[rs+d]+cost[rem[bs]-d]-cost[rs]-cost[rem[bs]]
   for z in np.argsort(delta)[:1000]:
    profit=float(delta[z])
    if profit>=-1e-10 or(best is not None and profit>=best[0]):break
    other=int(cand[z]);dst=int(flat[other]);u=int(tc[other]);fd=int(fam[dst])
    if t!=u and ((fd in familysets[t]and fd!=fs)or(fs in familysets[u]and fs!=fd)):continue
    best=(profit,other,dst,u,fd,d);break
  if best is None:continue
  profit,other,dst,u,fd,d=best
  if t!=u and fs!=fd:
   familysets[t].remove(fs);familysets[t].add(fd);familysets[u].remove(fd);familysets[u].add(fs)
  flat[rid]=dst;flat[other]=src;rem[src]+=d;rem[dst]-=d
  swaps.append([rid,other,src,dst,d]);changes+=1
 # Whole-role moves exploit the slack opened by the cross-call exchanges.
 for t in range(N):
  bs=placement[t]
  for h in sorted(range(408),key=lambda h:-rem[bs[h]]):
   src=int(bs[h]);width=int(W[h]);rs=int(rem[src])
   if rs==0:continue
   dests=np.flatnonzero((rem>=width)&(rem<rs+width)&(lo<t)&(t<=hi))
   if not len(dests):continue
   ds=cost[rs+width]+cost[rem[dests]-width]-cost[rs]-cost[rem[dests]]
   for j in np.argsort(ds)[:1000]:
    if ds[j]>=-1e-10:break
    dest=int(dests[j]);fd=int(fam[dest]);fs=int(fam[src])
    if dest==src or(fd in familysets[t]and fd!=fs):continue
    if fd!=fs:familysets[t].remove(fs);familysets[t].add(fd)
    rem[src]+=width;rem[dest]-=width;bs[h]=dest;moves.append([t,h,src,dest]);changes+=1;break
 print('sweep',sweep,'examined',examined,'changes',changes,'cross-swaps',len(swaps),'relocations',len(moves),'idle',dict(sorted(Counter(map(int,rem)).items())),flush=True)
 if changes==0 or time.monotonic()>deadline:break
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
