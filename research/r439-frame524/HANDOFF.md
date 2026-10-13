# Research handoff

Base `f567884aeb8851b6e794af1184119a3bfbe1e631`; branch
`research/bit-seed13-20261013`; assignment seed **13**, bit-supplier track.

## Best verified result

Replace PR589 frame-524 `B[449:490]` using `CANDIDATE.json`, rebuild literal
cleanup, and obtain 26 instead of 41 block ADDs / 24,275 instead of 24,305
complete local ADDs. The canonical reconstructed word SHA256 is
`997e9d9457ff92691bcab8c4d8e754cd13a0cbf2510406280771ac6a1dcc5072`.
The reverse positive prefix improves to 1,057,866; payload stays 93 bits.
Paid profile and rank mass remain unchanged. **No new bit c or κ.**

The exact fixed-factor scheduling minima are 12 and 15. Their sum 27 proves
that this comparison class cannot match the 26-operation whole-block witness.
The global optimum in broader positive or XOR circuit classes is unknown.

## Replay and evidence

```sh
python3 -I -B research/r439-frame524/verify.py
python3 -I -B research/r439-frame524/check_package.py
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r439-frame524/native.py --output /fresh/output
```

`CERTIFICATE.json`, `FACTOR-COMPARISON.json` and `NATIVE.json` retain exact
finite evidence. `SOURCES.json` pins all execution inputs. `VALIDATION.md`
and `VALIDATION.json` separate completed checks from unclaimed obligations.
The fresh original bit-supplier replay succeeds and matches its exact c.

The local worktree also retains its isolated `.venv`, Boost headers under
`build/deps/boost_1_86_0`, baseline outputs under `build/pr589-baseline`, native
outputs under `build/frame524-native-frozen`, and validation logs under
`build/validation`. These build artifacts are deliberately uncommitted.

## Search coverage and rejected directions

Completed all 12,000 seeded factorization trials; 6,277 reached the identity.
Best accepted length 26 was first found at trial 48. No global optimality
claim follows. Fixed-factor exact enumeration covers 2,080 states and 9,608
edges. Frame-only optimization was already covered by PR886. Whole-block
destination-once scheduling is excluded for frame 524 by concurrent PR891;
our witness changes that class by using intermediate values and multiple
writes. See `EXPERIMENTS.md` and the head-pinned `OVERLAP.json`.

## Justified next steps

1. If integrating this word, rebuild its hosted parent, physical invoice and
   assembly against the then-selected sources. Local dominance and identical
   paid profiles do not substitute for that replay.
2. A shorter whole-block search should introduce an exact lower-bound method
   or a genuinely different circuit class; another random seed alone adds
   little to the completed search.
3. Check compatibility explicitly before combining the distinct frame-507,
   frame-521, frame-523 and phase-A proposals. Their reported savings were
   not composed here.

Maintainer acceptance, replacement hosting, outer assembly, global XOR
optimality and the inherited all-size/analytic theorem remain outside this
result. Attribution and substantial AI assistance are disclosed in NOTICE.md.
