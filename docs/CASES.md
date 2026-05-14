# Test case corpus

The headline matrix evaluates 39 cases split into two panels (20 synthetic
+ 19 real-world). Cases live under `bench/cases/<case-id>/` and each
ships:

- `case.yaml` — metadata, ground-truth crash location, pre-registered
  judging rubric, and an optional `buggy_binary_path` for non-default
  build outputs.
- One or more source files (`.c`, `.cpp`, `.h`, etc.).
- Optional `stdin.bin` for cases triggered by a crafted input.

## Synthetic panel (20 cases)

Hand-authored crashes written in 2026, postdating every evaluated model's
training cutoff. Eleven cover bug classes that were underrepresented in
ChatDBG's original suite (signed/unsigned loops, integer overflow on
allocation, double-free on error paths, vector-iterator invalidation,
off-by-one, use-after-free on linked lists, uninitialized stack reads,
stack-buffer overflows). Nine are direct ports of ChatDBG's original
suite, retained as a calibration set against the upstream paper.

Locations:
- `bench/cases/paper/` — original ChatDBG ports
- `bench/cases/<case-id>/` — hand-authored 2026 crashes

## Real-world panel (19 cases)

| Source | Cases | How they crash |
|---|---|---|
| BugBench | 4 | Real reproducers from Lu et al. 2005 |
| Injected-repo (cJSON, Lua, Mongoose, SQLite, zlib) | 5 | Reverted known patches in pinned upstream versions |
| BugsCPP libtiff | 5 | Real bugs from the BugsCPP corpus |
| BugsCPP berry | 5 | Real bugs from the BugsCPP corpus |

The injected-repo cases reuse public patches that predate model cutoffs,
but pair them with novel failing inputs, crash signatures, and exact
repository states — pattern recognition is plausible but verbatim
retrieval is not.

## Extended sweeps (not in headline matrix)

Eleven additional cases used in ablations and longer sweeps:

- 6 from CrashBench (Ortega et al., 2024)
- 5 from the Juliet Test Suite covering CWE-121, 122, 126, 415, 416

These live under `bench/cases/external/` and are excluded from the
20-case + 19-case headline panels.

## `case.yaml` schema

```yaml
case_id: off-by-one-crc
language: c
description: >
  One-byte under-allocation of a CRC table triggers a heap overflow on
  the last update step.
ground_truth:
  function: crc16_update
  file: program.c
  line: 47
rubric:
  root_cause: |
    Model must identify that `tbl = malloc(255)` is one byte short for
    indices [0..255].
  local_fix: |
    Model must propose either `malloc(256)` or bounding the loop at
    `i < 255`.
  global_fix: |
    Model must propose the size fix AND note that any other
    255-element-table allocation in the file would have the same bug.
buggy_binary_path: ./bench_driver   # only when the build output isn't `a.out`
```

The judge sees `description`, the model's `collect.json`, and the three
rubric criteria — it never sees the source or the debugger transcript,
which keeps it from rewarding verbose work that ended in a wrong answer.
