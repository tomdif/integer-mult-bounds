"""Apply PR1049's unchanged independent leaver audit to both final words."""
import argparse
import json
from pathlib import Path
from common import P, ROOT, read, dump, load, identity, sha
import package

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    target = args.out.resolve()
    assert not target.exists() and not target.is_relative_to(ROOT)
    package.validate()
    source = P / 'vendor/pr1049/verify.py'
    checker = load(source, 'unchanged_pr1049_leaver_checker')
    cells = checker.read_pinned('CODED-CELLS-k8.json')
    targets = checker.cell_targets(cells, checker.read_pinned('TRI-LEAVER-k8.json'))
    result = {}
    for pid, name in [('demote3', 'THREE-WORD'), ('demote4', 'FOUR-WORD')]:
        word = read(P / 'data' / (name + '.json.gz'))
        found, receipt = checker.audit_word(word, cells, targets)
        receipt['controls'] = checker.controls(word, found, cells, targets)
        receipt['word_content_sha256'] = identity(word)
        assert len(found) == 8 and len(receipt['leavers']) == 24
        assert len(receipt['controls']) == 7
        result[pid] = receipt
    report = dict(status='PASS_INDEPENDENT_PR1049_AUDIT',
                  source_commit='6d0a145e8b4774b1b0d4e3da56890af5adc9b04f',
                  source_sha256=sha(source), providers=result)
    # The checker returns integer profile keys; JSON stores those as strings.
    assert json.loads(json.dumps(report)) == read(P / 'evidence/LEAVER-CHECKS.json')
    dump(target, report)
    print(report['status'], 'providers=2 cells=16 controls=14')

if __name__ == '__main__':
    main()
