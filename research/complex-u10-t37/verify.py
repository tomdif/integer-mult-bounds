# SPDX-License-Identifier: Apache-2.0
"""Compose PR987 U10 with PR942 T37 and replay full strict conditional admission.

The completed U8/T37 and PR799 ancestry are explicitly reused and rebound.
U10 native data, the combined controller, invoice, moments, and strict assembly
are rebuilt. New outputs must be outside the checkout.
"""
import argparse
import gzip
import os
import subprocess
import sys
import time
from fractions import Fraction as Q
from support import P, ROOT, T37, T21, read, sha, dump, load, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', required=True, type=__import__('pathlib').Path)
    parser.add_argument('--baseline799', required=True, type=__import__('pathlib').Path)
    parser.add_argument('--u8-run', required=True, type=__import__('pathlib').Path)
    parser.add_argument('--native-from', type=__import__('pathlib').Path,
                        help='Explicit reuse of a completed U10 native replay with identical frozen artifacts')
    args = parser.parse_args()
    work, baseline, u8 = args.work.resolve(), args.baseline799.resolve(), args.u8_run.resolve()
    assert not work.exists() and not work.is_relative_to(ROOT)
    pins = validate()
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               PYTHON=sys.executable, SW4_FRAME8_PYTHON=sys.executable,
               T37_WORK=str(work), T37_BASELINE=str(baseline), T37_LOCAL=str(work/'native/local'))
    temp = work/'temp'; temp.mkdir()
    env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD', 'WITNESS_SPEC'):
        env.pop(key, None)
    stages = []

    def run(name, script, *arguments):
        log = work/(name+'.log'); start = time.monotonic()
        with log.open('w') as stream:
            proc = subprocess.run([sys.executable, '-B', str(script), *map(str, arguments)],
                                  cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=proc.returncode,
                           seconds=round(time.monotonic()-start, 3), log_sha256=sha(log)))
        dump(work/'STAGES.json', stages)
        if proc.returncode:
            raise RuntimeError(name+'\n'+log.read_text(errors='replace')[-6000:])
        print('PASS', name, stages[-1]['seconds'], flush=True)

    run('upstream-t37-binding', P/'verify_upstream.py', '--work', u8, '--baseline', baseline,
        '--out', work/'UPSTREAM-T37-BINDING.json')
    run('ancestry-coverage', T21/'vendor/pr858/baseline_coverage.py', '--ancestor', baseline/'ancestor', '--out', work/'ANCESTRY-COVERAGE.json')
    run('baseline799-binding', ROOT/'scripts/verify_frontier799_bindings.py', '--ancestor', baseline/'ancestor',
        '--native', baseline/'native', '--global', baseline/'global', '--independent', baseline/'INDEPENDENT-LOCAL.json',
        '--price', baseline/'INDEPENDENT-PRICE.json', '--out', work/'BASELINE-BINDING.json')
    if args.native_from:
        run('u10-native', P/'reuse_local.py', '--source', args.native_from.resolve(), '--out', work/'native',
            '--u8-word', u8/'native/barch/FULL-WORD.json.gz')
    else:
        run('u10-native', P/'reproduce_local.py', '--main', ROOT, '--pr635', ROOT/'research/complex-sw4-frame8/vendor/pr635',
            '--u8-word', u8/'native/barch/FULL-WORD.json.gz', '--out', work/'native')
    native = work/'native/local'
    native_pins = read(P/'LOCAL-PINS.json')
    for name, expected in native_pins.items():
        if isinstance(expected, dict):
            assert name == 'CLIFFORD-REVIEW.json'
            review = read(native/name)
            elapsed = review.pop('seconds')
            assert isinstance(elapsed, (int, float)) and elapsed >= 0
            assert review == expected, 'Frozen mathematical phase review'
        else:
            assert sha(native/name) == expected, 'Frozen U10 artifact: '+name
    run('prepare', P/'prepare.py')
    run('frozen-construction', T37/'independent/verify_construct.py', '--out', work/'CONSTRUCTION-CHECK.json')
    run('independent-owners', T37/'independent/check_t37.py', '--word', native/'CANONICAL-WORD.json.gz',
        '--local-replay', native/'INDEPENDENT-LOCAL-REPLAY.json', '--baseline-base', baseline/'global/global/base', '--out', work/'INDEPENDENT-OWNERS.json')
    run('build-parent', work/'adapted/build_parent.py', '--base', baseline/'global/global/base',
        '--owners', T37/'OWNERS.json.gz', '--order', T37/'ORDER.json', '--out', work/'lift')
    run('nominate-provider', P/'nominate_provider.py', '--local', native, '--plan', work/'lift/PLAN.json')
    run('check-parent', work/'adapted/check_parent.py', '--source', baseline/'global/global/base/split-centres/GLOBAL-TEMPLATE.json.gz',
        '--parent', work/'lift/GLOBAL-TEMPLATE.json.gz', '--out', work/'PARENT-CHECK.json')
    run('independent-price', work/'composition/all_t_bound.py', '--out', work/'ALL-T-BOUND.json')
    run('discovery', T37/'replay.py', 'discovery')
    frozen_spec = sha(work/'runtime/data/SPEC.json')
    run('strict', T37/'replay.py', 'strict')
    assert sha(work/'runtime/data/SPEC.json') == frozen_spec, 'Strict run changed frozen witness'
    run('payload-controls', work/'composition/check_payload_controls.py', '--work', work, '--out', work/'PAYLOAD-CONTROLS.json')
    run('final-binding', work/'composition/final_binding.py', '--work', work, '--baseline', baseline)
    load(P/'prepare.py', 'u10_check_adapters').check_generated_checks(work)
    claim = read(P/'CLAIM.json')
    assembly = read(work/'strict/ASSEMBLY.json')
    owners = read(work/'INDEPENDENT-OWNERS.json')
    invoice = read(work/'strict/global/audit/PREFIX-AND-INVOICE.json')
    assert assembly['kappa_decimal'] == claim['kappa_decimal']
    assert assembly['complex_profile'] == claim['profile'] == owners['profile']
    assert owners['local_profile'] == claim['local_profile']
    for key in ('roles','calls','live','physical','rank_mass','deficit','idle','prefix_bits'):
        assert owners[key] == claim[key], key
    assert invoice['charged_prefix_bits'] == 1024
    assert invoice['finite']['physical_row_coefficient'] == 17495
    final = read(work/'FINAL-BINDING.json')
    assert final['status'] == 'PASS_COMPLETE_U10_T37_RESULT_BINDINGS'
    assert final['pins'] == pins['upstream']
    assert validate() == pins, 'Composition source changed during replay'
    k = Q(assembly['kappa'])
    result = dict(status='PASS_U10_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY',
                  kappa=str(k), kappa_decimal=assembly['kappa_decimal'],
                  improvement_over_pr942=str(k-Q('0.001661960547713947')),
                  improvement_over_pr987_t21=str(k-Q('0.001662036304429768')),
                  complex_lower=assembly['complex_lower'], bit_lower=assembly['bit_lower'],
                  prefix_bits=invoice['global_prefix_bits'], charged_prefix_bits=1024,
                  physical_row_coefficient=17495, profile=assembly['complex_profile'],
                  cold_baseline=str(baseline), reused_completed_ancestry=True,
                  reused_u8_run=str(u8), fresh_u10_native=args.native_from is None,
                  reused_u10_native=str(args.native_from.resolve()) if args.native_from else None,
                  pins=pins, final_binding_sha256=sha(work/'FINAL-BINDING.json'),
                  assembly_sha256=sha(work/'strict/ASSEMBLY.json'),
                  frozen_spec_sha256=frozen_spec, stages=stages,
                  scope='Finite conditional composition. Inherited all-size/compiler, common-label/physical-realization, precision/tape, analytic-transfer and bit H1-H5 assumptions remain. No unconditional or full proof-assistant theorem claim.',
                  credits={'U10':'rohanarun PR987, extending NewBArch PR869', 'T37':'jon314159 PR942',
                           'composition':'U10 local construction combined with T37 whole owners; OpenAI Codex assistance.'})
    dump(work/'RESULT.json', result)
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()
