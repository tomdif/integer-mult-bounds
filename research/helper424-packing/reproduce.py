# SPDX-License-Identifier: Apache-2.0
"""Pinned-source complete four-channel replay; no network or publication.

Default: rebuild all retained native/parent evidence. --retained explicitly
reuses an existing preparation, with complete source/cache/stage authentication.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'vendor/round1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_bytes())
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 if not __debug__:raise RuntimeError('Assertions required')
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--retained',type=Path);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args();w=a.work.resolve();assert not w.exists()and not w.is_relative_to(P)and not P.is_relative_to(w);w.mkdir(parents=True)
 assert sha(R/'MANIFEST.json')=='8dd8e55c8cce4d53431035e0ba9a8d11eb34cccff462e4ae67034c767f51b342'
 assert all(sha(R/n)==h for n,h in rd(R/'MANIFEST.json').items())
 s=importlib.util.spec_from_file_location('round1_reproducer',R/'reproduce_candidate.py');module=importlib.util.module_from_spec(s);s.loader.exec_module(module)
 up=w/'pr2894';pred=w/'pr2908';module.export(a.repo.resolve(),'18d03c447886895ef9abf888398178e0428533ca','research/shared-kernel-packing',up);module.export(a.repo.resolve(),'51309592971e3b5be935599eed2a95404dc7781e','research/two-sided-helper-extraction',pred)
 assert sha(up/'MANIFEST.json')=='3cb842b93dd3b0707ceea825bef2afeaa68f8df0d554867761b4752b69077293' and sha(pred/'MANIFEST.json')=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'
 core=up/'vendor/pr2857';retained=a.retained.resolve()if a.retained else w/'retained';old=w/'round1-integration';integ=w/'integration';py=[sys.executable,'-B'];repo=a.repo.resolve()
 recipe=[('saved-words-owners-moment',py+[P/'check_allocation.py','--predecessor',pred,'--words',P/'data','--allocation',P/'allocation','--bounds',core/'audit_relaxation.py','--out',w/'saved-check']),('materialize',py+[up/'tools/materialize_source.py','--repo',repo,'--out',w/'pr2833'])]
 if not a.retained:recipe.append(('retained',py+[up/'tools/prepare_retained.py','--source',w/'pr2833','--out',retained,'--jobs','2']))
 recipe += [('four-kernels',py+[core/'build_overlay.py','--source',w/'pr2833','--generator',core/'shared_kernel.py','--review',core/'review_four_groups.py','--candidate-dir',core/'words','--out',w/'source4']),('preload',py+[up/'vendor/pm/build_pm_overlay.py','--overlay',w/'source4','--pm-dir',up/'vendor/pm','--out',w/'source-pm']),('second-channel',py+[R/'try_second_extraction.py','--source',pred,'--work',w/'second-channel']),('compose-round1',py+[R/'build424_integration.py','--predecessor',pred,'--pm-source',w/'source-pm','--words',w/'second-channel','--retained',retained,'--out',old]),('new-channels',py+[P/'extract_tree_channels.py','--predecessor',pred,'--words',R/'data','--out',w/'new-channels']),('terminal-refit',py+[P/'terminal_refit.py','--generate','--vendor',pred/'vendor','--words',w/'new-channels/416','--work',w/'terminal-refit']),('compose-final',py+[P/'build_channels.py','--source',old/'source','--adapters',old,'--words',w/'new-channels','--refit',w/'terminal-refit','--retained',retained,'--out',integ]),('native',py+[integ/'prepare_channel_native.py','--source',integ/'source','--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',integ/'native','--jobs','2']),('admission',py+[integ/'admit_channel408.py','--source',integ/'source','--fill',P/'allocation/FILL.json.gz','--order',P/'allocation/ORDER.json','--dispatch',P/'allocation/DISPATCH.json','--native-cache',integ/'native/native-cache','--native-receipt',integ/'native/NATIVE-RECEIPT.json','--work',integ/'admission','--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',integ/'channel_blocknorm.py','--comparison-claim',up/'CLAIM.json','--source-profile','channel408','--comparison-profile','pr2894','--jobs','1'])]
 save(w/'RECIPE.json',[dict(stage=n,command=list(map(str,c)))for n,c in recipe])
 if a.dry_run:print('PREFLIGHT_PINNED_SOURCE_EXPORT_AND_RECIPE');return
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for n in ['PYTHONOPTIMIZE','PYTHONPATH','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(n,None)
 stages=[]
 for name,cmd in recipe:
  start=time.monotonic();log=w/(name+'.log')
  with log.open('w')as f:r=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(stage=name,command=list(map(str,cmd)),exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));save(w/'STAGES.json',stages);assert r.returncode==0,'failed '+name+'; see '+str(log)
  if name=='second-channel':
   for tag in ['base','extra']:
    generated=w/f'second-channel/{tag}-424-52.json.gz';saved=R/f'data/WORD-{tag}.json.gz';assert json.loads(gzip.decompress(generated.read_bytes()))==json.loads(gzip.decompress(saved.read_bytes()));shutil.copy2(saved,generated)
  if name=='terminal-refit':
   for tag in ['base','extra']:assert json.loads(gzip.decompress((w/f'terminal-refit/WORD-{tag}.json.gz').read_bytes()))==json.loads(gzip.decompress((P/f'data/WORD-{tag}.json.gz').read_bytes()))
  print('PASS',name,flush=True)
 result=rd(integ/'admission/RESULT.json');release=rd(integ/'admission/release/RELEASE-RECEIPT.json');expected=Q(rd(w/'saved-check/RESULT.json')['kappa'])
 assert result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE'and Q(result['kappa'])==Q(release['kappa_decimal'])==expected
 assert sha(integ/'admission/release/RELEASE-RECEIPT.json')==result['release_receipt_sha256']
 receipt=dict(status='PASS_FOUR_CHANNEL_COMPLETE_REPLAY',kappa=str(expected),kappa_decimal=release['kappa_decimal'],explicit_retained_reuse=bool(a.retained),source_manifest_sha256=result['source_manifest_sha256'],native_receipt_sha256=sha(integ/'native/NATIVE-RECEIPT.json'),release_receipt_sha256=result['release_receipt_sha256'],stages=stages,scope='Complete conditional finite supplier and modern outer release. Inherited all-size theorem hypotheses remain.')
 save(w/'RESULT.json',receipt);print(receipt['status'],release['kappa_decimal'],flush=True)
if __name__=='__main__':main()
