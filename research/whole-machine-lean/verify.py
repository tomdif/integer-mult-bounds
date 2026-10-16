"""Check saved evidence bindings only. Use verify_kernel.py to run Lean."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, expected in manifest['inputs'].items():
        need(digest(ROOT / relative) == expected, 'changed input: ' + relative)
    receipt = json.loads((HERE / 'KERNEL.json').read_text())
    need(receipt['status'] == 'PASS_SCOPED_LEAN_PROGRESS', 'wrong receipt type')
    need(receipt['whole_machine_proved'] is False and receipt['strict_acceptance'] is False,
         'this receipt cannot assert completion or strict acceptance')
    need(receipt['target'] == 'WholeMachine.Target.Complete', 'wrong target')
    need(receipt['source_manifest_sha256'] == digest(HERE / 'SOURCES.json'), 'stale receipt')
    for source in HERE.glob('*.lean'):
        need(receipt['local_source_sha256'][source.name] == digest(source), 'stale Lean source: ' + source.name)
    predecessor = ROOT / 'research/fine-prime-transform-assembly/Recovery.lean'
    need(receipt['local_source_sha256']['Recovery.lean'] == digest(predecessor), 'stale recovery source')
    dependencies = json.loads((HERE / 'lean/lake-manifest.json').read_text())['packages']
    need(receipt['dependencies'] == {d['name']: d['rev'] for d in dependencies}, 'dependency pins differ')
    for label, key in [('BUILD.log', 'build'), ('OFFICIAL-FRESH.log', 'official_fresh_replay')]:
        stage = receipt[key]
        need(stage['returncode'] == 0 and stage['stopped'] is None, 'unsuccessful stage: ' + key)
        need(stage['log_sha256'] == digest(HERE / 'evidence' / label), 'changed log: ' + label)
    official = receipt['official_fresh_replay']
    need(official['argv'][-3:] == ['--fresh', '--verbose', 'Audit'], 'wrong official invocation')
    need('replaying Audit with --fresh' in (HERE / 'evidence/OFFICIAL-FRESH.log').read_text(),
         'missing official replay marker')
    controls = receipt['rejected_controls']
    need(set(controls) == {'wrong_kappa', 'completed_map_bounds_calls', 'omit_restore_precision',
                           'erase_visited_history', 'omit_handoff'}, 'wrong controls')
    for name, stage in controls.items():
        need(stage['returncode'] != 0 and stage['stopped'] is None, 'control did not reject: ' + name)
        need(stage['log_sha256'] == digest(HERE / 'evidence' / (name + '.log')), 'changed control: ' + name)
    independent = receipt['independent']
    need(independent['accepted'] is False, 'raw checker result is not strict acceptance')
    if 'log_sha256' in independent:
        need(independent['log_sha256'] == digest(HERE / 'evidence/INDEPENDENT.log'), 'changed independent log')
    result = {'status': 'PASS_SAVED_EVIDENCE_BINDINGS_ONLY', 'inputs': len(manifest['inputs']),
              'new_lean_theorems': 58, 'whole_machine_proved': False, 'strict_acceptance': False,
              'scope': 'Saved source/receipt/log bindings only; this invocation does not run Lean.'}
    need(result == json.loads((HERE / 'RESULT.json').read_text()), 'unexpected saved summary')
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
