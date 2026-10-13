"""Replay one bounded search in a fresh directory outside the checkout.

The historical scripts are preserved verbatim. Only their checkout path is
adapted when materializing the replay directory; every adaptation is recorded.
No discovery script participates in finite-construction admission.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

D = Path(__file__).resolve().parent
P = D.parent
ROOT = P.parents[1]
HISTORICAL_ROOT = '/Users/thomasdifiore/integer-mult-next-construction'
SUITES = {'shared': 'search_shared_donations.py',
          'pairs': 'search_shared_pairs.py',
          'single': 'search_single_demotions.py',
          'partial-group': 'screen_partial_group.py',
          'retiming': 'search_retiming.py'}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite', choices=[*SUITES, 'repair'], required=True)
    ap.add_argument('--work', type=Path, required=True)
    args = ap.parse_args()
    work = args.work.resolve()
    assert not work.exists() and not work.is_relative_to(ROOT)
    work.mkdir(parents=True)
    (work / 'x54').mkdir()
    for pid, name in [('demote3', 'THREE-WORD'), ('demote4', 'FOUR-WORD')]:
        shutil.copyfile(P / 'data' / (name + '.json.gz'), work / 'x54' / (pid + '.json.gz'))
    toolkit = work / 'research/exact-frame-toolkit'
    shutil.copytree(P / 'vendor/pr1186', toolkit, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    adaptations = {}
    for source in (D / 'scripts').glob('*.py'):
        text = source.read_text()
        assert text.count(HISTORICAL_ROOT) == 1
        text = text.replace(HISTORICAL_ROOT, str(ROOT))
        dest = work / source.name
        dest.write_text(text)
        adaptations[source.name] = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                                       prepared_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
                                       replaced_checkout_path=True)
    (work / 'ADAPTATIONS.json').write_text(json.dumps(adaptations, indent=2) + '\n')
    env = dict(os.environ, IMB_ROOT=str(ROOT), OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    if args.suite == 'repair':
        command = [sys.executable, '-B', str(toolkit / 'repair.py'), str(work / 'x54/demote3.json.gz'),
                   str(work / 'repair-results.json'), '--workers', '3', '--timeout', '20', '--max-tasks-per-child', '50']
    else:
        if args.suite == 'pairs':
            path = work / 'shared-donations/CANDIDATES.json'
            path.parent.mkdir()
            path.write_bytes(gzip.decompress((D / 'records/shared-donations-CANDIDATES.json.gz').read_bytes()))
        if args.suite == 'retiming':
            # Recheck exactly the 700 retained cases; the original 14,720-case
            # census was stopped, so no complete census is claimed here.
            (work / 'RECORDED-RETIMING.json').write_bytes(gzip.decompress((D / 'records/retiming-RESULTS.json.gz').read_bytes()))
            driver = work / 'replay_retained_retiming.py'
            driver.write_text("""import json,multiprocessing as mp
import search_retiming as s
if __name__ == '__main__':
    cases=[tuple(r['case']) for r in json.loads((s.W/'RECORDED-RETIMING.json').read_text())]
    assert len(cases)==len(set(cases))==700
    s.OUT.mkdir()
    with mp.get_context('fork').Pool(2,initializer=s.init,maxtasksperchild=100) as pool:
        rows=list(pool.imap_unordered(s.trial,cases,chunksize=1))
    (s.OUT/'RESULTS.json').write_text(json.dumps(rows,indent=2)+'\\n')
    print('REPLAYED',len(rows),'gains',sum(r.get('delta',0)<0 for r in rows))
""")
        else:
            driver = work / SUITES[args.suite]
        command = [sys.executable, '-B', str(driver)]
    subprocess.run(command, cwd=ROOT, env=env, check=True)

if __name__ == '__main__':
    main()
