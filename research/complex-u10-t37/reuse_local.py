# SPDX-License-Identifier: Apache-2.0
"""Explicitly reuse a completed, source-pinned U10 native replay.

All native artifacts and the complete phase-review mathematics must match the
frozen discovery pins. The prior eight-stage audit is bound and copied; this
mode does not claim to rerun those stages. Default verify.py rebuilds them.
"""
import argparse
import gzip
import hashlib
import math
import shutil
from pathlib import Path
from support import P, read, sha, dump


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--u8-word', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    recipe = read(P/'vendor/pr987/RECIPE-U10.json')
    assert hashlib.sha256(gzip.decompress(args.u8_word.read_bytes())).hexdigest() == recipe['base_sha256']
    assert hashlib.sha256(gzip.decompress((source/'u10/FULL-WORD.json.gz').read_bytes())).hexdigest() == recipe['expect_sha256']
    for name, expected in read(P/'LOCAL-PINS.json').items():
        path = source/'local'/name
        if isinstance(expected, dict):
            assert name == 'CLIFFORD-REVIEW.json'
            review = read(path)
            elapsed = review.pop('seconds')
            assert type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0
            assert review == expected
        else:
            assert sha(path) == expected, name
    stages = read(source/'STEPS.json')
    assert [x['step'] for x in stages] == ['u10','u10-controls','layer-end-controls','native','ledgers','local-replay','wrappers','phases']
    assert all(x['exit_code'] == 0 for x in stages)
    controls = read(source/'u10-controls/controls.json')
    assert set(controls) == set(read(P/'vendor/pr987/LOCAL-PINS-U10.json')['u10_controls'])
    assert all(x['ok'] for x in controls.values())
    ends = read(source/'controls/COLD-END-CONTROLS.json')
    assert ends['status'] == 'PASS_COLD_END_RAW_WORD_CONTROLS' and len(ends['rejected']) == 95
    assert not args.out.exists()
    shutil.copytree(source, args.out)
    inventory = {p.relative_to(source).as_posix(): sha(p) for p in source.rglob('*') if p.is_file()}
    assert inventory == {p.relative_to(args.out).as_posix(): sha(p) for p in args.out.rglob('*') if p.is_file()}
    dump(args.out/'REUSE-BINDING.json', dict(status='PASS_COMPLETE_FROZEN_U10_NATIVE_REUSE',
         source=str(source), artifacts=inventory, source_pins_sha256=sha(P/'SOURCE-PINS.json')))
    print('PASS_COMPLETE_FROZEN_U10_NATIVE_REUSE')
