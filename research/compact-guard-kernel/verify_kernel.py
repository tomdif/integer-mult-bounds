"""Fresh kernel build for the guard/repair proof, with false-statement controls.

Workflow adapted from the preceding recovery verifier. Cached dependencies
are revision checked; no cached Guard theorem object is reused.
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
NAMES={'guardBounds','flipCorrect','loadedControl','parityCancellation','pairedFlipCorrect',
       'shuttle','sourcePreserved','packedUpdates','packBounds','packedNoWrap',
       'singleGuardDensity','productFailure','allGuardDensity','exceptionalDensity','controlledAdd',
       'rawPreservesGood','repairEquals','repairCorrect','repairBijective'}


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
        need(head==dep['rev'],'dependency revision '+dep['name'])
        need(subprocess.run(['git','-C',str(path),'diff','--quiet','HEAD','--']).returncode==0,
             'modified dependency '+dep['name'])
    shutil.copytree(HERE/'lean',work);shutil.copyfile(HERE/'Guard.lean',work/'Guard.lean')
    (work/'.lake').mkdir();(work/'.lake/packages').symlink_to(a.packages.resolve(),target_is_directory=True)
    env=dict(os.environ,PATH=str(lake.parent)+os.pathsep+os.environ.get('PATH',''))
    build=subprocess.run([str(lake),'build'],cwd=work,env=env,capture_output=True,text=True,timeout=900)
    output=build.stdout+build.stderr;(work/'BUILD.txt').write_text(output)
    need(build.returncode==0,'Lean build failed: '+str(work/'BUILD.txt'))
    reports=re.findall(r"'CompactGuard\.([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)
    axioms={name:sorted(x.strip() for x in raw.split(',') if x.strip()) for name,raw in reports}
    for name in re.findall(r"'CompactGuard\.([^']+)' does not depend on any axioms",output):
        need(name not in axioms,'duplicate axiom report');axioms[name]=[]
    need(set(axioms)==NAMES,'all nineteen axiom reports')
    need(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in axioms.values()),'unexpected axiom')
    controls={
        'scratch_guard_omitted':
            'example : CompactGuard.flip 2 32 1 1 17 = (1,16) := by norm_num [CompactGuard.flip]\n',
        'loaded_maximum_excluded':
            'example : (2+1 : Int) < 4-1 := by norm_num\n',
        'loaded_parity_omitted':
            'example : (((0+0%2)%2+0%2)%2 : Int) = (0+1)%2 := by norm_num\n',
        'forward_instead_of_inverse':
            'def cycle : Fin 3 ≃ Fin 3 := (Equiv.swap 0 1).trans (Equiv.swap 1 2)\n'
            'example : cycle (cycle 0) = 0 := by decide\n'}
    logs={}
    for name,code in controls.items():
        path=work/(name+'.lean');path.write_text('import Guard\n'+code)
        result=subprocess.run([str(lake),'env','lean',path.name],cwd=work,env=env,
                              capture_output=True,text=True,timeout=180)
        log=result.stdout+result.stderr;(work/(name+'.txt')).write_text(log)
        mathematical=('unsolved goals' in log or
                      re.search(r'Tactic `decide` proved.*\bis false',log,re.S) is not None)
        need(result.returncode!=0 and mathematical and 'Unknown' not in log,
             'mathematical rejection '+name+': '+log)
        logs[name]=sha256(log.encode()).hexdigest()
    receipt=dict(status='PASS_COMPACT_GUARD_REPAIR_KERNEL',kernel_checked=True,
        lean_version=version.strip(),axioms=axioms,
        dependencies={d['name']:d['rev'] for d in dependencies},
        source_sha256=sha256((HERE/'Guard.lean').read_bytes()).hexdigest(),
        build_log_sha256=sha256(output.encode()).hexdigest(),rejected_controls=logs,
        scope='Quantified guarded arithmetic, packed bounds, density inequalities and selective permutation repair. No tape-cost, native-dispatch, analytic-transform or complete multiplication theorem is formalized.')
    with a.out.open('x') as out:json.dump(receipt,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps(receipt,sort_keys=True,indent=2))


if __name__=='__main__':main()
