# SPDX-License-Identifier: Apache-2.0
"""Complete pinned-source replay of the PR2917 terminal-frame refit.

Recipe/export conventions derive from Mason Hale PR2917 and Jeremy Diviney
PR2908. Fresh retained bootstrap by default; explicit authenticated reuse is
available. No fetch, publication, or selected-result mutation is performed.
"""
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent;V=P/'vendor/pr2917'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_bytes())
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 if not __debug__:raise RuntimeError('Assertions required')
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--retained',type=Path);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args();w=a.work.resolve();repo=a.repo.resolve();assert not w.exists()and not w.is_relative_to(P)and not P.is_relative_to(w);w.mkdir(parents=True)
 assert sha(V/'MANIFEST.json')=='55c46ddf2e3edc87dfe1ba3320947466d36980d457eb37f6cd6fba341dae0192'
 assert {f.relative_to(V).as_posix():sha(f)for f in V.rglob('*')if f.is_file()and f!=V/'MANIFEST.json'}==rd(V/'MANIFEST.json')
 spec=importlib.util.spec_from_file_location('credited_pr2917_reproducer',V/'reproduce.py');upstream=importlib.util.module_from_spec(spec);spec.loader.exec_module(upstream);parent=w/'pr2908';upstream.export(repo,parent)
 up=w/'parent-export/pr2894';core=up/'vendor/pr2857';retained=a.retained.resolve()if a.retained else w/'retained';integ=w/'integration';py=[sys.executable,'-B']
 recipe=[('export-pr2894',py+[parent/'reproduce.py','--repo',repo,'--work',w/'parent-export','--dry-run']),('saved-words-owners-moment',py+[P/'check_allocation.py','--predecessor',parent,'--words',P/'data','--allocation',V/'allocation','--bounds',core/'audit_relaxation.py','--out',w/'saved-check']),('export-pr2833',py+[up/'tools/materialize_source.py','--repo',repo,'--out',w/'pr2833'])]
 if not a.retained:recipe.append(('fresh-retained-bootstrap',py+[up/'tools/prepare_retained.py','--source',w/'pr2833','--out',retained,'--jobs','2']))
 recipe += [('four-kernel-stage',py+[core/'build_overlay.py','--source',w/'pr2833','--generator',core/'shared_kernel.py','--review',core/'review_four_groups.py','--candidate-dir',core/'words','--out',w/'source4']),('preload-stage',py+[up/'vendor/pm/build_pm_overlay.py','--overlay',w/'source4','--pm-dir',up/'vendor/pm','--out',w/'source-pm']),('parent-paired-stage',py+[parent/'tools/build_channel_overlay.py','--source',w/'source-pm','--local-package',parent,'--out',w/'source2908']),('extension-and-refit',py+[P/'build.py','--source2908',w/'source2908','--package2908',parent,'--retained',retained,'--out',integ]),('fresh-current-native',py+[integ/'adapters/prepare_extension_native.py','--source',integ/'source','--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',w/'native','--jobs','2']),('complete-admission',py+[integ/'adapters/admit_extension.py','--source',integ/'source','--fill',V/'allocation/FILL.json.gz','--order',V/'allocation/ORDER.json','--dispatch',V/'allocation/DISPATCH.json','--native-cache',w/'native/native-cache','--native-receipt',w/'native/NATIVE-RECEIPT.json','--work',w/'admission','--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',integ/'adapters/extension_blocknorm.py','--comparison-claim',parent/'CLAIM.json','--source-profile','paired-extension','--comparison-profile','pr2908','--jobs','1'])]
 save(w/'RECIPE.json',[dict(stage=n,command=list(map(str,c)))for n,c in recipe])
 if a.dry_run:print('PREFLIGHT_PINNED_PR2908_EXPORT_AND_FULL_RECIPE');return
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for name in ['PYTHONOPTIMIZE','PYTHONPATH','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(name,None)
 stages=[]
 for name,command in recipe:
  start=time.monotonic();log=w/(name+'.log')
  with log.open('w')as stream:r=subprocess.run(list(map(str,command)),env=env,stdout=stream,stderr=subprocess.STDOUT)
  stages.append(dict(stage=name,command=list(map(str,command)),exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));save(w/'STAGES.json',stages);assert r.returncode==0,'failed '+name+'; see '+str(log);print('PASS',name,flush=True)
 result=rd(w/'admission/RESULT.json');release=rd(w/'admission/release/RELEASE-RECEIPT.json');target=Q(rd(w/'saved-check/RESULT.json')['kappa'])
 assert result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE'and Q(result['kappa'])==Q(release['kappa_decimal'])==target
 assert sha(w/'admission/release/RELEASE-RECEIPT.json')==result['release_receipt_sha256']and result['package_manifest_sha256']==release['manifest_sha256']
 receipt=dict(status='PASS_TERMINAL_REFIT_COMPLETE_REPLAY',kappa=str(target),kappa_decimal=release['kappa_decimal'],source_manifest_sha256=result['source_manifest_sha256'],release_receipt_sha256=result['release_receipt_sha256'],native_receipt_sha256=sha(w/'native/NATIVE-RECEIPT.json'),explicit_retained_reuse=bool(a.retained),stages=stages,scope='Conditional finite supplier and modern outer release; inherited all-size theorem hypotheses remain.')
 save(w/'RESULT.json',receipt);print(receipt['status'],release['kappa_decimal'])
if __name__=='__main__':main()
