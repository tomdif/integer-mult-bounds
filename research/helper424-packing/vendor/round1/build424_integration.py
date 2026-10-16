# SPDX-License-Identifier: Apache-2.0
"""Source-bound composition of PR2908 with the helper424 extraction.
All original 408 checks remain; 424 has a separate declared stage and controls.
Only source identities and the derived private-buffer count change in the
admission/preparation/block-norm adapters; dimension73 and group72 are retained.
"""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--pm-source',type=Path,required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--retained',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
q=a.predecessor.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def tree(p):return {f.relative_to(p).as_posix():sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f!=p/'MANIFEST.json'}
def replace(body,old,new,n=1):
 assert body.count(old)==n,(old,body.count(old),n)
 return body.replace(old,new)
assert tree(q)==rd(q/'MANIFEST.json'),'unchanged PR2908 export'
assert sha(q/'MANIFEST.json')=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f','pinned PR2908 manifest'
subprocess.run([sys.executable,'-B',str(q/'tools/build_channel_overlay.py'),'--source',str(a.pm_source),'--local-package',str(q),'--out',str(out/'source408')],check=True)
src=out/'source';shutil.copytree(out/'source408',src)
local=src/'new/borrow/channel424';(local/'data').mkdir(parents=True);(local/'vendor').mkdir()
for name in ['audit_local.py','preload_move.py']:shutil.copy2(q/'vendor'/name,local/'vendor'/name)
shutil.copy2(q/'structure.py',local/'structure.py')
for tag in ['base','extra']:
 shutil.copy2(q/f'data/WORD-{tag}.json.gz',local/f'data/PARENT-{tag}.json.gz')
 shutil.copy2(a.words/f'{tag}-424-52.json.gz',local/f'data/WORD-{tag}.json.gz')
shutil.copy2(a.words/'base-424-52-TRANSFORM.json',local/'data/TRANSFORM.json')
text=(q/'extract.py').read_text();text=replace(text,"h == 408","h == 424");text=replace(text,"'fresh helper408'","'fresh helper424'")
text=replace(text,"'1':2407,'2':640","'1':2410,'2':638");text=replace(text,"'8':87,'9':231","'8':88,'9':230")
text=text.replace('Jeremy Diviney with OpenAI Codex assistance.','Derived from Jeremy Diviney PR2908, with OpenAI Codex assistance. Second helper424 stage.')
(local/'extract.py').write_text(text);shutil.copy2(local/'extract.py',src/'new/borrow/channel424_extract.py')
text=(q/'verify.py').read_text();text=replace(text,"==73,'charged 73 private buffers'","==74,'charged 74 private buffers'")
text=replace(text,"['scale',408]);g[2]=1","['scale',424]);g[2]*=2")
text=replace(text,'==1112','==1128',n=2);text=text.replace('HELPER408','HELPER424')
# Native stages are handled by the complete source-bound preparer below.
text=replace(text,"if a.native:\n        for tag", "if a.native:\n        raise RuntimeError('Use the source-bound native preparer for this composed stage')\n        for tag")
(local/'verify.py').write_text(text)
save(local/'PINS.json',{f.relative_to(local).as_posix():sha(f)for d in ['data','vendor']for f in(local/d).rglob('*')if f.is_file()})
subprocess.run([sys.executable,'-B',str(local/'verify.py'),'--work',str(out/'local-review')],check=True,stdout=(out/'local-review.log').open('w'),stderr=subprocess.STDOUT)
prov=rd(src/'new/BORROW-PROVIDERS.json')
for tag,pid in [('base','gauge44'),('extra','extra')]:
 wordpath=src/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';shutil.copy2(wordpath,src/f'new/borrow/inputs/CHANNEL408-WORD-{tag}.json.gz');shutil.copy2(local/f'data/WORD-{tag}.json.gz',wordpath)
 w=rd(wordpath);hs=sorted(set(range(224,704))-set(w['removed']));prov[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[]))for h in hs],'actual_paid_profile':w['report']['local_profile']}
