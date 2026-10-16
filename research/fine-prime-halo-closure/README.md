# An explicit fine-prime halo routine that fits the budget

**Scoped proof under explicit norm premises; no complete multiplication theorem.**
[PROOF.md](PROOF.md) supplies a direct polynomial-iteration inverse on the small
halo-face volume. It makes the online work explicit after the fine-prime
conditioning bound enlarges the locality window.

Assuming bandwidth below p and matrix/inverse norms at most p^10, a dyadically
scaled Neumann polynomial with 2p^42 iterations has error at most
`p^10 exp(-p^2)` and radius below p^48. Sequential banded passes and schoolbook
coefficient arithmetic cost at most `O(V p^50)` eventually. On the retained
face volume, the total exponent is `epsilon + beta - 30 < -28`, so it fits the
current outer budget with ample room. This does not change kappa.

[NARROW.md](NARROW.md) also supplies a dimension-independent spectral bound
for the narrow Gaussian and its retained banded Schur sections. It combines
the sharp Gaussian row gap with bandwidth; row dominance alone would not
justify that spectral bound. The actual reference rounding accuracy remains
an explicit premise. [BROAD.md](BROAD.md) gives the separate finite/bilateral
Gaussian LDU argument for the broad map, including both row and column norms
and an explicit physical-prefix Schur hypothesis. The terminal cyclic-cut join
and actual reference-rounding bounds remain open.

The exact tests cover nonnormal rational matrices, both residual identities,
finite-section locality, necessary scale/adjoint/order controls, the dyadic
scaling inequalities and the actual ledger. Reproduce with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fine-prime-halo-closure
```

[RESULT.json](RESULT.json) is checked in full, including with assertions disabled.
Finite examples are not a proof of the spectral or asymptotic statements;
their quantified proofs are in the note. The code is an exact matrix checker,
not a tape simulation or a full Gaussian transform implementation.

## Open next questions

Bind the analytic bounds to the actual reference-rounding generator, settle
terminal cyclic prefixes whose omitted gap is narrower than the bandwidth,
and complete the capped-interior/source-transform assembly. Then integrate
contract T with the corrected logarithmic CRT and final integer recovery.
The first step is the source-bound rounding/capped-circuit join; the written
norm estimates and passing checks do not establish that whole transform.

## Credit

Prepared for Thomas DiFiore with substantial OpenAI Codex assistance, without
subagents. Apache-2.0. The Neumann locality argument, fine-prime powers and
setup/online precision separation are due to Chafik Boukhalfa's
[PR1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786).
Vlado Vojdanovski's PR1673 supplies the core/first-face decomposition and exact
duplication formula. This contribution supplies a direct online alternative
and its conservative cost join, not a new inverse-locality theorem. The earlier
source instead invokes capped circuits for online work; no error in that claim
is alleged. The current supplier and ledger retain their predecessor credit.
