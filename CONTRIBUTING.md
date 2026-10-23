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
- Pure SFT / preference tuning / online RL with no mid component (incl. FireAct/AgentTuning-scale agent SFT, env-RL warmups named “mid”)
- Generic LLM papers that only mention pretraining or post-training

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
  "category": "capability/agent",
  "tags": ["agent", "synthetic", "mid-training"],
  "note": "One-line contribution note."
}
```

3. Choose **one** primary `category` (see table below). Put cross-cutting facets in `tags`.
4. Add the id to `seen_arxiv_ids.txt` (also add reviewed-but-rejected ids there).
5. Regenerate the README:

```bash
python scripts/build_readme.py
```

6. Open a PR with the JSON diff + regenerated `README.md`.

## Categories (keys in `papers.json`)

| Key | Section |
|-----|---------|
| `surveys` | 0. Surveys & Position papers |
| `theory-analysis` | 1. Definition, Theory & Analysis |
| `capability/general` | 2.1 General Quality / Knowledge Annealing |
| `capability/math` | 2.2 Math & STEM |
| `capability/code` | 2.3 Code (incl. Repo-level / SWE) |
| `capability/reasoning` | 2.4 Reasoning & CoT (Mid for RL) |
| `capability/long-context` | 2.5 Long-Context |
| `capability/multilingual` | 2.6 Multilingual |
| `capability/instruction-alignment` | 2.7 Instruction & Alignment Mid-Training |
| `capability/agent` | 2.8 Agent & Tool Use |
| `capability/multimodal` | 2.9 Multimodal (LLM / VLM Mid-Training) |

Industrial tech reports, datasets/recipes, and methodological data/optimization papers should be filed under the **capability** they mainly advance, or under `theory-analysis` if they analyze mid-training dynamics/schedules/bridging without a clear capability target.

## Maintainer notes

- List is intended to update **weekly**.
- Prefer newest-first within each section (the build script sorts by year/month).
- When unsure of category, pick the best fit and explain in `note`.
