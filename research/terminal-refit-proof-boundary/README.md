# What is proved, and what still separates the bound from a multiplication theorem

The four terminal refits have a general algebraic justification. Lean checks
the commuting additions and a common-label program replacement theorem for
arbitrary modules and arbitrary inputs. The source check binds the eight
literal edited blocks, four in each provider, to the theorem's scalar premises.
This is a scoped proof. It does **not** prove that the entire supplier is a
correct, sufficiently fast physical machine at every input size.

The preceding research commit is
`db3248c232244daddc8c0c9de5f61c23f4e2aa83`. Its conditional saving remains
`0.001722052684227397319529 - 10^-46 - 10^-70` and its release manifest is
unchanged. The user requested this proof audit after authorizing that branch's
publication. All source pins are in [SOURCES.json](SOURCES.json).

## The refit proof

Let register r have decoded value x_r and physical value T_A(x_r), where T_A
is an invertible linear map for its current label A. An exact change A to B
applies T_B T_A^-1. An addition between equal labels therefore changes decoded
values by x_d := x_d + a x_s. A scalar multiplication changes x_d := c x_d.
Induction over the literal event list gives the common-label formula

```
physical run = D(final labels) · scalar run · D(initial labels)^-1.
```

This is the existing Lemma G of DreamingOfClouds and its credited predecessors,
copied without modification. Our `replace_program` is its direct corollary:
two well-labelled programs with exact transports, equal initial/final labels
and the same scalar action have the same physical action. Their intermediate
labels need not match. In particular, the earlier rank-seven addition need
not leave every source at the old intermediate rank-eight label.

For d distinct from s and t, neither addition changes the other source:

```
(x_d + a x_s) + b x_t = (x_d + b x_t) + a x_s.
```

`adds_commute` proves this equality on the **whole register file**, for every
semiring, module and input. `scale_then_adds_commute` retains any preceding
scale. It never moves that scale across an addition. The literal instances are:

| Destination | Source with coefficient 1/2 | Source with coefficient 1 | Preceding scale |
|---:|---:|---:|---:|
| 408 | 42 | 105 | none |
| 424 | 16 | 44 | none |
| 428 | 416 | 430 | -1 |
| 412 | 400 | 414 | -1 |

These are the only scalar changes in the terminal blocks. The release already
checks the entire scalar action, regenerated inverse cleanup, frame legality,
unchanged endpoint interfaces and both fresh native providers. The present
source checker independently authenticates the released package and matches
the literal blocks to the universal commutation premise.

For f columns take T_A to be the tensor product of its unary labels and keep
each role coefficient a, b or c once. Tensor products preserve unary products
and inverses. The module may be the full array space; no input separability or
independence of dirty helpers is required. Gareth Davidson's existing
[tensor-lift proof](../lean-common-label-tensor-lift/README.md) formalizes this
step and the coordinate-space identification. We inspected that source and
its reported kernel receipt; we did not rerun its separate pinned toolchain.

Our fresh Lean run proves the three generic lemmas, not a generated Lean
import of all native recipes, frames, 632 input columns or 271,728 owners.
The finite source check and mathematical application remain explicitly
separate from the kernel proof. Exact physical recipe realization is still
a hypothesis of `replace_program`; its running time is not in the statement.

## The assumption audit

