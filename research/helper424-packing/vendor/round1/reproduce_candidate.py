# SPDX-License-Identifier: Apache-2.0
"""Replay the helper408+424 candidate from pinned Git sources and saved owners.

The native/owner/outer mathematical predicates are retained. Exact unchanged
retained evidence may be explicitly reused; by default it is rebuilt fresh.
No network, publication, selected-result changes, or source edits are performed.
"""
import argparse,gzip,hashlib,io,json,os,subprocess,sys,tarfile,time
from fractions import Fraction as Q
from pathlib import Path,PurePosixPath
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def export(repo,head,prefix,out):
 raw=subprocess.check_output(['git','-C',str(repo),'archive',head,prefix]);out.mkdir()
 pref=PurePosixPath(prefix)
 with tarfile.open(fileobj=io.BytesIO(raw))as ar:
  for f in ar.getmembers():
   r=PurePosixPath(f.name)
   assert not r.is_absolute()and'..'not in r.parts and'\\'not in f.name
   if f.isdir()and(r==pref or r in pref.parents):continue
   assert r.is_relative_to(pref)and(f.isfile()or f.isdir())
   dest=out/r.relative_to(pref)
   if f.isdir():dest.mkdir(parents=True,exist_ok=True)
   else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(ar.extractfile(f).read())
 pins=read(out/'MANIFEST.json')
 assert {f.relative_to(out).as_posix():sha(f)for f in out.rglob('*')if f.is_file()and f!=out/'MANIFEST.json'}==pins

def main():
 if not __debug__:raise RuntimeError('Assertions must be enabled')
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--retained',type=Path);ap.add_argument('--dry-run',action='store_true');a=ap.parse_args()
 w=a.work.resolve();assert __debug__ and not w.exists()and not w.is_relative_to(P)and not P.is_relative_to(w);w.mkdir(parents=True)
 up=w/'pr2894';pred=w/'pr2908';export(a.repo.resolve(),'18d03c447886895ef9abf888398178e0428533ca','research/shared-kernel-packing',up);export(a.repo.resolve(),'51309592971e3b5be935599eed2a95404dc7781e','research/two-sided-helper-extraction',pred)
 assert sha(up/'MANIFEST.json')=='3cb842b93dd3b0707ceea825bef2afeaa68f8df0d554867761b4752b69077293'
 assert sha(pred/'MANIFEST.json')=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f'
 pins=read(P/'DATA-PINS.json');assert all(sha(P/name)==digest for name,digest in pins.items())
 core=up/'vendor/pr2857';retained=a.retained.resolve()if a.retained else w/'retained';integ=w/'integration';words=w/'words';py=[sys.executable,'-B']
 recipe=[('saved-owner-moment',py+[P/'check_saved_candidate.py','--predecessor',pred,'--bounds-package',up]),('materialize',py+[up/'tools/materialize_source.py','--repo',a.repo.resolve(),'--out',w/'pr2833'])]
 if not a.retained:recipe.append(('retained',py+[up/'tools/prepare_retained.py','--source',w/'pr2833','--out',retained,'--jobs','2']))
 recipe += [('four-kernels',py+[core/'build_overlay.py','--source',w/'pr2833','--generator',core/'shared_kernel.py','--review',core/'review_four_groups.py','--candidate-dir',core/'words','--out',w/'source4']),('preload',py+[up/'vendor/pm/build_pm_overlay.py','--overlay',w/'source4','--pm-dir',up/'vendor/pm','--out',w/'source-pm']),('second-channel',py+[P/'try_second_extraction.py','--source',pred,'--work',words]),('compose',py+[P/'build424_integration.py','--predecessor',pred,'--pm-source',w/'source-pm','--words',words,'--retained',retained,'--out',integ]),('native',py+[integ/'prepare_channel_native.py','--source',integ/'source','--retained-cache',retained/'native-cache','--retained-receipt',retained/'NATIVE-RECEIPT.json','--out',integ/'native','--jobs','2']),('admission',py+[integ/'admit_channel408.py','--source',integ/'source','--fill',P/'allocation/FILL.json.gz','--order',P/'allocation/ORDER.json','--dispatch',P/'allocation/DISPATCH.json','--native-cache',integ/'native/native-cache','--native-receipt',integ/'native/NATIVE-RECEIPT.json','--work',integ/'admission','--replica-helper-dir',core/'vendor/pr2839','--reconstructor',core/'vendor/pr2839/reconstruct_replica.py','--blocknorm-checker',integ/'channel_blocknorm.py','--comparison-claim',up/'CLAIM.json','--source-profile','channel408','--comparison-profile','pr2894','--jobs','1'])]
 (w/'RECIPE.json').write_text(json.dumps([{'stage':n,'command':list(map(str,c))}for n,c in recipe],indent=2)+'\n')
 if a.dry_run:print('PREFLIGHT_ONLY_PINNED_SOURCE_EXPORT_AND_RECIPE');return
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
 for n in ['PYTHONOPTIMIZE','PYTHONPATH','WITNESS_SPEC','WITNESS_DISCOVER','WITNESS_RECORD']:env.pop(n,None)
 stages=[]
 for name,cmd in recipe:
  log=w/(name+'.log');start=time.monotonic()
  with log.open('w')as f:r=subprocess.run(list(map(str,cmd)),env=env,stdout=f,stderr=subprocess.STDOUT)
  stages.append(dict(stage=name,exit_code=r.returncode,seconds=time.monotonic()-start,log_sha256=sha(log)));(w/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n')
  assert r.returncode==0,'failed '+name+'; see '+str(log)
  if name=='second-channel':
   for tag in ['base','extra']:
    assert json.loads(gzip.decompress((words/f'{tag}-424-52.json.gz').read_bytes()))==json.loads(gzip.decompress((P/f'data/WORD-{tag}.json.gz').read_bytes()))
  print('PASS',name,flush=True)
 result=read(integ/'admission/RESULT.json');release=read(integ/'admission/release/RELEASE-RECEIPT.json');target=Q(read(P/'MOMENT424.json')['lower'])-Q(1,10**46)-Q(1,10**70)
 assert result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE'and release['status']=='PASS_RELEASE'
 assert Q(result['kappa'])==Q(release['kappa_decimal'])==target>Q(read(pred/'CLAIM.json')['kappa'])
 assert sha(integ/'admission/release/RELEASE-RECEIPT.json')==result['release_receipt_sha256']
 receipt=dict(status='PASS_HELPER408424_COMPLETE_REPLAY',kappa=str(target),explicit_retained_reuse=bool(a.retained),native_receipt_sha256=sha(integ/'native/NATIVE-RECEIPT.json'),release_receipt_sha256=sha(integ/'admission/release/RELEASE-RECEIPT.json'),scope='Conditional finite supplier and outer certificate; inherited all-size hypotheses remain.',stages=stages)
 (w/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],str(target))
if __name__=='__main__':main()
