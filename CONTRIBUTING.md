# Contributing

Thanks for helping keep **Awesome Mid-Training for LLMs** up to date.

## What belongs here

**Include** papers that are about **LLM mid-training**: the stage between large-scale general pretraining and post-training (SFT / preference / online RL). Typical signals:

- Self-described mid-training / midtraining / annealing–cooldown data stages
- Continued / continual pretraining that functions as mid (math/code/agentic CPT, HQ annealing, long-context extension stages)
- Mid-training theory, datasets, open recipes, industrial reports with a substantive mid stage, or mid-specific evaluation protocols
- Objective is mainly NTP / CE (masking OK); token budget ≫ typical SFT and ≪ full pretraining

**Exclude** (add to `rejected.md` with a one-line reason instead):

- Non-LLM “mid-training” (CV, VLA/robotics, audio-only, tabular-only, etc.)
- Pure SFT / preference tuning / online RL with no mid component
- Generic LLM papers that only mention pretraining or post-training

**Boundary** works (FireAct-scale agent SFT, env-RL warmups named “mid”, etc.) go in category `9_boundary`, not main sections.

## How to add a paper

1. Verify the arXiv id via [export.arxiv.org/api](https://info.arxiv.org/help/api/index.html) (never invent titles or ids).
2. Append an object to `papers.json` (source of truth):

```json
{
  "title": "...",
  "authors": "Surname et al.",
  "year": 2026,
  "month": 10,
  "arxiv_id": "2610.xxxxx",
  "url": "https://arxiv.org/abs/2610.xxxxx",
  "code_url": null,
  "venue": "arXiv",
  "category": "2.8_agent",
  "tags": ["agent", "synthetic", "mid-training"],
  "note": "One-line contribution note."
}
```

3. Choose **one** primary `category` (see README taxonomy). Put capability / data / optimization facets in `tags`.
4. Add the id to `seen_arxiv_ids.txt` (also add reviewed-but-rejected ids there).
5. Regenerate the README:

```bash
python scripts/build_readme.py
```

6. Open a PR with the JSON diff + regenerated `README.md`.

## Categories (keys in `papers.json`)

| Key | Section |
|-----|---------|
| `0_surveys` | Surveys & Position papers |
| `1_theory` | Definition, Theory & Analysis |
| `2.1_general` … `2.9_multimodal` | By Target Capability |
| `3_data` | By Data |
| `4_optimization` | By Optimization |
| `5_bridge` | Bridge to Post-training |
| `6_industrial` | Industrial Technical Reports |
| `7_datasets` | Datasets & Open Recipes |
| `8_benchmarks` | Benchmarks / evaluation |
| `9_boundary` | Related / Boundary |

## Maintainer notes

- List is intended to update **weekly**.
- Prefer newest-first within each section (the build script sorts by year/month).
- When unsure of category, pick the best fit and explain in `note`.
