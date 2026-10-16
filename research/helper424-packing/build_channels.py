# SPDX-License-Identifier: Apache-2.0
"""Append declared 400 and 416 extraction stages to the verified round-one source.
Preserves every prior derivation, audit, native and outer predicate. Credits
PR2908's extraction and integration adapters and all retained source notices.
"""
import argparse,copy,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def tree(p):return {f.relative_to(p).as_posix():sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f!=p/'MANIFEST.json'}
def replace(s,old,new,n=1):
 assert s.count(old)==n,(old,s.count(old),n)
 return s.replace(old,new)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--adapters',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--refit',type=Path);ap.add_argument('--retained',type=Path);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 if not __debug__:raise RuntimeError('Assertions required')
 source=a.source;out=a.out;out.mkdir(parents=True,exist_ok=False)
 assert sha(source/'MANIFEST.json')=='efef6b2579bd72004c574635ad9d1e3d39aafac56bf8f0cb35658c151e860105'
 assert tree(source)==rd(source/'MANIFEST.json')
 pins=rd(P/'vendor/round1/evidence/ADAPTER-DERIVATION.json')
 for name,v in pins.items():
  if name=='prepare_channel_native.py' and a.retained:
   actual=(a.adapters/name).read_text();declared=sha(a.retained/'NATIVE-RECEIPT.json')
   normalized=replace(actual,f"OLD_RECEIPT_SHA='{declared}'","OLD_RECEIPT_SHA='ce6239ff3cee5222b4f8676df123b863902e04dd1e9fb0cd707adcbadc3dae42'")
   assert hashlib.sha256(normalized.encode()).hexdigest()==v['after'],'only the declared fresh retained receipt identity may differ'
  else:assert sha(a.adapters/name)==v['after']
 src=out/'source';shutil.copytree(source,src);model=source/'new/borrow/channel424';derivation=[]
 for index,h in enumerate([400,416],75):
  local=src/f'new/borrow/channel{h}';shutil.copytree(model,local)
  transform=rd(a.words/str(h)/'TRANSFORM-base.json');assert transform==rd(a.words/str(h)/'TRANSFORM-extra.json')
  for tag in ['base','extra']:
   current=src/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
   assert rd(current)==rd(a.words/str(h)/f'PARENT-{tag}.json.gz')
   for prefix in ['PARENT','WORD']:shutil.copy2(a.words/str(h)/f'{prefix}-{tag}.json.gz',local/f'data/{prefix}-{tag}.json.gz')
   shutil.copy2(current,src/f'new/borrow/inputs/PRE-CHANNEL{h}-WORD-{tag}.json.gz')
   shutil.copy2(local/f'data/WORD-{tag}.json.gz',current)
  save(local/'data/TRANSFORM.json',transform)
  s=(model/'extract.py').read_text();s=replace(s,'h == 424',f'h == {h}');s=replace(s,"'fresh helper424'",f"'fresh helper{h}'")
  s=replace(s,"PROFILE = {'1':2410,'2':638,'3':262,'4':128,'5':26,'8':8}",f"PROFILE = {transform['profile']!r}")
  s=replace(s,"INVENTORY = {'4':26,'5':2,'7':62,'8':88,'9':230}",f"INVENTORY = {transform['inventory']!r}")
  s=replace(s,'len(before)==24 and len(after)==3',f"len(before)=={len(transform['before'])} and len(after)=={len(transform['after'])}")
  s=replace(s,'frame = after[0][-1]',"frame = transform['final_frame']")
  s=replace(s,"pm.basis(frame)==(256,128,64,36,20,8,2,1), 'hyperplane52'",f"pm.basis(frame)=={tuple(transform['final_frame'])!r}, 'hyperplane{transform['normal']}'")
  s=replace(s,"g[0]=='add' and g[-1]==frame","g[0]=='add' and pm.contained(pm.basis(g[-1]),pm.basis(frame))")
  s=s.replace('Second helper424 stage.',f'Additional helper{h} stage after the verified helper408/424 construction.')
  (local/'extract.py').write_text(s);shutil.copy2(local/'extract.py',src/f'new/borrow/channel{h}_extract.py')
  s=(model/'verify.py').read_text();s=replace(s,"==74,'charged 74 private buffers'",f"=={index},'charged {index} private buffers'")
  first_scale=next(i for i,g in enumerate(transform['before'])if g[0]=='scale')
  s=replace(s,"g=next(g for g in w['A'][w['prelude_events']:] if g[:2]==['scale',424]);g[2]*=2",f"g=w['A'][w['prelude_events']+{first_scale}];need(g[0]=='scale','declared input scale');g[2]*=2")
  s=replace(s,'==1128',f'=={704+h}',n=2).replace('HELPER424',f'HELPER{h}')
  (local/'verify.py').write_text(s);save(local/'PINS.json',{f.relative_to(local).as_posix():sha(f)for d in ['vendor','data']for f in(local/d).rglob('*')if f.is_file()})
  with (out/f'local-{h}.log').open('w')as log:subprocess.run([sys.executable,'-B',str(local/'verify.py'),'--work',str(out/f'local-{h}')],check=True,stdout=log,stderr=subprocess.STDOUT)
  f=src/'new/rebuild_borrow.py';s=f.read_text();anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
  block=f"""    import channel{h}_extract
    declared_parent=json.loads(gzip.decompress((D/'inputs'/f'PRE-CHANNEL{h}-WORD-{{wt}}.json.gz').read_bytes()))
    assert chain[-1]==declared_parent
    declared_transform=json.loads((D/'channel{h}/data/TRANSFORM.json').read_text())
    declared_word=channel{h}_extract.apply(chain[-1],declared_transform)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=declared_word[k_])==channel{h}_extract.ALLOWED
    chain.append(declared_word);steps.append('two-sided-helper{h}')
"""
  f.write_text(replace(s,anchor,block+anchor))
  f=src/'verify.py';s=f.read_text();previous=424 if h==400 else 400;anchor=f"run('two-sided-helper{previous}-review',P/'new/borrow/channel{previous}/verify.py','--work',work/'two-sided-helper{previous}-review')";f.write_text(replace(s,anchor,anchor+f"\nrun('two-sided-helper{h}-review',P/'new/borrow/channel{h}/verify.py','--work',work/'two-sided-helper{h}-review')"))
  derivation.append(dict(helper=h,buffers=index,transform=transform,local_result_sha256=sha(out/f'local-{h}/RESULT.json')))
 if a.refit:
  local=src/'new/borrow/terminal_refit';(local/'data').mkdir(parents=True);shutil.copytree(model/'vendor',local/'vendor');shutil.copy2(P/'terminal_refit.py',local/'terminal_refit.py');shutil.copy2(P/'terminal_refit.py',src/'new/borrow/terminal_refit_apply.py')
  for tag in ['base','extra']:
   current=src/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';assert rd(current)==rd(a.refit/f'PARENT-{tag}.json.gz')
   for prefix in ['PARENT','WORD']:shutil.copy2(a.refit/f'{prefix}-{tag}.json.gz',local/f'data/{prefix}-{tag}.json.gz')
   shutil.copy2(a.refit/f'PATCH-{tag}.json',local/f'data/PATCH-{tag}.json');shutil.copy2(current,src/f'new/borrow/inputs/PRE-REFIT-WORD-{tag}.json.gz');shutil.copy2(local/f'data/WORD-{tag}.json.gz',current)
  save(local/'PINS.json',{f.relative_to(local).as_posix():sha(f)for d in ['vendor','data']for f in(local/d).rglob('*')if f.is_file()})
  with (out/'local-refit.log').open('w')as log:subprocess.run([sys.executable,'-B',str(local/'terminal_refit.py'),'--work',str(out/'local-refit')],check=True,stdout=log,stderr=subprocess.STDOUT)
  f=src/'new/rebuild_borrow.py';s=f.read_text();anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
  block="""    import terminal_refit_apply
    refit_parent=json.loads(gzip.decompress((D/'inputs'/f'PRE-REFIT-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==refit_parent
    refit_patch=json.loads((D/'terminal_refit/data'/f'PATCH-{wt}.json').read_text())
    refit_word=terminal_refit_apply.apply(chain[-1],refit_patch)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=refit_word[k_])==terminal_refit_apply.ALLOWED
    chain.append(refit_word);steps.append('commuting-terminal-frame-refit')
"""
  f.write_text(replace(s,anchor,block+anchor));f=src/'verify.py';s=f.read_text();anchor="run('two-sided-helper416-review',P/'new/borrow/channel416/verify.py','--work',work/'two-sided-helper416-review')";f.write_text(replace(s,anchor,anchor+"\nrun('terminal-frame-refit-review',P/'new/borrow/terminal_refit/terminal_refit.py','--work',work/'terminal-frame-refit-review')"));derivation.append(dict(stage='commuting-terminal-frame-refit',local_result_sha256=sha(out/'local-refit/RESULT.json')))
 providers={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=rd(src/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz');hs=sorted(set(range(224,704))-set(w['removed']));providers[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in hs],'actual_paid_profile':w['report']['local_profile']}
 save(src/'new/BORROW-PROVIDERS.json',providers);save(src/'MANIFEST.json',tree(src));manifest=sha(src/'MANIFEST.json');count=len(rd(src/'MANIFEST.json'))
 adapters={}
 for name in ['prepare_channel_native.py','admit_channel408.py','channel_blocknorm.py']:
  s=(a.adapters/name).read_text()
  if name=='prepare_channel_native.py':
   s=replace(s,"SOURCE_SHA='efef6b2579bd72004c574635ad9d1e3d39aafac56bf8f0cb35658c151e860105'",f"SOURCE_SHA='{manifest}'");s=replace(s,'SOURCE_FILES=624',f'SOURCE_FILES={count}');s=replace(s,"SOURCE_COMMIT='two-sided-helper408424-pr2908'","SOURCE_COMMIT='four-helper-channels-after-round1'");s=replace(s,"len(can['zero_buffers'])==74","len(can['zero_buffers'])==76")
  elif name=='admit_channel408.py':
   s=replace(s,"commit='two-sided-helper408424-pr2908',manifest='efef6b2579bd72004c574635ad9d1e3d39aafac56bf8f0cb35658c151e860105',helpers=408,source_file_count=624",f"commit='four-helper-channels-after-round1',manifest='{manifest}',helpers=408,source_file_count={count}")
   s=replace(s,'zero_buffers_allocated_and_cleared=74','zero_buffers_allocated_and_cleared=76');s=replace(s,"len(c.get('zero_buffers',[]))==74","len(c.get('zero_buffers',[]))==76");s=replace(s,'896*T+expected_helpers+8+74+2','896*T+expected_helpers+8+76+2');s=s.replace('74 private buffers','76 private buffers').replace('and 74 buffers','and 76 buffers')
  else:
   for old,new in [("len(allocated)==74","len(allocated)==76"),("'zero_buffers_allocated_and_cleared':74","'zero_buffers_allocated_and_cleared':76"),("r['zero_buffers_returned_to_zero']==74","r['zero_buffers_returned_to_zero']==76"),("live+8+408+74+2","live+8+408+76+2"),("len(mp)==74","len(mp)==76"),("'zero_buffers':[live+416,live+490], 'coefficient':[live+490,live+492]","'zero_buffers':[live+416,live+492], 'coefficient':[live+492,live+494]"),('physical=live+492','physical=live+494')]:s=replace(s,old,new)
   s=s.replace('all74 private','all76 private').replace('74distinct private','76distinct private')
  f=out/name;f.write_text(s);adapters[name]=dict(before=sha(a.adapters/name),after=sha(f))
 before=tree(source);after=tree(src);save(out/'SOURCE-DERIVATION.json',dict(parent_manifest=sha(source/'MANIFEST.json'),manifest_sha256=manifest,files=count,changes={n:{'before':before.get(n),'after':h}for n,h in after.items()if before.get(n)!=h},stages=derivation));save(out/'ADAPTER-DERIVATION.json',adapters)
 print('PASS_FOUR_CHANNEL_SOURCE',manifest,count,flush=True)
if __name__=='__main__':main()
