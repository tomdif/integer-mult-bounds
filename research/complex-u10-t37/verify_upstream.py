# SPDX-License-Identifier: Apache-2.0
"""Read-only rebinding of a completed PR942 run and its complete ancestry."""
import argparse
from pathlib import Path
from support import T37, read, sha, dump, load

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    checked = load(T37/'final_binding.py', 'original_t37_final_binding').check(work, args.baseline.resolve())
    assert checked == read(work/'FINAL-BINDING.json')
    result = read(work/'RESULT.json')
    assert result['status'] == 'PASS_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY'
    assert result['final_binding_sha256'] == sha(work/'FINAL-BINDING.json')
    assert not args.out.exists()
    dump(args.out, dict(status='PASS_SOURCE_BOUND_COMPLETED_T37_AND_ANCESTRY',
                       checked=checked, result_sha256=sha(work/'RESULT.json'),
                       full_u8_word_sha256=sha(work/'native/barch/FULL-WORD.json.gz')))
    print('PASS_SOURCE_BOUND_COMPLETED_T37_AND_ANCESTRY')
