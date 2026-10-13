# R439 frame 524: 41 additions to 26

This finite bit-circuit construction replaces `B[449:490]`, frame 524, in
DreamingOfClouds' PR589 tuned punctured R439 word. It preserves the exact
nonnegative integer forward map and decreases the reverse positive matrix
entrywise. Rebuilding the required literal reverse cleanup saves **30 native
ADDs**, from **24,305 to 24,275**. No new bit exponent or multiplication κ is
claimed.

| Quantity | Original | Replacement |
|---|---:|---:|
| Frame-524 block ADDs | 41 | 26 |
| Complete native ADDs, including cleanup | 24,305 | 24,275 |
| Forward positive prefix | 49,347 | 49,347 |
| Reverse positive prefix | 1,113,070 | 1,057,866 |
| Local payload envelope | 93 bits | 93 bits |
| Paid rank mass | 5,129 | 5,129 |

All 661 register frame paths, 439 helpers, nine COPY/ERASE pairs and the paid
histogram `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` are unchanged. The payload
stays below the inherited 104-bit cap.

The construction also separates two search classes. With the original split
after 17 operations held fixed, the two positive factors require **12 + 15 =
27** ADDs in their respective destination-once positive scheduling
classes. The 26-ADD whole-block witness improves on that restricted optimum.
Allowing repeated donors inside these write groups adds no feasible edges.
There is no claim that 26 is globally optimal. See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python3 -I -B research/r439-frame524/verify.py
```

Expected:

```text
PASS_R439_FRAME524 gates=41->26 native_adds=24305->24275 columns=661 rank_mass=5129 controls=9
```

The verifier checks pinned inputs, both integer matrices, all 4,096 local
Boolean inputs, all 661 dirty-input columns, E8 labels and closed frames,
the original H1–H5 interface, an independent set-valued interpretation of the
exported records, exact costs and prefix bounds, and nine rejection controls.
It independently verifies the fixed-factor lower bounds by integer triangular
back-substitution and feasible distance potentials; the comparison generator
uses F2 elimination and subset dynamic programming.

Additional checks:

```sh
python3 -I -B research/r439-frame524/factor_comparison.py
python3 -I -B research/r439-frame524/check_package.py
python3 -I -B research/r439-frame524/search.py --output /tmp/frame524-search.json
cmp /tmp/frame524-search.json research/r439-frame524/CANDIDATE.json
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r439-frame524/native.py --output /tmp/frame524-native-new
```

The native command needs C++17 and Boost headers and requires a new output
directory. It rebuilds and checks both words with the unchanged legality and
5/9/11-stage checkers: 883, 1,327 and 1,549 columns, plus 96 bridge-omission
controls. C++ and Python cost/prefix results must agree. `NATIVE.json` retains
the checked accounting; complete raw receipts and logs are written under the
requested output directory.

## Search, provenance and scope

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Assignment seed: **13**, bit-supplier track. The deterministic 12,000-trial
positive row-subtraction search completed 6,277 identity factorizations. It
found a reverse-dominated 27-ADD circuit at trial 4 and 26 ADDs at trial 48.
The stopping rule was fixed in advance. Failed paths and sampled coverage
do not constitute a lower bound on the broader class.

`CLAIM.json` records the scope and alternatives. `OVERLAP.json` preserves
relevant pending PR descriptions and exact heads at selection. No pinned
sprint issue existed; the claim is local. PR891 excludes whole-block
destination-once scheduling for this block. The new circuit permits
intermediate values and repeated writes. PR880 treats frame 507, PR884 frame
521, PR857/891 frame 523, and PR728/792 phase-A mini-nodes. Their savings are
not added to this result, and no mechanism-priority claim is made.

Final refresh through PR904 also checked its exact selected intervals: none
of its ten phase-B windows is at frame 524. The comparison is retained in
`PR904-COMPARISON.json`; its result has not been independently replayed or
composed with this one.

The selected conditional κ at the base is `0.001661634653669567`. This package
does not change the selected frontier, its inherited recursive cost profile,
or `upstream/`. A fresh replay of the original PR589 bit supplier is recorded
in [VALIDATION.md](VALIDATION.md); a rebuilt hosted invoice for the replacement
and a new outer assembly are not claimed. All inherited all-size/compiler,
mutable-source/common-label realization, whole-call hosting, precision/tape
and analytic obligations remain. Finite checks are not a formal proof of the
complete multiplication theorem or a measured end-to-end speedup.

Prepared for **Thomas DiFiore (@tomdif)** with substantial **OpenAI Codex
assistance**. Search and independent arithmetic checks were implemented by
one AI agent using different methods; no independent human or delegated-agent
review is claimed. See [NOTICE.md](NOTICE.md) for predecessor attribution.
