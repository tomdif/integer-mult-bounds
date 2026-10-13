#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Refine PR942's final decimal rounding, without changing its construction.

Prepared with OpenAI Codex assistance. Uses the attributed and pinned PR942
verification closure and its retained exact moment / outer assembly engines.
This is a conditional finite certificate, not a new circuit or theorem.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T37 = ROOT / 'research/complex-t37-owners'
ENGINES = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines'
OLD_K = Q('0.001661960547713947')
NEW_K = Q('0.001661960547713947858091')
GRID = Q(1, 10**24)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def decimal(value):
    with localcontext() as ctx:
        ctx.prec = 80
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def exact_moments(M, B, profile, width, live, lower, surcharge):
    """Check both ends by two different rational log/exp interval engines."""
    rows = []
    for endpoint, accepts in [(lower, True), (lower + GRID, False)]:
        lo, hi = M.moment(profile, width, live, endpoint, surcharge)
        blo, bhi = B.moment(width, live, list(profile.items()), endpoint)
        if surcharge:
            flo, fhi = B.moment(width, live,
                               [(1, 32 * width**2 * sum(profile.values()))], endpoint)
            blo += flo / 10**16
            bhi += fhi / 10**16
        assert lo <= hi and blo <= bhi
        assert (hi < 1 and bhi < 1) if accepts else (lo > 1 and blo > 1)
        rows.append(dict(endpoint=str(endpoint), accepted=accepts,
                         mercator_residual=[str(lo - 1), str(hi - 1)],
                         base_two_residual=[str(blo - 1), str(bhi - 1)]))
    return rows


