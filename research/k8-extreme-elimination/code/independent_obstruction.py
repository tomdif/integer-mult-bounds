"""Standard-library-only independent checker for a frame-obstruction witness.

No generator, frame optimizer or scheduling code is imported. A shared frame
contains both operands' current frames. Along each retained noncommuting
precedence edge a vector cannot disappear; every register ends at its cap.
"""
import json,gzip,hashlib,copy
from fractions import Fraction as Q
from pathlib import Path

def span(vectors):
    points={0}
    for x in vectors:points|={p^x for p in points}
    return points

def regs(e):return e[1:3]if e[0]=='add'else e[1:2]

def commute_exact(a,b):
    coordinates=sorted(set(regs(a)+regs(b)))
    def apply(e,rows):
        q=Q(e[3],e[4])if e[0]=='add'else Q(e[2],e[3]);t=e[1]
        if e[0]=='add':rows[t]=[x+q*y for x,y in zip(rows[t],rows[e[2]])]
        else:rows[t]=[q*x for x in rows[t]]
    def run(order):
        rows={r:[Q(int(r==s))for s in coordinates]for r in coordinates}
        for e in order:apply(e,rows)
        return rows
    return run([a,b])==run([b,a])

def check(w,witness):
    raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
    assert hashlib.sha256(raw).hexdigest()==witness['word_content_sha256']
    n=224+w['report']['R'];initial=witness['initial_register'];p=witness['initial_vector'];last=witness['last_register']
    assert 0<=initial<n and 0<p<512
    start=[w['ports'][initial]]if initial<112 else w.get('start_extra',{}).get(str(initial),[])
    assert p in span(start),'The witness vector is not in the entry frame'
    path=witness['A_gate_path'];assert path and path==sorted(set(path))
    gates=[w['A'][i]for i in path]
    assert initial in regs(gates[0]) and last in regs(gates[-1])
    for a,b in zip(gates,gates[1:]):
        assert set(regs(a))&set(regs(b))
        assert not commute_exact(a,b),'A claimed mandatory edge is commuting'
    boundary=witness['boundary']
    if boundary['kind']=='cut':
        if last in w['centers']:expected=span(w['center_frames'][w['centers'].index(last)])
        else:
            assert 112<=last<224;expected=span(w.get('target_levels',{}).get(str(last-112),[]))
    else:
        q=boundary['cap_register']
        if boundary['kind']=='B_or_tail':
            B=w['B']+[w['cleanup'][i]for i,U in w['early_cleanup']]
            assert {last,q}<=set(regs(B[boundary['event']]))
        else:assert boundary['kind']=='final'and q==last
        if 112<=q<224:expected={x for x in range(512)if (x&w['ports'][q-112]).bit_count()%2==0}
        else:expected=span(w['helper_final'].get(str(q),[1<<i for i in range(9)]))
    assert span(boundary['frame'])==expected,'Boundary frame differs from the actual interface'
    assert p not in expected,'No contradiction at the claimed endpoint'
    return dict(status='PASS_LITERAL_FRAME_OBSTRUCTION',initial_register=initial,initial_vector=p,
                mandatory_A_edges=len(path)-1,last_register=last,boundary=boundary)

def check_with_controls(w,witness):
    result=check(w,witness);controls=[]
    for name in ['zero_vector','full_boundary','wrong_entry_register']:
        bad=copy.deepcopy(witness)
        if name=='zero_vector':bad['initial_vector']=0
        elif name=='full_boundary':bad['boundary']['frame']=[1<<i for i in range(9)]
        else:bad['initial_register']=112
        try:check(w,bad)
        except (AssertionError,IndexError,KeyError):controls.append(name)
        else:raise AssertionError('False obstruction accepted: '+name)
    result['controls_rejected']=controls;return result

if __name__=='__main__':
    W=Path(__import__('os').environ['EXTREME_WORK']).resolve()
    word=json.load(gzip.open(W/'R464-SCALAR-ONLY.json.gz'));witness=json.loads((W/'R464-OBSTRUCTION.json').read_text())
    result=check_with_controls(word,witness);(W/'OBSTRUCTION-CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],'controls',len(result['controls_rejected']))
