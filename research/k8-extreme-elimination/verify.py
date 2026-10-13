"""Offline focused replay. Full discovery censuses are frozen, not rerun here."""
from pathlib import Path
from collections import Counter
import argparse,copy,gzip,hashlib,importlib.util,json,os,subprocess,sys

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
if not __debug__:raise RuntimeError('Run with assertions enabled')
def read(p):
    raw=p.read_bytes()
    return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def run(script,env,log):
    with log.open('w')as f:
        subprocess.run([sys.executable,'-B',str(script)],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);args=ap.parse_args()
    W=args.work.resolve()
    assert not W.is_relative_to(ROOT.resolve()),'Use a fresh directory outside the checkout'
    W.mkdir(parents=True,exist_ok=False)
    actual={str(q.relative_to(P)):sha(q)for q in P.rglob('*')if q.is_file()and q.name!='MANIFEST.json'and'__pycache__'not in q.parts}
    assert actual==read(P/'MANIFEST.json'),'Package bytes changed'
    for rel,pin in read(P/'DEPENDENCY-PINS.json').items():
        assert not Path(rel).is_absolute() and (ROOT/rel).resolve().is_relative_to(ROOT.resolve())
        assert sha(ROOT/rel)==pin,'Dependency changed: '+rel
    env=dict(os.environ,EXTREME_WORK=str(W),PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    retained=ROOT/'research/x54-mixed-allocation'
    with(W/'retained-bindings.log').open('w')as f:
        subprocess.run([sys.executable,'-B','-c',
          'import sys;sys.path.insert(0,sys.argv[1]);from package import validate;print(validate())',str(retained)],
          env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
    print('PASS retained source/package bindings',flush=True)
    summary={}
    for name in ['elimination','dynamic','reorder','interfaces','joint']:
        rows=read(P/'evidence'/name/'RESULTS.json.gz')
        summary[name]=dict(cases=len(rows),statuses=dict(Counter(r['status']for r in rows)),
          attempts=sum(len(r.get('attempts',[]))for r in rows))
    assert summary=={
      'elimination':{'cases':237,'statuses':{'compiler_rejected':121,'frame_infeasible':116},'attempts':0},
      'dynamic':{'cases':468,'statuses':{'compiler_rejected':273,'frame_infeasible':195},'attempts':0},
      'reorder':{'cases':195,'statuses':{'completed':195},'attempts':231},
      'interfaces':{'cases':195,'statuses':{'completed':195},'attempts':390},
      'joint':{'cases':195,'statuses':{'completed':195},'attempts':231}}
    for name in ['reorder','interfaces','joint']:
        rows=read(P/'evidence'/name/'RESULTS.json.gz')
        assert all(a['status']in ['OrderRejected','Infeasible']for r in rows for a in r['attempts'])
    (W/'dynamic').mkdir();(W/'dynamic/RESULTS.json').write_text(json.dumps(read(P/'evidence/dynamic/RESULTS.json.gz')))
    run(P/'code/check_r464.py',env,W/'r464.log')
    for name in ['R464-SCALAR-ONLY.json.gz','R464-COMPENSATION.json.gz']:
        assert read(W/name)==read(P/'data'/name),'Reconstructed scalar artifact differs: '+name
    assert read(W/'R464-RESULT.json')==read(P/'evidence/R464-RESULT.json')
    print('PASS R464: exact forward/dual map, explicit compensation, two scalar controls, geometry rejection',flush=True)
    word=read(W/'R464-SCALAR-ONLY.json.gz');cold=copy.deepcopy(word);cold['start_extra']={};cold['helper_final']={}
    assert cold==read(P/'data/R464-COLD-FULL-SCALAR-ONLY.json.gz')
    (W/'R464-COLD-FULL-SCALAR-ONLY.json.gz').write_bytes(gzip.compress(canonical(cold),mtime=0))
    sp=importlib.util.spec_from_file_location('independent_obstruction',P/'code/independent_obstruction.py')
    checker=importlib.util.module_from_spec(sp);sp.loader.exec_module(checker)
    for prefix,w in [('',word),('COLD-FULL-',cold)]:
        name='R464-'+prefix+'OBSTRUCTION.json';target=W/name
        ee=dict(env,R464_INPUT=str(W/('R464-'+prefix+'SCALAR-ONLY.json.gz')),OBSTRUCTION_OUT=str(target))
        run(P/'code/find_obstruction.py',ee,W/('find-'+prefix+'obstruction.log'))
        assert read(target)==read(P/'data'/name)
        result=checker.check_with_controls(w,read(target))
        expected='COLD-OBSTRUCTION-CHECK.json'if prefix else'OBSTRUCTION-CHECK.json'
        assert result==read(P/'evidence'/expected)
    print('PASS both independent obstruction checks and six controls',flush=True)
    for script in ['screen_geometry.py','check_controls.py']:
        run(P/'code'/script,env,W/(script+'.log'))
    for name in ['GEOMETRY-CEILINGS.json','CONTROLS.json']:
        assert read(W/name)==read(P/'evidence'/name)
    print('PASS fixed-word ceilings: two independent exact moment engines and scheduling controls',flush=True)
    run(P/'rank_network/verify.py',env,W/'rank-network.log')
    result=dict(status='PASS_EXTREME_SCALAR_AND_RANK_NETWORK_RESEARCH_NO_NEW_KAPPA',
      manifest_sha256=sha(P/'MANIFEST.json'),scalar_columns_each_direction=688,
      geometric_obstructions=2,frozen_search_summary=summary,
      matrix_label_cases=40,matrix_label_proposals=7813342,improved_kappa=False,
      scope='Focused reconstruction and exact replay; full discovery searches are archived, not repeated. No native supplier admission or repository-wide test suite claimed.')
    (W/'VERIFY.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
