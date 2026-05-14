# Reproducing the paper

This walks through what to install, what to run, and what to expect. There
are three reproduction depths; pick the one that matches what you want to
verify.

| Depth | What you get | Time | Cost |
|---|---|---|---|
| **Figures only** | Re-renders every paper figure from the shipped 640-cell scored panel | ~2 min | $0 |
| **Re-judge** | Runs `bench/judge.py` over the shipped model responses with GPT-4o, then re-renders | ~20 min + judge tokens | ~$2 (judge only) |
| **Full re-run** | Re-runs every model on every case from scratch, then judges, then renders | hours | tens of $$ (OpenRouter + judge) |

The shipped scored panel lives at
`bench/results/final_paper_bench/{synthetic,realworld}/`. Each cell is a
directory named
`<case>__tier{1,3}__<model>__<config>__ctx10__t1/` containing:

- `case.yaml` — pre-registered rubric + ground truth
- `result.json` — run metadata (status, elapsed, tier, model)
- `collect.json` — model's prose diagnosis (input to the judge)
- `score.json` — 0/1 axes (root_cause, local_fix, global_fix)
- `trajectory.json`, `chatdbg.log.yaml`, `session.cmds` — full transcript

---

## Prerequisites

- **Python 3.11+**
- **Docker** (only required for full re-run on BugsCPP / BugBench cases)
- **OpenRouter API key** for full re-run; **OpenAI API key** if you want
  to re-judge

```bash
git clone https://github.com/anikamehrotra/chatdbg-pro
cd chatdbg-pro
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
pip install -r bench/requirements.txt   # if a requirements file is present
cp .env.example .env
# Edit .env to fill in API keys for whichever depth you want
```

---

## Depth 1 — Re-render the paper figures (free)

Every figure in the paper is generated from the score.json files already
in `bench/results/final_paper_bench/`. From the repo root:

```bash
python -m bench.charts --panel bench/results/final_paper_bench --out paper/figures/
```

The eight paper figures will land in `paper/figures/`:

- `heatmap.png` — Figure 1
- `fig2_per_axis.png` — Figure 2
- `fig4_gdb_commands.png` — Figure 4
- `fig5_tool_calls.png` — Figure 5
- `fig6_tokens.png` — Figure 6
- `fig7_context.png` — Figure 7
- `fig8_cheatsheet.png` — Figure 8
- `fig9_cmw.png` — Figure 9

They should match the figures embedded in `paper/chatdbgpro_paper.pdf`.

---

## Depth 2 — Re-judge the shipped model responses (~$2)

The judge looks at each cell's `collect.json` (the model's final diagnosis,
**not** the debugger transcript) and applies the three-axis rubric. Set
`OPENAI_API_KEY` in `.env`, then:

```bash
python -m bench.judge bench/results/final_paper_bench --model openai/gpt-4o
```

This rewrites every `score.json` in place. Then re-render figures as in
Depth 1.

---

## Depth 3 — Re-run every model from scratch (hours + tens of $)

You almost certainly do not need this, but it is supported.

```bash
# Build the docker images that host the BugsCPP / BugBench targets.
# (Or pull pre-built images from ghcr.io/anikamehrotra/chatdbgpro-gdb-*.)
docker build -t chatdbg-pro .

# Sweep one cell to sanity-check the pipeline.
python -m bench.orchestrator \
  --case off-by-one-crc \
  --tier 1 \
  --model openrouter/openai/gpt-4o \
  --config bench/configs/tier1_bash_only.json

# Full panel — see bench/sbatch_paper_final.sh for the SLURM template, or
# bench/parallel_run.py for the local-parallel variant. Expect 1-3 hours
# wall time on a workstation, depending on rate limits.
```

After all runs land in `bench/results/<your-sweep-name>/`, copy the cells
into `bench/results/final_paper_bench/` using `bench/copy_to_final_bench.py`
and run Depth 2 to score.

---

## Provenance

`bench/results/final_paper_bench/_provenance.json` documents which
underlying sweep each cell was drawn from. Sweeps run by two different
human shards on the project team are recorded as `shard-a-paper-final-*`
and `shard-b-paper-final-*` so the audit trail of who-ran-what survives
without naming individuals in directory paths.

`_runset_locked.tsv` is the canonical work list (panel × case × tier ×
model) that the paper's tables are computed from.

---

## Troubleshooting

- **`gdb: ptrace: Operation not permitted` on Apple Silicon** — gdb's
  amd64 ptrace is broken under Rosetta. Use Linux/amd64 or Tier-1
  (bash-only) cells, which work everywhere.
- **OpenRouter rate limits during a full re-run** — `bench/orchestrator.py
  --resume` skips cells with an existing `result.json` whose status is
  `ok`; pair with `bench/watchdog.py` for unattended runs.
- **Judge disagrees with shipped score.json** — expected within ~5% on
  `gpt-4o`. The paper documents this in Section 4.3.
