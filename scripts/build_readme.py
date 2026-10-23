#!/usr/bin/env python3
"""Regenerate README.md from papers.json (source of truth)."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS_PATH = ROOT / "papers.json"
README_PATH = ROOT / "README.md"

# Display order and headings
SECTIONS: list[tuple[str, str]] = [
    ("0_surveys", "0. Surveys & Position Papers"),
    ("1_theory", "1. Definition, Theory & Analysis"),
    ("2.1_general", "2.1 General Quality / Knowledge Annealing"),
    ("2.2_math", "2.2 Math & STEM"),
    ("2.3_code", "2.3 Code (incl. Repo-level / SWE)"),
    ("2.4_reasoning", "2.4 Reasoning & CoT (Mid for RL)"),
    ("2.5_longctx", "2.5 Long-Context"),
    ("2.6_multilingual", "2.6 Multilingual"),
    ("2.7_alignment", "2.7 Instruction & Alignment Mid-Training"),
    ("2.8_agent", "2.8 Agent & Tool Use"),
    ("2.9_multimodal", "2.9 Multimodal (LLM / VLM Mid-Training)"),
    ("3_data", "3. By Data"),
    ("4_optimization", "4. By Optimization"),
    ("5_bridge", "5. Bridge to Post-Training"),
    ("6_industrial", "6. Industrial Technical Reports"),
    ("7_datasets", "7. Datasets & Open Recipes"),
    ("8_benchmarks", "8. Benchmarks / Evaluation"),
    ("9_boundary", "9. Related / Boundary"),
]

SECTION_BLURBS: dict[str, str] = {
    "0_surveys": "Surveys and position papers that define or map LLM mid-training.",
    "1_theory": "Why mid-training works: distribution bridging, plasticity, data timing, decay/annealing scaling.",
    "2.1_general": "HQ annealing, general quality uplift, and broad capability injection.",
    "2.2_math": "Math / STEM continued pretraining and mid-stage reasoning corpora.",
    "2.3_code": "Code and SWE mid-training, including repo-level and agent-native coding priors.",
    "2.4_reasoning": "Mid-training that shapes CoT / reasoning and downstream RL plasticity.",
    "2.5_longctx": "Context-extension stages and long-context continual pretraining.",
    "2.6_multilingual": "Language adaptation and multilingual continual / mid pretraining.",
    "2.7_alignment": "Instruction, safety, and alignment-oriented mid-training (still NTP-scale).",
    "2.8_agent": "Agentic CPT / tool-use / deep-research / SWE-agent mid-training.",
    "2.9_multimodal": "Only LLM/VLM mid-training (not pure CV / VLA robotics).",
    "3_data": "Natural HQ corpora, domain data, synthetic construction, mixtures, and replay.",
    "4_optimization": "LR schedules (WSD, annealing, rewarming), curricula, context engineering, compute.",
    "5_bridge": "Evaluation protocols, mid vs SFT/RL interplay, forgetting and plasticity.",
    "6_industrial": "Additional industrial reports with a substantive mid / annealing stage (many capability-tagged reports live in §2).",
    "7_datasets": "Standalone datasets and open mid-training recipes / corpora.",
    "8_benchmarks": "Benchmarks and evaluation protocols specifically informative for mid-training.",
    "9_boundary": "Related or boundary works (early agent SFT, env-RL warmups, precursors). Not counted as core mid-training.",
}

# Industrial table: model / report / mid stage name / tokens (best-effort from notes; null if unknown)
INDUSTRIAL_TABLE: list[dict] = [
    {
        "model": "MiniCPM",
        "arxiv_id": "2404.06395",
        "mid_stage": "WSD decay / annealing",
        "tokens": "not primary focus",
    },
    {
        "model": "Llama 3",
        "arxiv_id": "2407.21783",
        "mid_stage": "Annealing + long-context stage",
        "tokens": "annealing upsamples HQ data",
    },
    {
        "model": "DeepSeek-V3",
        "arxiv_id": "2412.19437",
        "mid_stage": "Context extension (32K→128K)",
        "tokens": "separate stage after main PT",
    },
    {
        "model": "Qwen2.5",
        "arxiv_id": "2412.15115",
        "mid_stage": "HQ continued training / long-context",
        "tokens": "series-dependent",
    },
    {
        "model": "OLMo 2",
        "arxiv_id": "2501.00656",
        "mid_stage": "Dolmino mid-training / annealing",
        "tokens": "public Dolmino mix",
    },
    {
        "model": "Qwen3",
        "arxiv_id": "2505.09388",
        "mid_stage": "Reasoning stage (functional mid)",
        "tokens": "~5T HQ after ~30T PT",
    },
    {
        "model": "Kimi K2",
        "arxiv_id": "2507.20534",
        "mid_stage": "Annealing + YaRN (agent mainly post)",
        "tokens": "after 15.5T PT",
    },
    {
        "model": "GLM-4.5",
        "arxiv_id": "2508.06471",
        "mid_stage": "Explicit Mid-Training",
        "tokens": "repo + reasoning + agent traj.; to 128K",
    },
    {
        "model": "AgentFounder",
        "arxiv_id": "2509.13310",
        "mid_stage": "Agentic Continual Pre-training",
        "tokens": "~200B + ~100B (32K→128K)",
    },
    {
        "model": "Kimi-Dev",
        "arxiv_id": "2509.23045",
        "mid_stage": "SWE mid-training",
        "tokens": "~150B",
    },
    {
        "model": "Tongyi DeepResearch",
        "arxiv_id": "2510.24701",
        "mid_stage": "Agentic mid-training / CPT",
        "tokens": "see report / AgentFounder line",
    },
    {
        "model": "daVinci-Dev",
        "arxiv_id": "2601.18418",
        "mid_stage": "Agent-native mid-training",
        "tokens": "73.1B (ctx+env)",
    },
    {
        "model": "MidTool",
        "arxiv_id": "2608.20314",
        "mid_stage": "Tool-use mid-training",
        "tokens": "MidTool-Mix ~20.3B",
    },
    {
        "model": "NVIDIA Nemotron mid recipe",
        "arxiv_id": "2610.22019",
        "mid_stage": "Open midtraining recipe",
        "tokens": "up to ~500B; 256K ctx",
    },
]


def load_papers() -> list[dict]:
    papers = json.loads(PAPERS_PATH.read_text(encoding="utf-8"))
    for p in papers:
        p.setdefault("code_url", None)
        p.setdefault("tags", [])
        p.setdefault("note", "")
        p.setdefault("venue", "arXiv")
    return papers


def sort_key(p: dict) -> tuple:
    return (-int(p["year"]), -int(p["month"]), p["title"].lower())


def format_entry(p: dict) -> str:
    links = [f"[[paper]({p['url']})]"]
    if p.get("code_url"):
        links.append(f"[[code]({p['code_url']})]")
    link_str = " ".join(links)
    venue = p.get("venue") or "arXiv"
    ym = f"{p['year']}.{int(p['month']):02d}"
    # Avoid "ACL 2020 2020.04" when venue already embeds the year
    if str(p["year"]) in venue:
        venue_str = venue
    else:
        venue_str = f"{venue} {ym}"
    tags = " ".join(f"`#{t}`" for t in p.get("tags") or [])
    note = (p.get("note") or "").strip()
    line = f"- **{p['title']}** {link_str} — *{venue_str}* — {note}"
    if tags:
        line += f" {tags}"
    return line


def anchor(title: str) -> str:
    a = title.lower()
    for ch in ".,/()&":
        a = a.replace(ch, "")
    a = a.replace(" ", "-")
    while "--" in a:
        a = a.replace("--", "-")
    return a


def build_readme(papers: list[dict], updated: str) -> str:
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for p in papers:
        by_cat[p["category"]].append(p)
    for cat in by_cat:
        by_cat[cat].sort(key=sort_key)

    n_core = sum(1 for p in papers if p["category"] != "9_boundary")
    n_boundary = len(by_cat.get("9_boundary", []))
    n_total = len(papers)

    lines: list[str] = []
    lines.append("# Awesome Mid-Training for LLMs")
    lines.append("")
    lines.append(
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)"
        " ![Papers](https://img.shields.io/badge/papers-{n}-blue)"
        " ![License: CC0-1.0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)"
        " ![Last Updated](https://img.shields.io/badge/Updated-{d}-green)".format(
            n=n_total, d=updated.replace("-", "--")
        )
    )
    lines.append("")
    lines.append(
        "**A curated list of papers on mid-training for large language models** — "
        "the stage between large-scale general pretraining and post-training "
        "(SFT / preference optimization / online RL)."
    )
    lines.append("")
    lines.append("## Operational definition")
    lines.append("")
    lines.append(
        "> **Mid-training** = stage between large-scale general pretraining and post-training "
        "(SFT / preference / online RL); mainly an NTP/CE objective (masking allowed); "
        "HQ / domain / synthetic data, usually with replay; token budget much larger than "
        "typical SFT and smaller than full pretraining; intent = distribution bridging / "
        "capability injection / post-training warmup, **not** final alignment."
    )
    lines.append("")
    lines.append(
        "Includes self-described mid-training, annealing/cooldown-stage data studies, "
        "continued pretraining that functions as mid (incl. agentic CPT, math/code CPT), "
        "long-context extension stages, theory/analysis, datasets & recipes, industrial "
        "reports with a substantive mid section, and mid-oriented evaluation protocols. "
        "Boundary cases (env-RL warmups, FireAct/AgentTuning-scale SFT) live in "
        "[§9 Related / Boundary](#9-related--boundary)."
    )
    lines.append("")
    lines.append(f"**Last updated:** {updated} (Asia/Shanghai) · updated weekly")
    lines.append("")
    lines.append(
        f"**Stats:** {n_total} entries ({n_core} core + {n_boundary} boundary). "
        "Machine-readable source: [`papers.json`](papers.json). "
        "Regenerate this file: `python scripts/build_readme.py`."
    )
    lines.append("")
    lines.append("## Citation (forthcoming survey)")
    lines.append("")
    lines.append(
        "This list accompanies a general LLM mid-training survey by Tingfeng Hui "
        "([HypherX](https://github.com/HypherX)). BibTeX TBD — placeholder:"
    )
    lines.append("")
    lines.append("```bibtex")
    lines.append("@article{hui2026midtraining-survey,")
    lines.append("  title   = {A Survey on Mid-Training of Large Language Models},")
    lines.append("  author  = {Hui, Tingfeng and others},")
    lines.append("  journal = {TBD},")
    lines.append("  year    = {2026},")
    lines.append("  note    = {Forthcoming}")
    lines.append("}")
    lines.append("```")
    lines.append("")
    lines.append("## Taxonomy")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TB")
    lines.append("  MT[LLM Mid-Training]")
    lines.append("  MT --> S0[0 Surveys]")
    lines.append("  MT --> S1[1 Theory and Analysis]")
    lines.append("  MT --> S2[2 By Capability]")
    lines.append("  MT --> S3[3 By Data]")
    lines.append("  MT --> S4[4 By Optimization]")
    lines.append("  MT --> S5[5 Bridge to Post-training]")
    lines.append("  MT --> S6[6 Industrial Reports]")
    lines.append("  MT --> S7[7 Datasets and Recipes]")
    lines.append("  MT --> S8[8 Benchmarks]")
    lines.append("  MT --> S9[9 Related / Boundary]")
    lines.append("  S2 --> C1[General / Annealing]")
    lines.append("  S2 --> C2[Math and STEM]")
    lines.append("  S2 --> C3[Code / SWE]")
    lines.append("  S2 --> C4[Reasoning / CoT]")
    lines.append("  S2 --> C5[Long-context]")
    lines.append("  S2 --> C6[Multilingual]")
    lines.append("  S2 --> C7[Instruction / Alignment]")
    lines.append("  S2 --> C8[Agent and Tools]")
    lines.append("  S2 --> C9[Multimodal VLM]")
    lines.append("```")
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    lines.append("- [Operational definition](#operational-definition)")
    lines.append("- [Taxonomy](#taxonomy)")
    lines.append("- [2. By Target Capability](#2-by-target-capability)")
    for key, title in SECTIONS:
        n = len(by_cat.get(key, []))
        lines.append(f"- [{title} ({n})](#{anchor(title)})")
    lines.append("- [Industrial mid-stage cheat sheet](#industrial-mid-stage-cheat-sheet)")
    lines.append("- [Contributing](#contributing)")
    lines.append("")

    for key, title in SECTIONS:
        if key == "2.1_general":
            lines.append("## 2. By Target Capability")
            lines.append("")
            lines.append(
                "Each paper has **one** primary section; tags capture cross-cutting "
                "capability / data / optimization facets."
            )
            lines.append("")
        heading = f"### {title}" if key.startswith("2.") else f"## {title}"
        lines.append(heading)
        lines.append("")
        blurb = SECTION_BLURBS.get(key)
        if blurb:
            lines.append(f"*{blurb}*")
            lines.append("")
        entries = by_cat.get(key, [])
        if not entries:
            lines.append("_None yet — contributions welcome._")
            lines.append("")
            continue
        for p in entries:
            lines.append(format_entry(p))
        lines.append("")

        # After industrial section, insert cheat-sheet table once we reach 6
        if key == "6_industrial":
            lines.append("### Industrial mid-stage cheat sheet")
            lines.append("")
            lines.append(
                "Best-effort summary of named mid / annealing stages in major reports "
                "(token counts as stated by authors; verify in the paper)."
            )
            lines.append("")
            lines.append("| Model | Report | Mid-stage name | Tokens (if stated) |")
            lines.append("|-------|--------|----------------|--------------------|")
            id_to_url = {p["arxiv_id"]: p["url"] for p in papers}
            for row in INDUSTRIAL_TABLE:
                url = id_to_url.get(row["arxiv_id"], f"https://arxiv.org/abs/{row['arxiv_id']}")
                lines.append(
                    f"| {row['model']} | [{row['arxiv_id']}]({url}) | {row['mid_stage']} | {row['tokens']} |"
                )
            lines.append("")

    lines.append("## Contributing")
    lines.append("")
    lines.append(
        "See [`CONTRIBUTING.md`](CONTRIBUTING.md). Edit `papers.json`, then run "
        "`python scripts/build_readme.py`. Reviewed-but-rejected ids go in "
        "`seen_arxiv_ids.txt` and `rejected.md`."
    )
    lines.append("")
    lines.append("## License")
    lines.append("")
    lines.append(
        "[CC0-1.0](LICENSE) — paper titles and metadata remain under their original copyrights."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    papers = load_papers()
    # Prefer fixed survey date from task if today unavailable; use papers note date
    updated = "2026-10-23"
    try:
        updated = date.today().isoformat()
    except Exception:
        pass
    # Force the date requested in the brief when building for the release
    updated = "2026-10-23"
    text = build_readme(papers, updated)
    README_PATH.write_text(text, encoding="utf-8")
    print(f"Wrote {README_PATH} ({len(papers)} papers)")


if __name__ == "__main__":
    main()
