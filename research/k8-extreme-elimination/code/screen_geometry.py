"""Apply PR1240's optimistic relaxation to the final mixed X54 profiles."""
import sys,json,gzip
from pathlib import Path
from fractions import Fraction as Q
W=Path(__import__('os').environ['EXTREME_WORK']).resolve()
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor/pr1240'))
import ceiling as C
P=ROOT/'research/x54-mixed-allocation';claim=json.loads((P/'CLAIM.json').read_text())
words=[json.load(gzip.open(P/'data'/f'{n}-WORD.json.gz'))for n in ['THREE','FOUR']]
local={r:sum(Q(count,333)*word['report']['local_profile'][str(r)]for count,word in zip([125,208],words))for r in [1,2,3,4,5,8]}
results=[]
for cap in [48,51]:
 lo,hi=C.ceiling(local,73,896,9,64,R=cap);k=hi/(1+hi)
 rec=dict(idle_cap=cap,complex_bracket=[str(lo),str(hi)],kappa_upper=str(k),kappa_upper_decimal=f'{float(k):.18f}',gain_ceiling_percent=float(100*(k/Q(claim['kappa'])-1)),moment_at_upper=[str(q)for q in C.relax(local,73,896,9,64,hi,R=cap)])
 results.append(rec);print(rec['idle_cap'],rec['kappa_upper_decimal'],rec['gain_ceiling_percent'],flush=True)
(W/'GEOMETRY-CEILINGS.json').write_text(json.dumps(dict(status='OPTIMISTIC_BOUND_NOT_A_CONSTRUCTION',source_pr=1240,source_commit='77dc486aafa0ce89c0af8b7bc012adb40a933fda',local={str(r):str(n)for r,n in local.items()},results=results),indent=2)+'\n')