| Obligation | Evidence and remaining work |
|---|---|
| Our four commuting refits | Generic Lean proof plus literal source bindings and the existing complete finite release. No extra tensor-width restriction is needed under exact transports. |
| PR589 H1-H5 | These are finite structural conditions, already covered by the predecessor checker. A fresh run checks all 661 symbolic columns and all five conditions. The tested compressed word equals the exact PR589 Git bytes despite its later directory rename. [Receipt](evidence/BIT-H1-H5.log). This is not a new proof of the bit compiler. |
| Common-label and tensor semantics | Existing Lemma G and tensor-lift proofs establish the quantified implication. A source-faithful formal import and physical implementation of the current recipes are separate. |
| Whole-call hosting | [PR589's exact-stream proof](../pr589-five-helper-hosting/PROOF.md) handles correlated helpers, cover classes and chronology. Our complex release checks concrete owners and costs. These results must be joined to actual routes, complete cover enumeration and the recursive caller. |
| Uniform recursion and storage | [BIT recursive closure](../selected-bit-recursive-closure/PROOF.md), the [parking boundary](../recursive-parking-boundary/README.md), and newer caller/storage work address pieces of this. Restored bytes alone do not imply time independent of ancestor length. The concrete current caller must obey the locality and volume contracts at every recursive entry. |
| Precision and exact recovery | PR2287 and the [Gaussian grid audit](../complex-grid-prefix-audit/README.md) give written bounds for their exact primitives and older construction. We have not instantiated and composed their full recursive prefix bounds with this newer supplier and outer witness. Finite norm invoices alone do not supply that proof. |
| Analytic/outer transfer | The release verifies exact inequality ledgers. The Gaussian maps, tensor circuits, tape implementation, rounding and integer-recovery argument need a joined all-size proof under the same parameters. Arithmetic success does not discharge those implementation hypotheses. |

The broadly repeated phrase “H1-H5 assumptions remain” should therefore not be
read as saying that no one has checked the finite conditions. They hold for
the pinned word. The unresolved implication is from the exact stream and
finite certificates to the complete costed implementation.

There is also a separate [external Lean development](https://github.com/platypii/integer-mult-bounds-lean/tree/4f40b5bc74235274835fe6952b9b90ac414786b0),
credited to Dan Brown and Kenny Daniel, with a stated end-to-end saving
`2^-34`; [PR2411](https://github.com/CrocSwap/integer-mult-bounds/pull/2411)
links it. We read its pinned `Statement.lean` and `Theorem.lean`. We did not
rebuild its complete import closure or audit the machine model. That separate,
much weaker numerical statement does not establish our saving or resolve the
interface obligations above by substitution.

## Reproduction

Read-only literal-source check, without claiming a Lean run:

```sh
python3.12 -I -B research/terminal-refit-proof-boundary/verify.py
```

Fresh kernel build with pinned, already populated dependency packages:

```sh
python3.12 -I -B research/terminal-refit-proof-boundary/verify.py \
  --lake /absolute/lean-4.32.2/bin/lake \
  --packages /absolute/pinned-lake-packages \
  --work /absolute/fresh-refit-proof-build \
  --out /absolute/new-refit-proof-receipt.json
```

The work and output paths must not exist. Dependency commits and tracked source
cleanliness are checked before building; local proof objects are built afresh.
The library cache is reused. Two false statements must fail on their
mathematical goals: commuting a self-reading addition and replacing a program
with a different scalar action. The three theorem axiom reports admit only
standard Lean foundations. See [KERNEL.json](KERNEL.json) for actual results.
Alternatively, `lake exe cache get` followed by `lake build` in an isolated
copy of `lean/` obtains and builds the pinned project.

## Open next questions

1. Bind the actual native recipe interpreter to the common-label theorem,
   including tensor phases and restored spectators. Start with one changed
   provider's emitted recipe list and a source-faithful formal importer.
2. Port the existing recursive machine and precision arguments to the exact
   current supplier and outer witness. Start with one full child entry/return,
   paying physical routing, retained storage and intermediate precision at
   the same chronological cuts. The unproved full implementation is the
   blocker; another parameter search does not close it.

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without
delegated agents. Credit DreamingOfClouds, Zhihao Chen and the Lemma G lineage;
Gareth Davidson's tensor audit and fresh-build conventions; Mason Hale and
Jeremy Diviney's construction; Jose Manuel and the machine/precision authors
linked above; all original notices remain intact. Apache-2.0. No independent
human review or complete multiplication theorem is claimed.
