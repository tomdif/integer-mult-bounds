# Validation and limits

The exact base is `f567884aeb8851b6e794af1184119a3bfbe1e631`. All new files are
under `research/r439-frame524/`; no selected supplier, imported source, or
upstream manuscript is edited. Source digests are in `SOURCES.json`; exact
results are in `CERTIFICATE.json`, `FACTOR-COMPARISON.json` and `NATIVE.json`.

## Completed local checks

- Rebuilt and replayed the **original PR589 bit supplier** with its complete
  `tune/verify.sh` pipeline, exit 0, 158 seconds reported. This includes source
  and manifest checks, word rediscovery, exact geometry/interfaces, native
  multistage checks, word/record controls, nine/eleven-stage hosted invoices
  and both original control suppliers. It reproduced nine-stage
  `c=1733427039589844234749/10^24` and eleven-stage
  `c=855475950388791987811/(5*10^23)` exactly.
- New local verifier passes normally and in isolated optimized Python.
  Independently computed integer maps and all 4,096 local Boolean inputs
  agree; the inherited exact checker verifies 661 arbitrary dirty columns,
  636 closed frames, and H1–H5 and U/J/K/U-inverse obligations.
- Independent set-valued replay of actual exported instructions verifies
  the endpoint, COPY/ERASE lifecycle, frame paths, paid histogram and costs.
  Nine local corruption controls are rejected. Stale old cleanup is also
  tested as an endpoint-positive but H4-negative control.
- Fixed-factor dynamic programming and the separate integer
  back-substitution/distance-potential checker agree on all 2,080 states and
  9,608 feasible edges. Legal witnesses attain the lower bounds 12 and 15.
- Fresh unchanged C++ legality and 5/9/11-stage checkers pass for both original
  and replacement words. They verify 883/1,327/1,549 formal columns and reject
  96 bridge-omission controls in total. Python and C++ ADD counts, rank profiles
  and positive-prefix/payload bounds match. The frozen native receipt was
  reproduced in another fresh output directory.
- The 12,000-trial seeded search was rerun and reproduced `CANDIDATE.json`
  byte for byte. It is sampled search coverage, not an optimality proof for
  the broader class.
- Minimal-source relocation to a path containing spaces passes under
  isolated optimized Python. Five candidate/source/certificate corruptions
  fail; an existing output directory and its contents are preserved.
- The selected-result/source-binding check and Python compilation pass.

The recorded environment is macOS, Python 3.11.14, Apple clang 21.0.0,
Boost 1.86.0. Python dependencies for the original supplier replay were
installed in an isolated virtual environment. Boost headers were extracted
locally; no system installation was changed. `VALIDATION.json` records exact
commands, outcomes, environment and hashes of the retained local logs.

## Development findings

Review caught a mechanical adaptation that changed a MOVE upper bound to
1260. It was corrected to `0 <= register < 661`, and a temporary-register
MOVE rejection test was added before freezing the package. A later package
control expected a different error message after adding the factor checker;
structural gate-count validation was moved earlier. The corrupted candidate
was rejected throughout. Both issues are recorded to distinguish development
checks from final evidence.

## What this result does not establish

The original bit supplier was replayed in full. The **replacement** has local
and native multistage verification; its hosted parent program, physical
invoice and outer assembly were not rebuilt. The selected complex supplier
and full multiplication theorem were not independently reconstructed here.
No new κ, global XOR optimality, Lean proof, independent human review or
runtime benchmark is claimed. The unchanged local paid profile by itself
does not certify compatibility with every inherited hosting interface.

## Complete repository check coverage

All **18 top-level groups** of `make verify` passed across the initial run
and documented resumes, including **87 isolated test modules** and **20
historical patch-application checks**. This is not reported as a single
successful `make verify` invocation: that invocation exited 2 when an unchanged
historical target passed `-fopenmp` to Apple clang.

The initial run completed the first twelve groups, through `verify-research`,
including a fresh original PR741/PR589 composition replay. The next invocation
used the already-installed GCC 16.2.0 and completed `verify-strips` and
`verify-clones`. It stopped because an older compiler command did not consume
`BOOST_INCLUDE`. A retry also refused the output directory left by that failed
build; those task-generated files were preserved under
`build/positive-skip-exact-missing-boost`.

After exposing the same isolated Boost headers through `CPLUS_INCLUDE_PATH`,
this fresh-output resume completed with exit 0:

```sh
CXX=/opt/homebrew/bin/g++-16 \
BOOST_INCLUDE=/path/to/boost CPLUS_INCLUDE_PATH=/path/to/boost \
OMP_NUM_THREADS=4 make verify-positive verify-joint verify-pair verify-tests
```

The isolated Python environment was on PATH for every invocation. No source
or expected mathematical result was altered to resolve these setup issues.
The only tracked changes after the entire suite are this research package.
Exact command outcomes and log digests are in `VALIDATION.json`.
