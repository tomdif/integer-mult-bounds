"""Fresh Lean build, exact dependency pins and mathematical rejection controls.

Harness conventions follow the preceding terminal-refit-proof-boundary and
Gareth Davidson's common-label audit. No machine theorem is inferred here.
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
    parser=argparse.ArgumentParser()
    for name in ('lake','packages','work','out'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();lake=args.lake.resolve();work=args.work.resolve()
    need(not work.exists(),'fresh kernel work directory required')
    version=subprocess.check_output([str(lake.with_name('lean')),'--version'],text=True)
    need('4.32.2' in version,'Lean 4.32.2 required')
    dependencies=json.loads((HERE/'lean/lake-manifest.json').read_text())['packages']
    for dep in dependencies:
        path=args.packages.resolve()/dep['name']
        head=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        need(head==dep['rev'],'dependency revision: '+dep['name'])
        need(subprocess.run(['git','-C',str(path),'diff','--quiet','HEAD','--']).returncode==0,
             'modified dependency: '+dep['name'])
    shutil.copytree(HERE/'lean',work);shutil.copyfile(HERE/'Recursion.lean',work/'Recursion.lean')
    (work/'.lake').mkdir();(work/'.lake/packages').symlink_to(args.packages.resolve(),target_is_directory=True)
    env=dict(os.environ,PATH=str(lake.parent)+os.pathsep+os.environ.get('PATH',''))
    build=subprocess.run([str(lake),'build'],cwd=work,env=env,capture_output=True,text=True,timeout=900)
    output=build.stdout+build.stderr;(work/'BUILD.log').write_text(output)
    need(build.returncode==0,'Lean build failed: '+str(work/'BUILD.log'))
    reports=re.findall(r"'RefitRecursion\.([^']+)' depends on axioms:\s*\[([^\]]*)\]",output)
    axioms={name:sorted(s.strip() for s in raw.split(',') if s.strip()) for name,raw in reports}
    need(set(axioms)=={'properChild','deferredReservation','rowCapacity','elevenRows','heightBound','deferredHeight'},
         'all six axiom reports required')
    need(all(set(xs)<={'propext','Classical.choice','Quot.sound'} for xs in axioms.values()),'unexpected axiom')
    controls={
        'noncontracting_child':'example : 73 * (73 / 73 : Nat) < 73 := by norm_num\n',
        'too_small_deferral_tail':'example : 16 * ((128+63)/64 + (128+127)/128 + 11 : Nat) ≤ 128 := by norm_num\n',
        'floor_instead_of_ceiling':'example : (10576 : Nat) ≤ (10576 / 5376) * 5376 := by norm_num\n'}
    control_logs={}
    for name,code in controls.items():
        path=work/(name+'.lean');path.write_text('import Recursion\n'+code)
        result=subprocess.run([str(lake),'env','lean',path.name],cwd=work,env=env,
                              capture_output=True,text=True,timeout=180)
        log=result.stdout+result.stderr;(work/(name+'.log')).write_text(log)
        need(result.returncode!=0 and 'unsolved goals' in log and 'Unknown' not in log,
             'mathematical rejection required: '+name)
        control_logs[name]=sha256(log.encode()).hexdigest()
    result={'status':'PASS_SCOPED_RECURSIVE_ARITHMETIC_KERNEL','kernel_checked':True,
            'lean_version':version.strip(),'axioms':axioms,
            'dependencies':{d['name']:d['rev'] for d in dependencies},
            'source_sha256':sha256((HERE/'Recursion.lean').read_bytes()).hexdigest(),
            'build_log_sha256':sha256(output.encode()).hexdigest(),'rejected_controls':control_logs,
            'scope':'All-width arithmetic implications only; native event semantics, physical refinement and outer multiplication are not formalized.'}
    with args.out.open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=='__main__':main()
