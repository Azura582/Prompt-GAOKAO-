#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an English-only objective heatmap from domain CSV files.

Design (aligned with the subjective script style):
- Input: `Results/obj/<domain>/scoring_rates.csv`
- 7 objective domains only
- Plot matrix transposed: X-axis = Prompting Strategy, Y-axis = Task Domain
- Colormap: low -> high = green -> red
- Blue rectangles mark row-wise maxima (after transpose)
- No chart title
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Rectangle


DOMAIN_FOLDERS = {
    "Commonsense_and_WorldKnowledge": "Commonsense",
    "Data_and_StatisticalLiteracy": "Data Statistic",
    "Lang_Comp_and_Produc": "Language Comprehension",
    "Logical_Reasoning": "Logical Reasoning",
    "Mathematical_Reasoning": "Mathematical Reasoning",
    "Natural_Science": "Natural Science",
    "Sociocultural_Understanding": "Sociocultural Understanding",
}

DOMAIN_ORDER = [
    "Commonsense",
    "Data Statistic",
    "Language Comprehension",
    "Logical Reasoning",
    "Mathematical Reasoning",
    "Natural Science",
    "Sociocultural Understanding",
]

STRATEGY_NAME_MAP = {
    "0_CoT": "CoT",
    "1_SC": "SC",
    "2_ToT": "ToT",
    "3_GoT": "GoT",
    "4_Auto-CoT": "Auto-CoT",
    "5_KGR": "KGR",
    "6_ART": "ART",
    "7_ReAct": "ReAct",
    "8_APE": "APE",
    "9_RAG": "RAG",
}

STRATEGY_ORDER = [
    "CoT",
    "SC",
    "ToT",
    "GoT",
    "Auto-CoT",
    "KGR",
    "ART",
    "ReAct",
    "APE",
    "RAG",
]


def read_scoring_matrix(base_dir: Path) -> pd.DataFrame:
    """Read all objective CSV files and build strategy-domain matrix in [0,1]."""
    matrix: dict[str, dict[str, float]] = {}

    for domain_folder, domain_display in DOMAIN_FOLDERS.items():
        csv_path = base_dir / domain_folder / "scoring_rates.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing CSV: {csv_path}")

        df = pd.read_csv(csv_path)
        required_cols = {"strategy", "scoring_rate"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV missing required columns {required_cols}: {csv_path}")

        for _, row in df.iterrows():
            strategy_raw = str(row["strategy"]).strip()
            strategy_name = STRATEGY_NAME_MAP.get(strategy_raw, strategy_raw)
            score = float(row["scoring_rate"])

            matrix.setdefault(strategy_name, {})
            matrix[strategy_name][domain_display] = score

    result = pd.DataFrame(matrix).T
    result = result.reindex(index=STRATEGY_ORDER)
    result = result.reindex(columns=DOMAIN_ORDER)

    missing_domains = [d for d in DOMAIN_ORDER if d not in pd.DataFrame(matrix).T.columns]
    if missing_domains:
        raise ValueError(
            "Missing domain columns after loading CSV files: "
            + ", ".join(missing_domains)
            + "."
        )

    if result.isna().any().any():
        missing_cells = int(result.isna().sum().sum())
        raise ValueError(f"Matrix contains {missing_cells} missing values; please verify all strategies exist in all CSVs.")

    return result


def plot_heatmap(df: pd.DataFrame, output_path: Path) -> None:
    """Plot transposed heatmap and mark row maxima with blue rectangles."""
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    df_pct = (df * 100).T

    fig, ax = plt.subplots(figsize=(18, 10))

    sns.heatmap(
        df_pct,
        annot=True,
        fmt=".2f",
        cmap="RdYlGn_r",  # low green -> high red
        cbar_kws={"label": "Accuracy (%)"},
        linewidths=1.0,
        linecolor="white",
        ax=ax,
        annot_kws={"fontsize": 11, "fontweight": "bold"},
    )

    # Row-wise maxima highlighting (on transposed view)
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
    output_img = base_dir / "heatmap_strategy_domain_obj_en.png"

    print(f"Reading CSV files from: {base_dir}")
    df_scoring = read_scoring_matrix(base_dir)

    print("\nScore matrix (fraction):")
    print(df_scoring)

    plot_heatmap(df_scoring, output_img)
    print(f"\nSaved heatmap to: {output_img}")


if __name__ == "__main__":
    main()
