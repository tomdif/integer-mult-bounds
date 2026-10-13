# T37 final rounding refinement

The unchanged PR942 construction admits the rational value

**κ = 0.001661960547713947858091**

under its existing conditional finite-construction assumptions. This exceeds
PR942's published `0.001661960547713947` by `8.58091 × 10⁻¹⁹`, or about
`5.163125 × 10⁻¹⁴%`. This is solely a refinement of the final rounding grid
from `10⁻¹⁸` to `10⁻²⁴`. It is not a new circuit, geometry, packing improvement,
or meaningful performance breakthrough.

The construction and its improvement over PR890 belong to
[jon314159's PR942](https://github.com/CrocSwap/integer-mult-bounds/pull/942).
This package uses that source at commit
`1960cfa919a0945d0ca4cb14ea96237000037903`, including its attributed U8,
owner-map, bit-supplier, moment, and assembly dependencies. It leaves that
package and all original replay receipts unmodified.

## Exact argument

Keep the certified complex rate `b = 0.001664727258740678855772`, bit rate
`c = 0.001733427039589844234749`, all seven bootstrap steps, and
`η = β = 10⁻²⁴`. For the final bootstrapped bit saving `a`, set
`q = a(1 − 2η)`. The strict outer margin is the rational number
`m = (1 − η)q/(1 + q)`, whose decimal expansion begins

`0.001661960547713947858091490826766299749683299895306672687882...`

The new κ is strictly below this margin by approximately
`4.908267663 × 10⁻²⁵`. The original 47 exact rational inequalities consist of
40 constraints independent of κ and seven comparisons of a margin with κ.
The verifier recomputes all 47 through the retained engine, independently
subtracts `κ_new − κ_old` from exactly the seven affected old constraints,
and checks that both calculations agree and every result remains positive.

The next `10⁻²⁴` grid point and equality at the margin are rejected. So is
the next original `10⁻¹⁸` grid point. PR942's fixed-family optimality statement
on the original grid is fully consistent with this refinement.

## Reproduction

First run the unchanged PR942 verifier, or supply a completed run from that
verifier. Its `--baseline799` option explicitly permits complete, checked
ancestry reuse. Then run:

```sh
python -B research/t37-rounding-refinement/verify.py \
  --work /absolute/path/to/completed-t37-run \
  --baseline /absolute/path/to/completed-frontier799-run \
  --output /absolute/path/to/new-certificate.json
```

The refinement verifier reruns PR942's complete final source/receipt binding,
checks both moment endpoints using the two exact rational interval engines,
and reconstructs all seven bootstrap cutoffs. The complex prefix charge stays
1024 bits and the bit prefix charge stays 512 bits. Outputs are created
exclusively; existing certificates are never overwritten.

`CERTIFICATE.json` records this run's exact rational witnesses and source
hashes. `VALIDATION.json` identifies the verified upstream run. The full T37
verification passed all 13 stages, with freshly checked U8 construction and
T37 admission; the previously completed ancestry was explicitly reused.

The inherited all-size/compiler, common-label and physical-realization,
precision/tape, analytic-transfer, and bit H1–H5 assumptions remain. This
does not claim an unconditional theorem or formal proof-assistant validation.

Prepared with OpenAI Codex assistance. Apache-2.0; all upstream attribution
remains in the referenced source files and notices.
