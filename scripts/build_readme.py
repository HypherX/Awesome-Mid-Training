#!/usr/bin/env python3
"""Regenerate README.md from papers.json (source of truth).

Taxonomy (capability-only):
  surveys | theory-analysis | capability/<slug> for 2.1–2.9
"""

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
    ("surveys", "0. Surveys & Position Papers"),
    ("theory-analysis", "1. Definition, Theory & Analysis"),
    ("capability/general", "2.1 General Quality / Knowledge Annealing"),
    ("capability/math", "2.2 Math & STEM"),
    ("capability/code", "2.3 Code (incl. Repo-level / SWE)"),
    ("capability/reasoning", "2.4 Reasoning & CoT (Mid for RL)"),
    ("capability/long-context", "2.5 Long-Context"),
    ("capability/multilingual", "2.6 Multilingual"),
    ("capability/instruction-alignment", "2.7 Instruction & Alignment Mid-Training"),
    ("capability/agent", "2.8 Agent & Tool Use"),
    ("capability/multimodal", "2.9 Multimodal (LLM / VLM Mid-Training)"),
]

SECTION_BLURBS: dict[str, str] = {
    "surveys": "Surveys and position papers that define or map LLM mid-training.",
    "theory-analysis": (
        "Why mid-training works: definition, distribution bridging, plasticity, "
        "data/LR schedules, mixtures, mid↔post bridging, and cross-cutting analysis."
    ),
    "capability/general": "HQ annealing, general quality uplift, and broad capability injection.",
    "capability/math": "Math / STEM continued pretraining and mid-stage reasoning corpora.",
    "capability/code": "Code and SWE mid-training, including repo-level and agent-native coding priors.",
    "capability/reasoning": "Mid-training that shapes CoT / reasoning and downstream RL plasticity.",
    "capability/long-context": "Context-extension stages and long-context continual pretraining.",
    "capability/multilingual": "Language adaptation and multilingual continual / mid pretraining.",
    "capability/instruction-alignment": (
        "Instruction, safety, and alignment-oriented mid-training (still NTP-scale)."
    ),
    "capability/agent": "Agentic CPT / tool-use / deep-research / SWE-agent mid-training.",
    "capability/multimodal": "Only LLM/VLM mid-training (not pure CV / VLA robotics).",
}

ALLOWED_CATEGORIES = {key for key, _ in SECTIONS}


def load_papers() -> list[dict]:
    papers = json.loads(PAPERS_PATH.read_text(encoding="utf-8"))
    for p in papers:
        p.setdefault("code_url", None)
        p.setdefault("tags", [])
        p.setdefault("note", "")
        p.setdefault("venue", "arXiv")
        cat = p.get("category")
        if cat not in ALLOWED_CATEGORIES:
            raise SystemExit(
                f"Invalid category {cat!r} for {p.get('arxiv_id')} "
                f"(allowed: {sorted(ALLOWED_CATEGORIES)})"
            )
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
        "long-context extension stages, theory/analysis, datasets & recipes, and industrial "
        "reports with a substantive mid section. Classification is by **target capability** "
        "(plus surveys and theory/analysis). Works that do not meet the mid-training "
        "definition (env-RL warmups, FireAct/AgentTuning-scale SFT, etc.) are listed in "
        "[`rejected.md`](rejected.md)."
    )
    lines.append("")
    lines.append(f"**Last updated:** {updated} (Asia/Shanghai) · updated weekly")
    lines.append("")
    lines.append(
        f"**Stats:** {n_total} papers. "
        "Machine-readable source: [`papers.json`](papers.json). "
        "Regenerate this file: `python scripts/build_readme.py`."
    )
    lines.append("")
    lines.append("## Contents")
    lines.append("")
    lines.append("- [Operational definition](#operational-definition)")
    n0 = len(by_cat.get("surveys", []))
    n1 = len(by_cat.get("theory-analysis", []))
    lines.append(f"- [0. Surveys & Position Papers ({n0})](#0-surveys-position-papers)")
    lines.append(f"- [1. Definition, Theory & Analysis ({n1})](#1-definition-theory-analysis)")
    lines.append("- [2. By Target Capability](#2-by-target-capability)")
    for key, title in SECTIONS:
        if not key.startswith("capability/"):
            continue
        n = len(by_cat.get(key, []))
        lines.append(f"  - [{title} ({n})](#{anchor(title)})")
    lines.append("- [Contributing](#contributing)")
    lines.append("")

    for key, title in SECTIONS:
        if key == "capability/general":
            lines.append("## 2. By Target Capability")
            lines.append("")
            lines.append(
                "Each paper has **one** primary capability section; tags capture "
                "cross-cutting data / optimization facets. Industrial tech reports and "
                "datasets/recipes are filed under the capability they mainly advance."
            )
            lines.append("")

        if key.startswith("capability/"):
            heading = f"### {title}"
        else:
            heading = f"## {title}"
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
    updated = "2026-10-23"
    try:
        updated = date.today().isoformat()
    except Exception:
        pass
    updated = "2026-10-23"
    text = build_readme(papers, updated)
    README_PATH.write_text(text, encoding="utf-8")
    print(f"Wrote {README_PATH} ({len(papers)} papers)")
    from collections import Counter

    c = Counter(p["category"] for p in papers)
    for k, _ in SECTIONS:
        print(f"  {k}: {c.get(k, 0)}")


if __name__ == "__main__":
    main()
