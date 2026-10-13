# SPDX-License-Identifier: Apache-2.0
"""Explicit composition adapters; original PR942 / PR987 sources stay read-only.

Construction, ownership, payload and assembly checks retain their upstream
algorithms. Only the local profile, expected arithmetic result, and native
recipe identity change. Every generated edit is recorded and re-derived.
"""
import os
from pathlib import Path
from support import P, ROOT, T37, read, sha, dump, load


def replace(text, before, after, count=1):
    assert text.count(before) == count, (before, text.count(before), count)
    return text.replace(before, after)


def expected_adaptations():
    upstream = load(T37/'prepare.py', 'u10_original_prepare')
    records = upstream.expected_adaptations()
    rec = records['build_parent.py']
    old = "read(HERE/'data/CLAIM.json')['local_profile']"
    new = repr(read(P/'CLAIM.json')['local_profile'])
    rec['text'] = replace(rec['text'], old, new)
    rec['edits'] = [[old, new, 1]]
    return records


def expected_checks():
    claim = read(P/'CLAIM.json')
    k = claim['kappa_decimal']
    b = claim['complex_lower']
    common_prefix = 'import sys\nsys.path.insert(0, '+repr(str(T37))+')\n'
    inventory = {}
    for name in ('all_t_bound.py', 'check_payload_controls.py', 'final_binding.py'):
        path = T37/name if name == 'final_binding.py' else T37/'independent'/name
        text = path.read_text()
        edits = []

        def edit(before, after, count=1):
            nonlocal text
            text = replace(text, before, after, count)
            edits.append([before, after, count])

        if name == 'all_t_bound.py':
            edit('ROOT = HERE.parents[2]', 'ROOT = Path('+repr(str(ROOT))+')')
            edit("claim = json.loads((ROOT/'research/complex-t21-owners/data/CLAIM.json').read_text())",
                 "claim = json.loads((ROOT/'research/complex-u10-t37/CLAIM.json').read_text())")
            edit('fixed U8 whole-owner family', 'fixed U10 whole-owner family')
            edit('unchanged U8 local paid profile', 'fixed U10 local paid profile')
            edit('PASS_ALL_T_U8_SIGNED_DUAL_RELAXATION_BOUND', 'PASS_ALL_T_U10_SIGNED_DUAL_RELAXATION_BOUND')
        elif name == 'check_payload_controls.py':
            edit('ROOT=HERE.parents[2]', 'ROOT=Path('+repr(str(ROOT))+')')
            edit("'0.001661960547713947'", repr(k))
        else:
            edit("load(P/'prepare.py','t37_expected_adapters').expected_adaptations()",
                 "load(Path("+repr(str(P/'prepare.py'))+"),'u10_expected_adapters').expected_adaptations()")
            edit("Q('0.001661960547713947')", 'Q('+repr(k)+')')
            edit("Q('0.001664727258740678855772')", 'Q('+repr(b)+')')
            edit("['barch','barch-controls','layer-end-controls','native','ledgers','local-replay','wrappers','phases']",
                 "['u10','u10-controls','layer-end-controls','native','ledgers','local-replay','wrappers','phases']")
            edit("len(read(work/'native/barch-controls/controls.json'))==38",
                 "len(read(work/'native/u10-controls/controls.json'))==14")
            edit("expected=['ancestry-coverage','baseline799-binding','u8-native','prepare'",
                 "expected=['upstream-t37-binding','ancestry-coverage','baseline799-binding','u10-native','prepare'")
            edit("'independent-owners','build-parent','check-parent','independent-price'",
                 "'independent-owners','build-parent','nominate-provider','check-parent','independent-price'")
            edit('PASS_COMPLETE_T37_RESULT_BINDINGS', 'PASS_COMPLETE_U10_T37_RESULT_BINDINGS')
            text = common_prefix+text
        inventory[name] = dict(source=path, text=text, edits=edits)
    return inventory


def materialize_checks(work):
    dest = work/'composition'
    dest.mkdir()
    receipts = {}
    for name, record in expected_checks().items():
        path = dest/name
        path.write_text(record['text'])
        receipts[name] = dict(source_sha256=sha(record['source']),
                              generated_sha256=sha(path), edits=record['edits'])
    dump(work/'COMPOSITION-CHECK-ADAPTERS.json', receipts)


def check_generated_checks(work):
    actual = read(work/'COMPOSITION-CHECK-ADAPTERS.json')
    wanted = expected_checks()
    assert set(actual) == set(wanted)
    assert {p.name for p in (work/'composition').glob('*.py')} == set(wanted)
    for name, record in wanted.items():
        path = work/'composition'/name
        assert path.read_text() == record['text'], 'Composition checker bytes: '+name
        assert actual[name] == dict(source_sha256=sha(record['source']),
                                   generated_sha256=sha(path), edits=record['edits'])
    return actual


def main():
    work = Path(os.environ['T37_WORK']).resolve()
    load(T37/'prepare.py', 'u10_prepare_base').main()
    records = expected_adaptations()
    receipts = {}
    for name, record in records.items():
        dest = work/'runtime/code'/name.split('/',1)[1] if name.startswith('runtime/') else work/'adapted'/name
        dest.write_text(record['text'])
        receipts[name] = dict(source_sha256=sha(record['source']), generated_sha256=sha(dest))
        if 'edits' in record:
            receipts[name]['edits'] = record['edits']
    dump(work/'ADAPTATIONS.json', receipts)
    spec = read(work/'runtime/data/SPEC.json')
    spec['name'] = 'gauge44-U10-t37-whole-owners'
    dump(work/'runtime/data/SPEC.json', spec)
    materialize_checks(work)
    print('PREPARED_U10_T37', work)


if __name__ == '__main__':
    main()