def verify(work, baseline):
    # Recheck source pins and actual construction/ancestry bytes, not just a
    # success label. PR942's immutable files and receipts remain unmodified.
    sys.path.insert(0, str(T37))
    binding = load(T37 / 'final_binding.py', 'rounding_t37_binding')
    current_binding = binding.check(work, baseline)
    assert current_binding == read(work / 'FINAL-BINDING.json')
    result = read(work / 'RESULT.json')
    assert result['status'] == 'PASS_T37_STRICT_WITH_SOURCE_BOUND_ANCESTRY'
    assert result['final_binding_sha256'] == sha(work / 'FINAL-BINDING.json')
    assert Q(result['kappa']) == OLD_K
    assert result['pins'] == current_binding['pins']
    old = read(work / 'strict/ASSEMBLY.json')
    invoice_path = work / 'strict/global/audit/PREFIX-AND-INVOICE.json'
    owner_path = work / 'strict/global/audit/OWNERS-AND-PROFILE.json'
    invoice, owner = read(invoice_path), read(owner_path)
    assert old['input_sha256']['owner_audit'] == sha(owner_path)
    assert old['input_sha256']['fresh_invoice'] == sha(invoice_path)
    assert invoice['charged_prefix_bits'] == 1024
    assert invoice['row_prefix_extra'] == 2048
    assert invoice['global_prefix_bits'] == 779
    assert invoice['finite']['physical_row_coefficient'] == 17495 < 20161
    modules = {}
    for name in ('moment', 'base_two_moment', 'outer'):
        path = ENGINES / (name + '.py')
        assert sha(path) == old['input_sha256']['engines/' + name + '.py']
        modules[name] = load(path, 'rounding_' + name)
    M, B, A = (modules[name] for name in ('moment', 'base_two_moment', 'outer'))
    b, c = Q(old['complex_lower']), Q(old['bit_lower'])
    assert b == Q('0.001664727258740678855772')
    assert c == Q('0.001733427039589844234749')
    H = {int(r): n for r, n in owner['paid_profile'].items()}
    assert 73 * owner['live'] - sum(r*n for r, n in H.items()) == 11840
    complex_moments = exact_moments(M, B, H, 73, owner['live'], b, False)
    bit_path = work / 'runtime/inputs/PR589-EXPECTED.json'
    assert sha(bit_path) == old['input_sha256']['package:inputs/PR589-EXPECTED.json']
    bit = read(bit_path)['nine']
    bitH = {int(r): n for r, n in bit['profile'].items()}
    assert bit['bit']['charged_two_level_coefficient_bits'] == 512
    assert 64 * bit['bit']['live'] - sum(r*n for r, n in bitH.items()) == 10272
    bit_moments = exact_moments(M, B, bitH, 64, bit['bit']['live'], c, True)

    eta = beta = GRID
    s = min(c, (1-beta)*b) - Q(1, 10**27)
    assert 0 < s < c and s < (1-beta)*b
    a = Q(384599, 10**10)
    cuts = []
    ceil = lambda x: -(-x.numerator // x.denominator)
    for _ in range(7):
        previous = a
        a = (1-s)*s + s*previous
        gap = min(s-a, 1-a-s, 1-a-s*(1-previous), 1-s)
        assert previous < a < s < 1-a and gap > 0
        cutoff = max(ceil(36/gap**2), ceil(2*(4+1024)/gap))
        assert cutoff*gap**2 >= 36 and cutoff*gap >= 2*(4+1024)
        cuts.append(dict(exponent=str(a), gap=str(gap), cutoff_log2=str(cutoff)))
    assert cuts == old['bootstrap'], 'All seven bootstrap witnesses unchanged'
    q = a*(1-2*eta)
    margin = (1-eta)*q/(1+q)
    # Strict floor remains correct even if margin lies exactly on the grid.
    ticks = (margin.numerator * 10**24 - 1) // margin.denominator
    k = Q(ticks, 10**24)
    assert k == NEW_K and OLD_K < k < margin <= k + GRID
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000},
                           'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6) - Q(51*20161, 25)}}
    prior = A.assembly(a, b, bridge, OLD_K, eta=eta, beta=beta)
    assert {n: str(v) for n, v in prior['strict_constraints'].items()} == old['outer']
    refined = A.assembly(a, b, bridge, k, eta=eta, beta=beta)
    assert refined['minimum_margin'] == margin
    assert refined['margins'] == prior['margins']
    assert len(refined['strict_constraints']) == 47
    assert all(v > 0 for v in refined['strict_constraints'].values())
    # Independent exact update of the previously admitted 47 inequalities:
    # only the seven `margin - kappa` comparisons change.
    changes = 0
    for name, before in old['outer'].items():
        after = Q(before)
        if name.endswith('_above_kappa'):
            changes += 1
            after -= k - OLD_K
        assert after == refined['strict_constraints'][name] and after > 0
    assert changes == 7
    rejected = []
    for name, candidate in [('next_1e24_grid', k+GRID),
                            ('equality_at_margin', margin),
                            ('next_1e18_grid', OLD_K+Q(1, 10**18))]:
        try:
            A.assembly(a, b, bridge, candidate, eta=eta, beta=beta)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError('Invalid candidate accepted: ' + name)
    return dict(
        status='PASS_CONDITIONAL_T37_ROUNDING_REFINEMENT',
        contribution='Final rational rounding only; no new circuit or asymptotic construction.',
        kappa=str(k), kappa_decimal=decimal(k), baseline_kappa=str(OLD_K),
        absolute_gain=str(k-OLD_K), absolute_gain_decimal=decimal(k-OLD_K),
        relative_gain_percent=decimal(100*(k/OLD_K-1)),
        grid=str(GRID), strict_margin=str(margin), strict_margin_decimal=decimal(margin),
        absorption_gap=str(margin-k), absorption_gap_decimal=decimal(margin-k),
        complex_lower=str(b), bit_lower=str(c),
        charged_prefix_bits=dict(complex=1024, bit=512),
        bootstrap=cuts, complex_moments=complex_moments, bit_moments=bit_moments,
        strict_constraints={n: str(v) for n, v in refined['strict_constraints'].items()},
        constraints_checked=47, unchanged_constraints=40, shifted_constraints=changes,
        controls_rejected=rejected,
        upstream_pr='https://github.com/CrocSwap/integer-mult-bounds/pull/942',
        upstream_source_pins=current_binding['pins'],
        upstream_receipts={p: sha(work/p) for p in
                           ('RESULT.json', 'FINAL-BINDING.json', 'strict/ASSEMBLY.json')},
        reused_completed_ancestry=result['reused_completed_baseline'],
        scope=result['scope'],
        verifier_sha256=sha(Path(__file__)),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    certificate = verify(args.work.resolve(), args.baseline.resolve())
    encoded = json.dumps(certificate, indent=2) + '\n'
    if args.output:
        with args.output.open('x') as target:
            target.write(encoded)
        print(certificate['status'], certificate['kappa_decimal'])
    else:
        print(encoded, end='')
