"""Logarithmic block factorization of the retained triangular CRT map.

This is an address-level specification, not a fast tape FFT implementation.
The production spectral implementation and its explicit prerequisites are
proved in CRT.md. All arithmetic here is exact and standard-library only.
"""
from math import prod


def need(condition, message):
    if not condition:
        raise ValueError(message)


class TriangularCRT:
    def __init__(self, moduli):
        self.moduli = tuple(moduli)
        need(bool(self.moduli) and all(s >= 2 for s in self.moduli), 'positive axes')
        self.prefix = tuple(prod(self.moduli[:i]) for i in range(len(self.moduli)))
        self.units = tuple(pow(P, -1, s) for P, s in zip(self.prefix, self.moduli))
        self.coeff = tuple(tuple(u * P % s for P in self.prefix[:i])
                           for i, (u, s) in enumerate(zip(self.units, self.moduli)))

    def valid(self, a):
        return len(a) == len(self.moduli) and all(0 <= x < s for x, s in zip(a, self.moduli))

    def direct(self, a):
        need(self.valid(a), 'valid source address')
        k = sum(x * P for x, P in zip(a, self.prefix))
        return tuple(u * k % s for u, s in zip(self.units, self.moduli))

    def block_forward(self, a, lo, hi):
        return tuple((a[i] + sum(self.coeff[i][j] * a[j] for j in range(lo, i)))
                     % self.moduli[i] for i in range(lo, hi))

    def block_inverse(self, a, lo, hi):
        recovered = []
        for i in range(lo, hi):
            recovered.append((a[i] - sum(self.coeff[i][j] * recovered[j-lo]
                                         for j in range(lo, i))) % self.moduli[i])
        return tuple(recovered)

    def layers(self):
        # Binary blocks with a possibly short final block need no padded axes.
        d = len(self.moduli)
        width = 2
        while width < 2*d:
            nodes = tuple((lo, min(lo+width//2, d), min(lo+width, d))
                          for lo in range(0, d, width) if lo+width//2 < d)
            if nodes:
                yield nodes
            width *= 2

    def offsets(self, a, node, wrong_controls=False):
        lo, mid, hi = node
        original = tuple(a[lo:mid]) if wrong_controls else self.block_inverse(a, lo, mid)
        return tuple(sum(self.coeff[i][j] * original[j-lo] for j in range(lo, mid))
                     % self.moduli[i] for i in range(mid, hi))

    def apply_layer(self, a, nodes, inverse=False, wrong_controls=False):
        out = list(a)
        for node in nodes:
            lo, mid, hi = node
            shifts = self.offsets(a, node, wrong_controls)
            for i, shift in zip(range(mid, hi), shifts):
                out[i] = (out[i] + (-shift if inverse else shift)) % self.moduli[i]
        return tuple(out)

    def execute(self, a, inverse=False, wrong_controls=False, reverse_forward=False):
        need(self.valid(a), 'valid source address')
        layers = tuple(self.layers())
        if inverse or reverse_forward:
            layers = layers[::-1]
        for nodes in layers:
            a = self.apply_layer(a, nodes, inverse, wrong_controls)
        return a

    def phase_exponent(self, a, nodes, frequency_units, inverse=False):
        """Numerator mod S_J for exp(-2 pi i * numerator / S_J).

        a contains control values and *frequency* values on the target axes.
        The retained transform reads frequency t_i*k_i, not k_i.
        """
        targets = tuple(i for _, mid, hi in nodes for i in range(mid, hi))
        S = prod(self.moduli[i] for i in targets)
        exponent = 0
        for node in nodes:
            _, mid, hi = node
            for i, shift in zip(range(mid, hi), self.offsets(a, node)):
                exponent += frequency_units[i] * a[i] * shift * (S // self.moduli[i])
        return ((-exponent if inverse else exponent) % S), S
