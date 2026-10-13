"""Focused replay of algebra, obstruction and a nonzero admitted local control.

Search receipts are integrity-bound evidence, not a proof over unsearched words.
The full native PR1286 replay is a separate reproduction, not rerun by default.
"""
import argparse,collections,copy,gzip,hashlib,itertools,json,math,os,subprocess,sys
from pathlib import Path

P=Path(__file__).resolve().parent
R=P.parents[1]
def rd(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rejected(fn):
    try:fn()
    except AssertionError:return True
    raise AssertionError('negative control was accepted')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
    work=a.work.resolve();assert not work.exists() and not work.is_relative_to(P)
    pins=rd(P/'MANIFEST.json')
    actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json'}
    assert actual==set(pins)
    for rel,h in pins.items():assert sha(P/rel)==h,rel
    source=rd(P/'SOURCE-PINS.json')
    for p in source['repository_dependencies']:assert sha(R/p['path'])==p['sha256'],p['path']
    for p in source['vendor']:assert sha(P/p['path'])==p['sha256'],p['path']
    work.mkdir();os.environ['BASIS_WORK']=str(work);os.environ['IMB_ROOT']=str(R)
    sys.path.insert(0,str(P/'code'))
    import basis_search as b
    import prefix_search as prefix
    import frames as F
    from word import inline
    from model import cone_caps,aud
    from harness import DEFAULT_B
    from writeback import write_back
    controls=b.controls();assert controls==rd(P/'evidence/CONTROLS.json')
    w=b.load(P/'inputs/BASE.json.gz')
    identity=b.transform(w,593,594,b.Q(0))
    assert [e[:-1] for e in identity['B']]==[e[:-1] for e in w['B']]
    glob=b.transform(w,593,594,b.Q(1))
    assert b.canon(glob)==b.canon(b.load(P/'examples/global-593-594-scalar-only.json.gz'))
    assert len(glob['B'])==len(w['B'])-2

    def endpoint(word):
        _,comp=cone_caps(word)
        early={i for i,U in word['early_cleanup']}
        program=word['precondition']+comp+word['A']+word['cut']+word['B']
        program += [word['cleanup'][i] for i,U in word['early_cleanup']]
        program += [e for i,e in enumerate(word['cleanup']) if i not in early]
        n=224+word['report']['R']
        for dual in (False,True):
            rows=[{i:b.Q(1)} for i in range(n)]
            for e in program:aud.apply(e,rows,dual)
            expected=[{i:b.Q(1)} for i in range(n)]
            for t in range(112):expected[t if dual else 112+t][112+t if dual else t]=b.Q(-1 if dual else 1)
            assert rows==expected,('endpoint',dual)
        return n

    assert endpoint(glob)==704
    try:F.Graph(inline(glob,True),check_literal=False,tail_mutable=True,cut_equality=True)
    except F.Infeasible:pass
    else:raise AssertionError('permanent-conjugation frame counterexample accepted')
    witness=rd(P/'evidence/GLOBAL-OBSTRUCTION.json')
    def check_path(data):
        r=data['source'];v=data['vector']
        starts=inline(glob,True)['_start_frames']
        assert v in F.span(tuple(starts[r]))
        previous=(-1,-1)
        for section,i,src,dst in data['path']:
            key=(('A','B').index(section),i)
            assert key>previous and src==r
            assert {src,dst}<=set(b.regs(glob[section][i]))
            r=dst;previous=key
        assert r==data['target'] and 112<=r<224
        assert data['port']==glob['ports'][r-112]
        assert (v&data['port']).bit_count()%2==1
    check_path(witness)
    bad=copy.deepcopy(witness);bad['path'][1][1]+=10
    rejected(lambda:check_path(bad))

    # A nonzero prefix basis change survives every local exact audit.
    z=prefix.transform(w,[(593,594,b.Q(1))],1053)
    caps,compensation=cone_caps(z);costs=F.Costs(DEFAULT_B)
    assert cone_caps(prefix.transform(w,[(593,594,b.Q(1))],423))==(caps,compensation)
    g=F.Graph(inline(z,True),check_literal=False,tail_mutable=True,caps=caps,cut_equality=True)
    rr=F.optimal_frames(inline(z,True),costs,check_literal=False,graph=g)
    assert rr['certified']
    from cached_frames import optimal
    basecaps,_=cone_caps(w)
    basegraph=F.Graph(inline(w,True),check_literal=True,tail_mutable=True,caps=basecaps,cut_equality=True)
    optimal(inline(w,True),costs,graph=basegraph)
    cached=optimal(inline(z,True),costs,graph=g)
    assert cached['cache_hits']>0
    assert (cached['cost'],cached['profile'],cached['certified'])==(rr['cost'],rr['profile'],rr['certified'])
    positive=write_back(z,g,rr['assign'])
    assert positive['report']['local_profile']==w['report']['local_profile']
    assert positive['report']['width_inventory']==w['report']['width_inventory']
    assert b.canon(positive)==b.canon(b.load(P/'examples/nonzero-prefix-control.json.gz'))
    positive_path=work/'POSITIVE.json.gz';b.save(positive_path,positive)
    auditor=R/'research/gauge44-frames-x/independent/audit_local.py'
    with (work/'positive.log').open('w') as log:
        subprocess.run([sys.executable,'-B',str(auditor),'--word',str(positive_path),'--main',str(R),'--output',str(work/'POSITIVE-AUDIT.json')],check=True,stdout=log,stderr=subprocess.STDOUT)
    bad=copy.deepcopy(positive);bad['cleanup'].pop()
    rejected(lambda:endpoint(bad))
    bad=copy.deepcopy(glob);bad['B'][witness['path'][1][1]][3]*=-1
    rejected(lambda:endpoint(bad))
    # Dense, noncommuting four-coordinate positive control, independently audited.
    from dense_search import eliminate
    def determinant(m):
        return sum((-1)**sum(p[i]>p[j] for i in range(4) for j in range(i+1,4))*math.prod(m[i][p[i]] for i in range(4)) for p in itertools.permutations(range(4)))
    block_certificates=rd(P/'evidence/FULL-RANK-BLOCKS.json')
    assert len(block_certificates)==12
    touched={r for e in w['A']+w['cut'] for r in b.regs(e)}
    for block in block_certificates:
        hs,ds=block['helpers'],block['sources']
        assert not set(hs+ds)&touched
        raw=[{i:b.Q(1)} for i in range(704)]
        for e in w['A']+w['cut']+w['B'][:block['B_prefix_length']]:aud.apply(e,raw)
        matrix=[[raw[h].get(d,b.Q(0)) for d in ds] for h in hs]
        assert matrix==[[b.Q(q) for q in row] for row in block['matrix']]
        det=determinant(matrix);assert det==b.Q(block['determinant']) and det!=0
        _,diagonal=eliminate(matrix,(0,1,2,3))
        assert math.prod(diagonal[i][i] for i in range(4))==det
        U=tuple(block['source_frame']);V=tuple(block['helper_start_frame'])
        assert all(F.basis(tuple(w['start_extra'][str(d)]))==U for d in ds)
        assert all(F.basis(tuple(w['start_extra'][str(h)]))==V for h in hs)
        assert F.leq(V,U) and len(V)==1 and len(U) in (4,5)
    singular=copy.deepcopy(matrix);singular[0]=[b.Q(0)]*4
    assert determinant(singular)==0
    matrices=rd(P/'evidence/DENSE-MATRICES.json')
    matrix=matrices[0];hs=matrix['helpers']
    ops,diagonal=eliminate([[b.Q(q) for q in row] for row in matrix['matrix']],(0,1,2,3))
    dense=prefix.transform(w,[(hs[h],hs[d],q) for h,d,q in ops],matrix['cuts'][0])
    cap,_=cone_caps(dense)
    dg=F.Graph(inline(dense,True),check_literal=False,tail_mutable=True,caps=cap,cut_equality=True)
    dr=optimal(inline(dense,True),costs,graph=dg)
    dense=write_back(dense,dg,dr['assign'])
    assert dr['certified'] and dense['report']['local_profile']==w['report']['local_profile']
    assert b.canon(dense)==b.canon(b.load(P/'examples/dense-0.json.gz'))
    densepath=work/'DENSE.json.gz';b.save(densepath,dense)
    with (work/'dense.log').open('w') as log:
        subprocess.run([sys.executable,'-B',str(auditor),'--word',str(densepath),'--main',str(R),'--output',str(work/'DENSE-AUDIT.json')],check=True,stdout=log,stderr=subprocess.STDOUT)
    summary=rd(P/'RESULT.json')
    assert summary['new_kappa'] is None
    assert summary['permanent']['tested']==10428
    assert summary['permanent']['statuses']=={'frame-infeasible':10428}
    def receipts(name):return [json.loads(s) for s in gzip.decompress((P/'evidence'/name).read_bytes()).decode().splitlines()]
    permanent=receipts('PRICE-0-200.jsonl.gz')+receipts('PRICE-200-10228.jsonl.gz')
    assert sorted(r['index'] for r in permanent)==list(range(10428))
    assert all(r['status']=='frame-infeasible' for r in permanent)
    for tag in ('pairs','blocks','dense'):
        assert summary['temporary'][tag]['improved']==0
        assert summary['temporary'][tag]['errors']==0
        name={'pairs':'PREFIX-pairs-92.jsonl.gz','blocks':'PREFIX-blocks.jsonl.gz','dense':'DENSE.jsonl.gz'}[tag]
        rows=receipts(name);counts=summary['temporary'][tag]
        assert len(rows)==counts['distinct_tested']==len({r['index'] for r in rows})
        assert dict(collections.Counter(r['status'] for r in rows))==counts['statuses']
        priced=[r for r in rows if r['status']=='priced']
        assert len(priced)==counts['frame_priced']
        assert all(r['certified'] and r['cost_delta']==0 and r['profile']=={'1':2352,'2':504,'3':412,'4':130,'5':82} for r in priced)
    baseline=rd(P/'evidence/PR1286-RESULT.json')
    assert baseline['kappa']=='838166083799229/500000000000000000'
    assert baseline['base_native_reuse'] is False and baseline['extra_native_reuse'] is False
    later=rd(P/'evidence/PR1297-RESULT.json')
    assert later['kappa_decimal']=='0.001676854978651125'
    assert later['base_native_reuse'] is False and later['extra_native_reuse'] is False
    assert sha(P/'evidence/PR1297-SOURCE-MANIFEST.json')==source['additional_reproduction']['source_manifest_sha256']
    for pr in [1286,1297]:
        stages=rd(P/'evidence'/f'PR{pr}-STAGES.json')
        assert all(s['exit_code']==0 for s in stages)
        assert {'fresh-native-base','fresh-native-extra','strict-global'}<=set(s['name'] for s in stages)
        for stage in stages:
            raw=gzip.decompress((P/'evidence'/f"PR{pr}-{stage['name']}.log.gz").read_bytes())
            assert hashlib.sha256(raw).hexdigest()==stage['log_sha256']
    result=dict(status='PASS_HELPER_BASIS_SCREEN_SCOPED_NO_NEW_KAPPA',controls=controls,additional_negative_controls=4,full_rank_blocks=12,scalar_columns=704,orientations=2,positive_cost_change=0,search_receipts=summary,baseline_native_replay='Separate frozen receipt; not rerun by this focused verifier.')
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],flush=True)

if __name__=='__main__':main()
