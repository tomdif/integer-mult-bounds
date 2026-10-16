"""Exact finite CRT, Fourier-label and normalization verification."""
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import gcd, prod
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from crt_layers import TriangularCRT, need


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def divide_exact(a, b):
    a = list(a)
    q = [0] * max(1, len(a)-len(b)+1)
    while len(a) >= len(b) and any(a):
        need(a[-1] % b[-1] == 0, 'integral monic division')
        k, c = len(a)-len(b), a[-1] // b[-1]
        q[k] += c
        for j, x in enumerate(b):
            a[k+j] -= c*x
        trim(a)
    need(not any(a), 'exact polynomial quotient')
    return tuple(trim(q))


@lru_cache(None)
def cyclotomic(n):
    poly = (-1,) + (0,)*(n-1) + (1,)
    for d in range(1, n):
        if n % d == 0:
            poly = divide_exact(poly, cyclotomic(d))
    return poly


def reduce_poly(a, modulus):
    a = list(a)
    while len(a) >= len(modulus):
        c, k = a[-1], len(a)-len(modulus)
        for j, x in enumerate(modulus):
            a[k+j] -= c*x
        trim(a)
    return tuple(a + [0]*(len(modulus)-1-len(a)))


def root_sum(n, exponents):
    terms = [0] * n
    for e in exponents:
        terms[e % n] += 1
    return reduce_poly(terms, cyclotomic(n))


def check_addresses():
    cases, rejected = [], set()
    for moduli in [(3,), (3,5), (3,5,7), (3,5,7,11), (2,3,5,7,11)]:
        crt = TriangularCRT(moduli)
        count = 0
        for a in product(*(range(s) for s in moduli)):
            expected = crt.direct(a)
            actual = crt.execute(a)
            need(actual == expected, 'layered CRT equals independent integer residue oracle')
            need(crt.execute(actual, inverse=True) == a, 'complete CRT inverse')
            # Check each inductive intermediate, not only the endpoint.
            current = a
            for nodes in crt.layers():
                current = crt.apply_layer(current, nodes)
                for lo, _, hi in nodes:
                    need(current[lo:hi] == crt.block_forward(a, lo, hi), 'block invariant')
            if crt.execute(a, wrong_controls=True) != expected:
                rejected.add('use_transformed_controls_without_block_inverse')
            if crt.execute(a, reverse_forward=True) != expected:
                rejected.add('reverse_forward_layer_order')
            count += 1
        need(len(tuple(crt.layers())) == (len(moduli)-1).bit_length(), 'ceiling logarithmic depth')
        cases.append(dict(moduli=moduli, addresses=count, layers=len(tuple(crt.layers()))))
    need(len(rejected) == 2, 'both address mutations have witnesses')
    witness = TriangularCRT((3,5)).direct((1,0))
    need(witness == (1,2) and sum(x.bit_count() for x in witness) == 2,
         'CRT is not a binary-coordinate permutation: input (1,0) has weight one')
    return cases, sorted(rejected)


def check_fourier():
    checks = 0
    rejected = set()
    # Exact sandwich for every source, destination and shift, using primitive
    # roots in Q[X]/Phi_s. Positive shift sends input j to output j+shift.
    for s, t in [(3,4), (5,8), (7,8), (9,16), (15,16)]:
        need(gcd(s,t) == 1, 'retained frequency relabel is a unit')
        zero = (0,)*(len(cyclotomic(s))-1)
        for j, y, shift in product(range(s), repeat=3):
            # F^- has exponent -t*k*j; phase -t*k*shift; F^+ +t*k*y.
            total = root_sum(s, (t*k*(y-j-shift) for k in range(s)))
            expected = (s,) + zero[1:] if y == (j+shift) % s else zero
            need(total == expected, 'retained Fourier sandwich equals exact shift')
            if shift == 1 and j == 0 and y == 1:
                wrong = root_sum(s, (t*k*(y-j)-k*shift for k in range(s)))
                if wrong != expected:
                    rejected.add('omit_retained_frequency_unit')
                need(Fraction(total[0],s*s) == Fraction(1,s), 'two normalized transforms return shift/S')
                rejected.add('omit_final_S_scale')
            checks += 1
    # Execute the phase compiler on complete two-target spectra. A sign or
    # denominator error here is separate from the one-axis Fourier identity.
    crt = TriangularCRT((3,5,7,11))
    units = (4,8,8,16)
    phase_checks = 0
    for nodes in crt.layers():
        for a in product(*(range(s) for s in crt.moduli)):
            exponent, S = crt.phase_exponent(a, nodes, units)
            reference = Fraction(0)
            for node in nodes:
                _, mid, hi = node
                original = crt.block_inverse(a, node[0], mid)
                for i in range(mid,hi):
                    shift = sum(crt.coeff[i][j]*original[j-node[0]] for j in range(node[0],mid))
                    reference += Fraction(units[i]*a[i]*shift, crt.moduli[i])
            need((reference-Fraction(exponent,S)).denominator == 1, 'conditional tensor phase')
            inverse, S2 = crt.phase_exponent(a, nodes, units, inverse=True)
            need(S == S2 and (exponent+inverse) % S == 0, 'inverse diagonal phase')
            phase_checks += 1
    need(len(rejected) == 2, 'frequency and normalization mutations detected')
    return dict(sandwich_entries=checks, conditional_phase_checks=phase_checks,
                arithmetic='exact integer cyclotomic reductions and rational phases'), sorted(rejected)


def main():
    addresses, address_controls = check_addresses()
    fourier, fourier_controls = check_fourier()
    receipt = dict(status='PASS_SCOPED_CRT_FACTORIZATION', addresses=addresses,
                   fourier=fourier, rejecting_controls=address_controls+fourier_controls,
                   scope='Exact finite specification checks. No Gaussian FFT or fixed-tape asymptotic implementation is executed.')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
