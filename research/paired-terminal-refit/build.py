# SPDX-License-Identifier: Apache-2.0
"""Preserve PR2917's complete source and append four exact terminal refits.
Mason Hale/PR2917 and Jeremy Diviney/PR2908 retain extraction/integration credit.
"""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;V=P/'vendor/pr2917'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def tree(p):return {f.relative_to(p).as_posix():sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f!=p/'MANIFEST.json'}
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source2908',type=Path,required=True);ap.add_argument('--package2908',type=Path,required=True);ap.add_argument('--retained',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 if not __debug__:raise RuntimeError('Assertions required')
 assert sha(V/'MANIFEST.json')=='55c46ddf2e3edc87dfe1ba3320947466d36980d457eb37f6cd6fba341dae0192' and tree(V)==rd(V/'MANIFEST.json')
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);py=[sys.executable,'-B']
 def run(name,args):
  with(out/(name+'.log')).open('w')as log:subprocess.run(list(map(str,py+args)),check=True,stdout=log,stderr=subprocess.STDOUT)
 run('upstream-overlay',[V/'tools/build_extension.py','--source',a.source2908,'--local-package',V,'--out',out/'parent-source'])
 parent=out/'parent-source';oldsha=sha(parent/'MANIFEST.json');assert oldsha=='98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'
 run('upstream-adapters',[V/'tools/derive_adapters.py','--parent-package',a.package2908,'--source',parent,'--source-manifest',oldsha,'--retained-receipt',a.retained/'NATIVE-RECEIPT.json','--out',out/'parent-adapters'])
 run('generate',[P/'terminal_refit.py','--generate','--vendor',V/'vendor','--words',V/'data','--work',out/'generated'])
 src=out/'source';shutil.copytree(parent,src);local=src/'new/borrow/terminal_refit';(local/'data').mkdir(parents=True);shutil.copytree(V/'vendor',local/'vendor');shutil.copy2(P/'terminal_refit.py',local/'terminal_refit.py');shutil.copy2(P/'terminal_refit.py',src/'new/borrow/terminal_refit_apply.py')
 providers=rd(src/'new/BORROW-PROVIDERS.json')
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  current=src/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';assert rd(current)==rd(out/f'generated/PARENT-{tag}.json.gz')
  assert rd(out/f'generated/WORD-{tag}.json.gz')==rd(P/f'data/WORD-{tag}.json.gz')
  for prefix in ['PARENT','WORD']:shutil.copy2(out/f'generated/{prefix}-{tag}.json.gz',local/f'data/{prefix}-{tag}.json.gz')
  shutil.copy2(out/f'generated/PATCH-{tag}.json',local/f'data/PATCH-{tag}.json');shutil.copy2(current,src/f'new/borrow/inputs/PRE-REFIT-WORD-{tag}.json.gz');shutil.copy2(local/f'data/WORD-{tag}.json.gz',current)
  providers[pid]['actual_paid_profile']=rd(current)['report']['local_profile']
 save(local/'PINS.json',{f.relative_to(local).as_posix():sha(f)for d in ['vendor','data']for f in(local/d).rglob('*')if f.is_file()})
 run('local-review',[local/'terminal_refit.py','--work',out/'local-review'])
 f=src/'new/rebuild_borrow.py';s=f.read_text();anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
 block="""    import terminal_refit_apply
    refit_parent=json.loads(gzip.decompress((D/'inputs'/f'PRE-REFIT-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==refit_parent
    refit_patch=json.loads((D/'terminal_refit/data'/f'PATCH-{wt}.json').read_text())
    refit_word=terminal_refit_apply.apply(chain[-1],refit_patch)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=refit_word[k_])==terminal_refit_apply.ALLOWED
    chain.append(refit_word);steps.append('four-commuting-terminal-refits')
"""
 f.write_text(rep(s,anchor,block+anchor));f=src/'verify.py';s=f.read_text();anchor="run('paired-extension-review',P/'new/borrow/paired-extension/verify.py','--work',work/'paired-extension-review')";f.write_text(rep(s,anchor,anchor+"\nrun('terminal-frame-refit-review',P/'new/borrow/terminal_refit/terminal_refit.py','--work',work/'terminal-frame-refit-review')"))
 save(src/'new/BORROW-PROVIDERS.json',providers);save(src/'MANIFEST.json',tree(src));newsha=sha(src/'MANIFEST.json');count=len(rd(src/'MANIFEST.json'));adapters=out/'adapters';adapters.mkdir();changes={}
 for name in ['prepare_extension_native.py','admit_extension.py','extension_blocknorm.py']:
  source=out/'parent-adapters'/name;s=source.read_text()
  if name=='prepare_extension_native.py':s=rep(s,f"SOURCE_SHA='{oldsha}'",f"SOURCE_SHA='{newsha}'");s=rep(s,'SOURCE_FILES=632',f'SOURCE_FILES={count}');s=rep(s,"SOURCE_COMMIT='paired-helper-extension-pr2908'","SOURCE_COMMIT='paired-terminal-refit-pr2917'")
  elif name=='admit_extension.py':s=rep(s,f"commit='paired-helper-extension-pr2908',manifest='{oldsha}',helpers=408,source_file_count=632",f"commit='paired-terminal-refit-pr2917',manifest='{newsha}',helpers=408,source_file_count={count}")
  dest=adapters/name;dest.write_text(s);changes[name]=dict(before=sha(source),after=sha(dest))
 before=tree(parent);after=tree(src);save(out/'SOURCE-DERIVATION.json',dict(parent_head='224bd5e56041c40078ff6b5fa7393733a215de5c',parent_manifest_sha256=oldsha,source_manifest_sha256=newsha,files=count,changes={n:dict(before=before.get(n),after=h)for n,h in after.items()if before.get(n)!=h}));save(out/'ADAPTER-DERIVATION.json',changes)
 print('PASS_SOURCE_BOUND_FOUR_TERMINAL_REFITS',newsha,count,flush=True)
if __name__=='__main__':main()
