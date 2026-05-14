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

## What's here

- `src/chatdbg/` — the fork (modified GDB/LLDB tool surface, tier configs,
  command allow-list).
- `bench/` — orchestrator, judge, charts, drivers, configs, and the 39
  test cases.
- `bench/results/final_paper_bench/` — scored 640-cell panel (synthetic +
  real-world × T1 + T3 × 8 models) used to produce every figure in the
  paper.
- `paper/` — the `.tex` source.
- `docs/REPRODUCE.md` — clone → install → `regen_figures` walkthrough.

## Quick start

```bash
git clone https://github.com/anikamehrotra/chatdbg-pro
cd chatdbg-pro
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env   # fill in API keys if you intend to re-run or re-judge

# Re-render every paper figure from the shipped score.json files (free):
python -m bench.charts --panel bench/results/final_paper_bench --out paper/figures/
```

See [`docs/REPRODUCE.md`](docs/REPRODUCE.md) for the full reproduction
guide, including the re-judge and full re-run paths.

## Provenance

`bench/results/final_paper_bench/` was produced by two team members running
disjoint shards of the sweep. Result directory names use neutral
`shard-a-*` / `shard-b-*` prefixes so the audit trail of which shard
produced which cells is preserved without putting individual names on
filesystem paths. The mapping is documented in `_provenance.json`.

## Upstream credit

ChatDBG was introduced by Levin, Zheng, Berger et al.:
- Paper: <https://arxiv.org/abs/2501.18504>
- Code: <https://github.com/plasma-umass/ChatDBG>

This work extends ChatDBG's procedure with structured tier ablations, a
larger and more cutoff-robust test corpus, and an LLM-as-judge scoring
pipeline. License (Apache-2.0) is inherited from the upstream project.

## Citation

See [`CITATION.cff`](CITATION.cff). Short form:

```
Amin, I., Garimella, S., Mehrotra, A.
"ChatDBGPro: GDB Is All You Need."
COS 484 (Princeton), 2026.
```

[upstream]: https://github.com/plasma-umass/ChatDBG