save(src/'new/BORROW-PROVIDERS.json',prov)
f=src/'new/rebuild_borrow.py';text=f.read_text();anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
block="""    import channel424_extract
    second_parent=json.loads(gzip.decompress((D/'inputs'/f'CHANNEL408-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==second_parent
    second_transform=json.loads((D/'channel424/data/TRANSFORM.json').read_text())
    second_word=channel424_extract.apply(chain[-1],second_transform)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=second_word[k_])==channel424_extract.ALLOWED
    chain.append(second_word);steps.append('two-sided-helper424')
"""
f.write_text(replace(text,anchor,block+anchor))
f=src/'verify.py';text=f.read_text();anchor="run('two-sided-helper408-review',P/'new/borrow/channel408/verify.py','--work',work/'two-sided-helper408-review')"
f.write_text(replace(text,anchor,anchor+"\nrun('two-sided-helper424-review',P/'new/borrow/channel424/verify.py','--work',work/'two-sided-helper424-review')"))
save(src/'MANIFEST.json',tree(src));manifest=sha(src/'MANIFEST.json');count=len(rd(src/'MANIFEST.json'))
before_tree=tree(out/'source408');after_tree=tree(src)
changes={n:{'before':before_tree.get(n),'after':h}for n,h in after_tree.items()if before_tree.get(n)!=h}
save(out/'SOURCE-DERIVATION.json',dict(parent_head='51309592971e3b5be935599eed2a95404dc7781e',parent_manifest=sha(out/'source408/MANIFEST.json'),manifest_sha256=manifest,files=count,changes=changes))
# Narrow adapters: exact replacement counts prevent accidental dimension changes.
adapters={}
for name in ['prepare_channel_native.py','admit_channel408.py','channel_blocknorm.py']:
 text=(q/'tools'/name).read_text();original=text
 if name=='prepare_channel_native.py':
  text=replace(text,"SOURCE_SHA='56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'",f"SOURCE_SHA='{manifest}'")
  text=replace(text,'SOURCE_FILES=610',f'SOURCE_FILES={count}')
  text=replace(text,"SOURCE_COMMIT='two-sided-helper408-pr2894'","SOURCE_COMMIT='two-sided-helper408424-pr2908'")
  text=replace(text,"OLD_RECEIPT_SHA='dd36443f2789ffa6deca7210c76ada781e2b9b7e622a546b366f51a475faff3e'",f"OLD_RECEIPT_SHA='{sha(a.retained/'NATIVE-RECEIPT.json')}'")
  text=replace(text,"len(can['zero_buffers'])==73","len(can['zero_buffers'])==74")
 elif name=='admit_channel408.py':
  text=replace(text,"commit='two-sided-helper408-pr2894',manifest='56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83',helpers=408,source_file_count=610",f"commit='two-sided-helper408424-pr2908',manifest='{manifest}',helpers=408,source_file_count={count}")
  text=replace(text,'zero_buffers_allocated_and_cleared=73','zero_buffers_allocated_and_cleared=74')
  text=replace(text,"len(c.get('zero_buffers',[]))==73","len(c.get('zero_buffers',[]))==74")
  text=replace(text,'896*T+expected_helpers+8+73+2','896*T+expected_helpers+8+74+2')
  text=text.replace('73 private buffers','74 private buffers').replace('and 73 buffers','and 74 buffers')
 else:
  for old,new in [("len(allocated)==73","len(allocated)==74"),("'zero_buffers_allocated_and_cleared':73","'zero_buffers_allocated_and_cleared':74"),("r['zero_buffers_returned_to_zero']==73","r['zero_buffers_returned_to_zero']==74"),("live+8+408+73+2","live+8+408+74+2"),("len(mp)==73","len(mp)==74")]:text=replace(text,old,new)
  text=text.replace('all73 private','all74 private').replace('73distinct private','74distinct private')
  text=replace(text,"'zero_buffers':[live+416,live+489], 'coefficient':[live+489,live+491]", "'zero_buffers':[live+416,live+490], 'coefficient':[live+490,live+492]")
  text=replace(text,'physical=live+490','physical=live+492')
 path=out/name;path.write_text(text);adapters[name]=dict(before=sha(q/'tools'/name),after=sha(path))
save(out/'ADAPTER-DERIVATION.json',adapters)
print('PASS_COMPOSED_SOURCE_AND_LOCAL_CONTROLS',manifest,count,flush=True)
