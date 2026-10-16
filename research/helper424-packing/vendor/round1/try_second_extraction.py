# SPDX-License-Identifier: Apache-2.0
"""Bounded symmetric second-channel experiment, credit PR2908's paired extraction.

Screen the analogous 424/440 terminal triples after the admitted 408 word.
Exact free-operator pairing and all protected inputs are mandatory. Nominees
must pass the complete inherited local auditor; no supplier claim follows.
"""
import argparse,copy,gzip,importlib.util,json,sys,subprocess
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict

ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
root=a.source.resolve();out=a.work.resolve();out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(root/'vendor'))
import preload_move as pm
import audit_local as aud

def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def fail(c,msg):
 if not c:raise ValueError(msg)
def nz(d):return {k:v for k,v in d.items()if v}
def program(w):
 P=[g for g in w['A'][w['prelude_events']:]if g[0]=='warp' or not 112<=g[1]<224]
 by=defaultdict(list)
 for op,rec in enumerate(w['warps'],1):by[rec[0]].append(['warp',rec[1],op])
 for i in range(len(w['B'])+1):
  P+=by[i]
  if i<len(w['B'])and not 112<=w['B'][i][1]<224:P.append(w['B'][i])
 return P+w['restore']
def trans(w,h,s,t):
 live=set(range(704))-set(w['removed'])-set(range(112,224));P=program(w)
 M={r:{(r,()):Q(1)}for r in live}
 for g in P:aud.walg_apply(g,M,False,10**6)
 alpha={h:Q(1),s:Q(1,2),t:Q(1)}
 u=defaultdict(Q)
 for r,c in alpha.items():
  for k,d in M[r].items():u[k]+=c*d
 u=nz(u)
 protected=set(map(int,w['helper_final']))|set(map(int,w['start_extra']))|{c['source']for c in w['initial_corrections']}
 H={r for r in live if r>=224 and r not in protected}
 fail(all(r in H and not op for r,op in u),('u not scalar/protected',[(r,op)for r,op in u if r not in H or op]))
 u={r:c for (r,op),c in u.items()}
 V={r:{} for r in live};V[s][('v',())]=Q(2)
 for g in reversed(P):aud.walg_apply(aud.invert_item(g,()),V,False,10**6)
 fail(all(r in H and all(not op for var,op in row)for r,row in V.items()if row),'v not scalar/protected')
 v={r:row[('v',())]for r,row in V.items()if row}
 fail(sum(u.get(r,0)*c for r,c in v.items())==1,'pairing')
 fail(h in v and v[h]!=0,'nonzero pivot')
 # S=S0*R. R removes the other entries of u*S0; S0 sends e_h to v.
 before=[]
 for r,c in sorted(u.items()):
  if r!=h:before.append(['add',h,r,(-c).numerator,c.denominator,[]])
 before.append(['scale',h,v[h].numerator,v[h].denominator,[]])
 for r,c in sorted(v.items()):
  if r!=h:
   d=c/v[h];before.append(['add',r,h,d.numerator,d.denominator,[]])
 # Candidate E must contain the terminal current frames of the entire output triple.
 cur=[(p,)for p in w['ports']]+[()]*(704-112)
 for r,E in w['start_extra'].items():cur[int(r)]=pm.basis(E)
 for g in w['A']:
  if g[0]=='warp':cur[g[1]]=pm.basis(g[4])
  else:
   for r in aud.registers(g):cur[r]=pm.basis(g[-1])
 by=defaultdict(list)
 for rec in w['warps']:by[rec[0]].append(rec)
 for i in range(len(w['B'])+1):
  for rec in by[i]:cur[rec[1]]=pm.basis(rec[4])
  if i<len(w['B']):
   for r in aud.registers(w['B'][i]):cur[r]=pm.basis(w['B'][i][-1])
 for g in w['restore']:
  for r in aud.registers(g):cur[r]=pm.basis(g[-1])
 normals=[n for n in range(1,512)if all((n&x).bit_count()%2==0 for r in [h,s,t]for x in cur[r])]
 fail(normals,'no terminal hyperplane')
 results=[]
 for normal in normals:
  E=list(pm.basis([x for x in range(1,512)if (x&normal).bit_count()%2==0]))
  after=[['add',h,s,1,2,E],['add',h,t,1,1,E],['add',s,h,-2,1,E]]
  x=copy.deepcopy(w);n=x['prelude_events'];x['A']=x['A'][:n]+before+x['A'][n:];x['restore']+=after;x['helper_final'][str(h)]=E
  C=defaultdict(dict)
  for g in x['compensation']:C[g[2]][g[1]]=C[g[2]].get(g[1],Q(0))+Q(g[3],g[4])
  for g in reversed(before):
   if g[0]=='scale':C[g[1]]={t:c*Q(g[2],g[3])for t,c in C[g[1]].items()}
   else:
    d,sr=g[1:3];c=Q(g[3],g[4])
    for target,b in C[d].items():C[sr][target]=C[sr].get(target,Q(0))+c*b
  x['compensation']=[['add',t,r,c.numerator,c.denominator,[]]for r,col in sorted(C.items())for t,c in sorted(col.items())if c]
  fail(not any(g[2]==h for g in x['compensation']),'cold input compensation')
  profile,inventory=pm.frame_report(x);x['report']['local_profile']=profile;x['report']['width_inventory']=inventory
  z=copy.deepcopy(x);z['A']=z['A'][n:];x['cleanup']=pm.derive_cleanup(z,set(map(int,x['helper_final'])))
  results.append((x,dict(helper=h,normal=normal,before=before,after=after,profile=profile,inventory=inventory,v={r:str(c)for r,c in v.items()},u={r:str(c)for r,c in u.items()})))
 return results
receipt=[]
for tag in ['base','extra']:
 for h,s,t in [(408,42,105),(424,16,44),(440,20,46)]:
  p=root/'data'/('PARENT-'+tag+'.json.gz'if h==408 else'WORD-'+tag+'.json.gz');w=read(p)
  try:
   candidates=trans(w,h,s,t)
   for x,tr in candidates:
    name=f'{tag}-{h}-{tr["normal"]}';path=out/(name+'.json.gz');path.write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0));(out/(name+'-TRANSFORM.json')).write_text(json.dumps(tr,indent=2)+'\n')
    run=subprocess.run([sys.executable,'-B',str(root/'vendor/audit_local.py'),'--word',str(path),'--output',str(out/(name+'-AUDIT.json'))],capture_output=True,text=True)
    (out/(name+'.log')).write_text(run.stdout+run.stderr)
    receipt.append(dict(variant=tag,helper=h,normal=tr['normal'],profile=tr['profile'],inventory=tr['inventory'],audit_exit=run.returncode,reason=(run.stdout+run.stderr)[-500:]))
  except ValueError as e:receipt.append(dict(variant=tag,helper=h,status='REJECTED_EXACT_SCREEN',reason=str(e)))
  print(receipt[-1],flush=True)
(out/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
