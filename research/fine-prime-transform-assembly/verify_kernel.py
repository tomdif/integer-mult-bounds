"""Fresh recovery-only Lean build; source-derived from refit-proof-closure.

No inherited theorem objects for Recovery.lean are used. Cached mathlib
dependencies are revision checked, as in the preceding kernel verifier.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    ap=argparse.ArgumentParser()
    for name in ('lake','packages','work','out'):ap.add_argument('--'+name,type=Path,required=True)
    a=ap.parse_args();lake=a.lake.resolve();work=a.work.resolve()
    need(not work.exists(),'fresh kernel directory required')
    version=subprocess.check_output([str(lake.with_name('lean')),'--version'],text=True)
    need('4.32.2' in version,'Lean 4.32.2 required')
    dependencies=json.loads((HERE/'lean/lake-manifest.json').read_text())['packages']
    for dep in dependencies:
        path=a.packages.resolve()/dep['name']
        head=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        need(head==dep['rev'],'dependency revision: '+dep['name'])
        need(subprocess.run(['git','-C',str(path),'diff','--quiet','HEAD','--']).returncode==0,'modified dependency '+dep['name'])
    shutil.copytree(HERE/'lean',work);shutil.copyfile(HERE/'Recovery.lean',work/'Recovery.lean')
    (work/'.lake').mkdir();(work/'.lake/packages').symlink_to(a.packages.resolve(),target_is_directory=True)
    env=dict(os.environ,PATH=str(lake.parent)+os.pathsep+os.environ.get('PATH',''))
    build=subprocess.run([str(lake),'build'],cwd=work,env=env,capture_output=True,text=True,timeout=900)
    output=build.stdout+build.stderr;(work/'BUILD.txt').write_text(output)
    need(build.returncode==0,'Lean build failed: '+str(work/'BUILD.txt'))
    reports=re.findall(r"'OuterRecovery\.([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)
    axioms={name:sorted(x.strip() for x in raw.split(',') if x.strip()) for name,raw in reports}
    need(set(axioms)=={'productError','scaleEnvelope','quarterRadius','roundOfQuarter','exactRecovery'},'five axiom reports')
    need(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in axioms.values()),'unexpected axiom')
    controls={
        'one_bit_accuracy_is_insufficient':'example : (16 : Rat) * 4^2 * 4 * (4*4+1) * (1/4) < 1/4 := by norm_num\n',
        'nearest_integer_without_radius':'example : round (3 / 4 : Rat) = 0 := by norm_num [round_eq_iff]\n',
        'omitted_S_normalization':'example : (3 / 5 : Rat) * 5 = 3 / 5 := by norm_num\n'}
    logs={}
    for name,code in controls.items():
        path=work/(name+'.lean');path.write_text('import Recovery\n'+code)
        result=subprocess.run([str(lake),'env','lean',path.name],cwd=work,env=env,capture_output=True,text=True,timeout=180)
        log=result.stdout+result.stderr;(work/(name+'.txt')).write_text(log)
        need(result.returncode!=0 and 'unsolved goals' in log and 'Unknown' not in log,'mathematical rejection '+name)
        logs[name]=sha256(log.encode()).hexdigest()
    receipt=dict(status='PASS_RECOVERY_IMPLICATION_KERNEL',kernel_checked=True,lean_version=version.strip(),
                 axioms=axioms,dependencies={d['name']:d['rev'] for d in dependencies},
                 source_sha256=sha256((HERE/'Recovery.lean').read_bytes()).hexdigest(),
                 build_log_sha256=sha256(output.encode()).hexdigest(),rejected_controls=logs,
                 scope='The error envelope and nearest-integer recovery implication only. The approximation and complexity premises of the outer algorithms are not formalized.')
    with a.out.open('x') as out:json.dump(receipt,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps(receipt,sort_keys=True,indent=2))

if __name__=='__main__':main()
