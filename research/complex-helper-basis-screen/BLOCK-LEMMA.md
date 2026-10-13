# Full-rank correction blocks retain a frame requirement

This is a local statement about the retained monotone B-phase contract.
It is not a lower bound on κ, on arbitrary gate counts, or on alternative
recursive interfaces.

Let four arbitrary dirty source registers enter a monotone scalar-gate segment
with a common frame `U`. Let the coefficients of their initial values in four
recipient registers at a specified seam form an invertible rational matrix
`M`. An invertible recipient-coordinate change `S` replaces that matrix by
`S M`; an invertible source-coordinate change additionally gives `S M T^-1`.
Both remain invertible, so every recipient row has a nonzero source coefficient.

A nonzero coefficient implies a dependency path from at least one source to
that recipient. Under the native contract, an ADD uses a common frame on its
two operands, and register frames grow monotonically throughout the segment.
Consequently `U` propagates along that path. At the seam, **each of the four
recipient frames contains `U`**. Cancellation of other scalar coefficients
does not remove the surviving dependency.

This uses arbitrary independent dirty source columns. It does not apply when
those columns are fixed to zero or assumed equal. It also does not apply across
an unpriced frame descent, reset, non-scalar primitive, or changed entry/exit
contract. Such mechanisms require their own implementation and cost proof.

`evidence/FULL-RANK-BLOCKS.json` verifies the premise for the 12 natural
four-helper blocks used by the dense screen. Their exact determinants are 1
or 4. The common source-frame ranks are 4 or 5; all recipient entry frames
have rank 1. The certificate reconstructs the coefficient matrices from the
full scalar A/cut/B prefixes, rather than assuming the visible twelve-gate
submatrices account for every dependency.

This explains one limitation of these coordinate changes: sparse matrices and
fewer scalar additions cannot keep any of the four recipients below `U`.
It does **not** show that their complete recursive profiles are optimal.
A successful redesign might combine this forced growth with later growth in
a larger single jump, change another paid path, alter the interfaces, or share
work between calls. Those possibilities remain open. The unchanged costs in
`RESULT.json` are finite search results, separate from this lemma.
