# SPDX-License-Identifier: Apache-2.0
"""Four commuting terminal pairs, evaluated first in their common 7-frame.

Pure declared patch plus independent full-word and scalar-operator replay.
The ten-extraction parent is Mason Hale PR2917, building on Jeremy Diviney PR2908 and the credited Kothe/2857/native lineage.
"""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
ALLOWED={'restore','report','cleanup'}
PROFILE={'1':2408,'2':644,'3':280,'4':110,'5':26,'8':8}
INVENTORY={'4':26,'5':2,'7':62,'8':96,'9':222}
def canon(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,x):
 b=(json.dumps(x,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0)if p.suffix=='.gz'else b)
def apply(word,patch):
 import preload_move as pm
 assert patch['parent_canonical_sha256']==canon(word)
 x=copy.deepcopy(word);assert len(patch['edits'])==4
 for e in patch['edits']:
  i=e['index'];old=e['old'];new=e['new'];assert x['restore'][i:i+len(old)]==old
  assert len(old)==len(new)and len(old)in(2,3)
  a,b=old[-2:];assert a[0]==b[0]=='add'and a[1]==b[1]and a[1]not in(a[2],b[2])
  assert a[1]in(408,424,428,412)and new[-2][:-1]==b[:-1]and new[-1]==a
  assert len(new[-2][-1])==7 and pm.contained(pm.basis(new[-2][-1]),pm.basis(b[-1]))
  if len(old)==3:assert old[0][0]=='scale'and old[0][1]==a[1]and new[0][:-1]==old[0][:-1]and new[0][-1]==new[-2][-1]
  x['restore'][i:i+len(old)]=copy.deepcopy(new)
 profile,inventory=pm.frame_report(x);assert profile==PROFILE and inventory==INVENTORY
 x['report']['local_profile']=profile;x['report']['width_inventory']=inventory
 z=copy.deepcopy(x);z['A']=z['A'][z['prelude_events']:];x['cleanup']=pm.derive_cleanup(z,set(map(int,x['helper_final'])))
 assert {k for k in word if word[k]!=x[k]}==ALLOWED
 return x
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--vendor',type=Path);ap.add_argument('--words',type=Path);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--generate',action='store_true');a=ap.parse_args();P=Path(__file__).resolve().parent
 if not __debug__:raise RuntimeError('Assertions required')
 vendor=a.vendor or P/'vendor';sys.path.insert(0,str(vendor));import audit_local as aud;import preload_move as pm
 if not a.generate:
  actual={f.relative_to(P).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()for d in ['data','vendor']for f in(P/d).rglob('*')if f.is_file()};assert actual==read(P/'PINS.json')
 out=a.work;out.mkdir(parents=True,exist_ok=False);results={}
 for tag in ['base','extra']:
  if a.generate:
   parent=read(a.words/f'WORD-{tag}.json.gz');edits=[]
   for h,s,t,F in [(408,42,105,[256,128,66,36,22,8,1]),(424,16,44,[256,128,65,37,20,8,2]),(428,416,430,[256,128,72,44,28,2,1]),(412,400,414,[256,128,65,36,20,9,3])]:
    i=next(i for i,g in enumerate(parent['restore'])if g[:5]==['add',h,s,1,2]);old=copy.deepcopy(parent['restore'][i:i+2]);assert old[1][:5]==['add',h,t,1,1];new=[old[1][:-1]+[F],old[0]]
    if h in(428,412):
     i-=1;scale=copy.deepcopy(parent['restore'][i]);assert scale[:4]==['scale',h,-1,1];old=[scale]+old;new=[scale[:-1]+[F]]+new
    edits.append(dict(index=i,old=old,new=new))
   patch=dict(parent_canonical_sha256=canon(parent),edits=edits);candidate=apply(parent,patch)
   for name,x in [(f'PARENT-{tag}.json.gz',parent),(f'WORD-{tag}.json.gz',candidate),(f'PATCH-{tag}.json',patch)]:save(out/name,x)
   data=out
  else:
   data=P/'data';parent=read(data/f'PARENT-{tag}.json.gz');patch=read(data/f'PATCH-{tag}.json');candidate=apply(parent,patch);assert candidate==read(data/f'WORD-{tag}.json.gz')
  # A separate exact scalar replay checks the entire terminal operators.
  rows=[]
  for w in [parent,candidate]:
   mat={r:{r:1}for r in range(704)}
   for g in w['restore']:aud.apply(g,mat)
   rows.append(mat)
  assert rows[0]==rows[1]
  aud.run(data/f'PARENT-{tag}.json.gz',out/f'PARENT-AUDIT-{tag}.json');aud.run(data/f'WORD-{tag}.json.gz',out/f'AUDIT-{tag}.json')
  report=read(out/f'AUDIT-{tag}.json');assert report['zero_buffers']==report['restored_cold']==82 and report['local_profile']==PROFILE and report['width_inventory']==INVENTORY
  results[tag]=dict(parent_canonical=canon(parent),candidate_canonical=canon(candidate),full_terminal_operator_equal=True,audit=report)
 rejected={};parent=read(data/'PARENT-base.json.gz');good=read(data/'WORD-base.json.gz')
 for name in ['wrong_coefficient','noncommuting_order','underpriced_profile','too_small_frame']:
  w=copy.deepcopy(good);i=read(data/'PATCH-base.json')['edits'][0]['index']
  if name=='wrong_coefficient':w['restore'][i][3]*=2
  elif name=='noncommuting_order':w['restore'][i+1],w['restore'][i+2]=w['restore'][i+2],w['restore'][i+1]
  elif name=='underpriced_profile':w['report']['local_profile']['1']-=1
  else:w['restore'][i][-1]=w['restore'][i][-1][1:]
  if name in ['wrong_coefficient','noncommuting_order']:
   profile,inventory=pm.frame_report(w);w['report']['local_profile']=profile;w['report']['width_inventory']=inventory
   z=copy.deepcopy(w);z['A']=z['A'][z['prelude_events']:];w['cleanup']=pm.derive_cleanup(z,set(map(int,z['helper_final'])))
  save(out/(name+'.json.gz'),w)
  try:aud.run(out/(name+'.json.gz'),out/(name+'.json'))
  except (AssertionError,RuntimeError,ValueError)as error:rejected[name]=str(error)
  else:raise AssertionError('accepted '+name)
 result=dict(status='PASS_COMMUTING_TERMINAL_FRAME_REFIT',providers=results,semantic_controls=rejected,scope='Exact scalar operator equality, declared local frame and complete forward/dual word audits; full native and supplier admission required.')
 save(out/'RESULT.json',result);print(result['status'],PROFILE,flush=True)
if __name__=='__main__':main()
