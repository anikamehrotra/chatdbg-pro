# ChatDBGPro: GDB Is All You Need

Public release accompanying the COS 484 (Princeton, 2026) paper of the same
title.

**Authors:** Ibraheem Amin, Shreyas Garimella, Anika Mehrotra
(`{ia8920, sg6104, am9487}@princeton.edu`)

ChatDBGPro is a research fork of [plasma-umass/ChatDBG][upstream] that
evaluates how much of an LLM-driven debugger's behavior comes from the
underlying model versus the structure of the debugger surface itself. The
study sweeps eight contemporary models across two tiers of debugger access
(bash-only and `gdb`/`lldb`-only) over a 39-case corpus split between
hand-authored synthetic crashes and real-world bugs drawn from BugBench,
BugsCPP, and reverted patches in cJSON / Lua / Mongoose / SQLite / zlib.

> **Status:** This repository is being populated. The placeholder commit
> exists so the URL can be cited in the paper. The full code, scored
> benchmark results, and figure-regeneration scripts will land in a single
> tagged release shortly (`v0.1-paper`).

## What will be here

- `src/chatdbg/` — the fork (modified GDB/LLDB tool surface, tier configs,
  command allow-list).
- `bench/` — orchestrator, judge, charts, drivers, configs, and the 39
  test cases.
- `bench/results/final_paper_bench/` — scored 640-cell panel (synthetic +
  real-world × T1 + T3 × 8 models) used to produce every figure in the
  paper.
- `paper/` — the `.tex` source and compiled PDF.
- `docs/REPRODUCE.md` — clone → Docker → `regen_figures` walkthrough.

## Upstream credit

ChatDBG was introduced by Zheng, Berger et al.:
- Paper: <https://arxiv.org/abs/2501.18504>
- Code: <https://github.com/plasma-umass/ChatDBG>

This work extends ChatDBG's procedure with structured tier ablations, a
larger and more cutoff-robust test corpus, and an LLM-as-judge scoring
pipeline. License (Apache-2.0) is inherited from the upstream project.

## Citation

A `CITATION.cff` will be added with the full release. For now:

```
Amin, I., Garimella, S., Mehrotra, A.
"ChatDBGPro: GDB Is All You Need."
COS 484 (Princeton), 2026.
```

[upstream]: https://github.com/plasma-umass/ChatDBG
