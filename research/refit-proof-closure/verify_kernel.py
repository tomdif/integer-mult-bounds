"""Fresh Lean build and false-statement controls; adapted from predecessor."""
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
    args=ap.parse_args();lake=args.lake.resolve();work=args.work.resolve()
    need(not work.exists(),'fresh kernel directory required')
    version=subprocess.check_output([str(lake.with_name('lean')),'--version'],text=True)
    need('4.32.2' in version,'Lean 4.32.2 required')
    dependencies=json.loads((HERE/'lean/lake-manifest.json').read_text())['packages']
    for dep in dependencies:
        path=args.packages.resolve()/dep['name']
        head=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        need(head==dep['rev'],'dependency revision: '+dep['name'])
        need(subprocess.run(['git','-C',str(path),'diff','--quiet','HEAD','--']).returncode==0,
             'modified dependency: '+dep['name'])
    shutil.copytree(HERE/'lean',work);shutil.copyfile(HERE/'Closure.lean',work/'Closure.lean')
    (work/'.lake').mkdir();(work/'.lake/packages').symlink_to(args.packages.resolve(),target_is_directory=True)
    env=dict(os.environ,PATH=str(lake.parent)+os.pathsep+os.environ.get('PATH',''))
    build=subprocess.run([str(lake),'build'],cwd=work,env=env,capture_output=True,text=True,timeout=900)
    output=build.stdout+build.stderr;(work/'BUILD.log').write_text(output)
    need(build.returncode==0,'Lean build failed: '+str(work/'BUILD.log'))
    reports=re.findall(r"'RefitClosure\.([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)
    axioms={name:sorted(s.strip() for s in raw.split(',') if s.strip()) for name,raw in reports}
    need(set(axioms)=={'blockFactorization','conditionalShiftInverse','normalizedSandwichScale',
                      'weightedClosure','oldScanExceedsTarget'},'all five axiom reports')
    need(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in axioms.values()),'unexpected axiom')
    controls={
        'omit_inverse_controls':'example : ((1 + 1 : Int) + 1) = 1 + 1 := by norm_num\n',
        'omit_fourier_scale':'example : (1 / 5 : Rat) = 1 := by norm_num\n',
        'reverse_old_scan_margin':'example : (1 : Rat) - (1025 / 1024) / 10^104 ≤ 1 - (1722052684227397319529 / 10^24 - 1 / 10^46 - 1 / 10^70) := by norm_num\n'}
    control_logs={}
    for name,code in controls.items():
        path=work/(name+'.lean');path.write_text('import Closure\n'+code)
        result=subprocess.run([str(lake),'env','lean',path.name],cwd=work,env=env,
                              capture_output=True,text=True,timeout=180)
        log=result.stdout+result.stderr;(work/(name+'.log')).write_text(log)
        need(result.returncode!=0 and 'unsolved goals' in log and 'Unknown' not in log,
             'mathematical rejection required: '+name)
        control_logs[name]=sha256(log.encode()).hexdigest()
    receipt={'status':'PASS_SCOPED_REFIT_CLOSURE_KERNEL','kernel_checked':True,
             'lean_version':version.strip(),'axioms':axioms,
             'dependencies':{d['name']:d['rev'] for d in dependencies},
             'source_sha256':sha256((HERE/'Closure.lean').read_bytes()).hexdigest(),
             'build_log_sha256':sha256(output.encode()).hexdigest(),'rejected_controls':control_logs,
             'scope':'Five algebraic/arithmetic implications only. No Fourier construction, tape semantics or complete multiplication theorem is formalized.'}
    with args.out.open('x') as out:json.dump(receipt,out,sort_keys=True,indent=2);out.write('\n')
    print(json.dumps(receipt,sort_keys=True,indent=2))


if __name__=='__main__':main()
