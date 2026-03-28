#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an English-only heatmap from score rate.md.

Requirements implemented:
- Y-axis: strategies
- X-axis: task domains
- Colormap: low -> high = green -> red
- Blue rectangle marks maximum value(s) in each column
- No chart title
"""

from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle


DOMAIN_ALIASES = {
    "Commonsense&WorldKnowledge": "Commonsense",
    "Creative&Open-ended": "Creative Questions",
    "Creative&Open-ended_Questions": "Creative Questions",
    "Data&StatisticalLiteracy": "Data Statistic",
    "Lang_Comp&Produc": "Language Comprehension",
    "LogicalReasoning": "Logical Reasoning",
    "MathematicalReasoning": "Mathematical Reasoning",
    "Scientific_Inquiry": "Scientific Inquiry",
    "Socialcultural_Understanding": "Sociocultural Understanding",
}

DOMAIN_ORDER = [
    "Commonsense",
    "Creative Questions",
    "Data Statistic",
    "Language Comprehension",
    "Logical Reasoning",
    "Mathematical Reasoning",
    "Scientific Inquiry",
    "Sociocultural Understanding",
]

STRATEGY_NAME_MAP = {
    "Strategy_0_CoT": "CoT",
    "Strategy_1_SC": "SC",
    "Strategy_2_ToT": "ToT",
    "Strategy_3_GoT": "GoT",
    "Strategy_4_Auto-CoT": "Auto-CoT",
    "Strategy_5_GKP": "GKP",
    "Strategy_6_ART": "ART",
    "Strategy_7_ReAct": "ReAct",
    "Strategy_8_APE": "APE",
    "Strategy_9_RAG": "RAG",
}

STRATEGY_ORDER = [
    "CoT",
    "SC",
    "ToT",
    "GoT",
    "Auto-CoT",
    "GKP",
    "ART",
    "ReAct",
    "APE",
    "RAG",
]


def parse_score_md(md_path: Path) -> pd.DataFrame:
    """Parse score markdown into strategy-domain matrix in [0, 1]."""
    if not md_path.exists():
        raise FileNotFoundError(f"Input markdown file not found: {md_path}")

    content = md_path.read_text(encoding="utf-8")
    strategy_pattern = r"(Strategy_\d+_[^:]+):\s*\n((?:\s{2}[^\n]+\n)+)"
    score_pattern = r"\s{2}([^:]+):\s*([\d.]+)%"

    matrix: dict[str, dict[str, float]] = {}

    for strategy_key, block in re.findall(strategy_pattern, content):
        strategy_name = STRATEGY_NAME_MAP.get(strategy_key, strategy_key)
        matrix.setdefault(strategy_name, {})

        for raw_domain, score_str in re.findall(score_pattern, block):
            domain_name = DOMAIN_ALIASES.get(raw_domain.strip())
            if domain_name is None:
                # Ignore unknown domain keys to keep the plot stable.
                continue
            matrix[strategy_name][domain_name] = float(score_str) / 100.0

    df = pd.DataFrame(matrix).T

    # Ensure stable order and avoid KeyError even when some domains are missing.
    df = df.reindex(columns=DOMAIN_ORDER)
    df = df.reindex(STRATEGY_ORDER)

    # If any domain was not parsed, fail fast with a clear message.
    missing_domains = [d for d in DOMAIN_ORDER if d not in pd.DataFrame(matrix).T.columns]
    if missing_domains:
        raise ValueError(
            "Missing domain columns after parsing markdown: "
            + ", ".join(missing_domains)
            + ". Please check DOMAIN_ALIASES and score rate.md keys."
        )

    return df


def plot_heatmap(df: pd.DataFrame, output_path: Path) -> None:
    """Draw heatmap with blue boxes on per-column maxima, no title."""
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    df_pct = (df * 100).T

    fig, ax = plt.subplots(figsize=(18, 10))

    # low -> high = green -> red
    sns.heatmap(
        df_pct,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn_r",
        cbar_kws={"label": "Accuracy (%)"},
        linewidths=1.0,
        linecolor="white",
        ax=ax,
        annot_kws={"fontsize": 11, "fontweight": "bold"},
    )

    # Draw blue boxes around max value(s) in each row.
    for row_idx, row_name in enumerate(df_pct.index):
        row_max = df_pct.loc[row_name].max()
        max_cols = df_pct.columns[df_pct.loc[row_name] == row_max]
        for col_name in max_cols:
            col_idx = df_pct.columns.get_loc(col_name)
            ax.add_patch(
                Rectangle(
                    (col_idx, row_idx),
                    1,
                    1,
                    fill=False,
                    edgecolor="blue",
                    linewidth=3,
                )
            )

    # No title on purpose.
    ax.set_xlabel("Prompting Strategy", fontsize=13, fontweight="bold")
    ax.set_ylabel("Task Domain", fontsize=13, fontweight="bold")
    ax.tick_params(axis="both", labelsize=11)
    plt.xticks(rotation=0, ha="center")
    plt.yticks(rotation=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_md = base_dir / "score rate.md"
    output_img = base_dir / "heatmap_strategy_domain_sub_en.png"

    print(f"Reading: {input_md}")
    df_scoring = parse_score_md(input_md)

    print("\nScore matrix (fraction):")
    print(df_scoring)

    plot_heatmap(df_scoring, output_img)
    print(f"\nSaved heatmap to: {output_img}")


if __name__ == "__main__":
    main()
