# Experiment log

Run started 2026-10-13 10:33 UTC. OS-random assignment seed 13 selected the
bit-supplier track. Base `f567884aeb8851b6e794af1184119a3bfbe1e631`.

1. Read the contribution guide, selected record, current status, ledger,
   supplier construction/interface and reproduction scripts. Retrieved 683
   open PRs over seven API pages and the latest closed/merged page. Reviewed
   relevant bodies and exact heads, with scoped reviews/attribution. Only
   issue #650 was open; no pinned sprint claim issue was found.
2. Rejected a frame-only bit search because PR886 already claims an exact
   optimum. Deferred additional star punctures because PR631/747/772/875
   cover broad threshold classes. Selected the uncovered frame-524 block:
   PR891 excludes destination-once whole-block scheduling, making intermediate
   writes a concrete change of search class.
3. Fixed a 12,000-trial search budget and seed 13. Starting from the exact
   positive matrix, repeatedly subtract a dominated row, using five fixed
   randomized scoring regimes. Each trajectory stops at the identity, a
   dead end, or 60 subtractions. Only shorter circuits whose reversed
   positive matrices are dominated by the baseline are accepted.
4. Trial 4 found 27 gates; trial 48 found 26. Completed all 12,000 trials;
   6,277 reached the identity, including 390 length-26 factorizations (not
   all are claimed reverse-dominated). No shorter accepted circuit appeared.
   The complete length histogram is in `CANDIDATE.json`.
5. Compared the two original fixed factors by exhaustive subset DP. Their
   destination-once positive minima are 12 and 15. A separate integer
   solver and distance-potential checker verified these exact bounds, including all nonnegative donor multiplicities; no feasible edge uses a repeated donor. The
   26-gate circuit improves on this restricted 27-gate class.
6. Froze the candidate; checked independent integer columns, every Boolean
   block input, the whole dirty-input circuit, literal cleanup, all frame
   paths, exported records, costs and precision bounds. Ran mathematical
   mutation controls, fresh native multistage checks, relocation/corruption
   checks and a byte-identical search replay. See `VALIDATION.md`.
7. Replayed the complete unchanged PR589 supplier successfully. Its c values
   match exactly. No new bit c or κ is inferred for the replacement.

Exact reproduction commands are in `README.md` and `VALIDATION.json`.
Broader global optimality and new hosted recursion are outside this run.
