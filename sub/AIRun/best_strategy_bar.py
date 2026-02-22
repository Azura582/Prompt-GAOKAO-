#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成柱状图：显示每个领域得分率最高的策略及其得分

用法：在仓库根目录运行此脚本，它会读取 `Results/deepseek` 下的策略结果，
并把图片保存到 `image/bar_chart_best_strategies_per_domain.png`。
"""

import json
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import sys


# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def calculate_best_per_domain(results_dir: str = "../Results/deepseek"):
    """
    遍历每个策略目录与其领域 JSON，计算每个策略在每个领域的得分率，
    并返回每个领域得分率最高的策略与得分。

    返回格式：{domain: (best_strategy_name, best_rate)}
    当没有数据时返回空字典。
    """
    results_path = Path(results_dir)
    if not results_path.exists():
        print(f"错误: 结果目录不存在: {results_path}")
        return {}

    # 临时存储： scores[strategy][domain] = (sum_teacher, sum_total)
    scores = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0]))

    strategy_dirs = sorted([d for d in results_path.iterdir() if d.is_dir()])
    if not strategy_dirs:
        print(f"警告: 在 {results_path} 下未找到策略目录")
        return {}

    for strategy_dir in strategy_dirs:
        strategy = strategy_dir.name
        for json_file in strategy_dir.glob("*.json"):
            domain = json_file.stem
            try:
                with json_file.open(encoding="utf-8") as f:
                    data = json.load(f)

                examples = data.get("example", [])
                for ex in examples:
                    teacher = ex.get("teacher_score", 0)
                    total = ex.get("score", 0)
                    if total and total > 0:
                        scores[strategy][domain][0] += float(teacher)
                        scores[strategy][domain][1] += float(total)
            except Exception as e:
                print(f"✗ 读取 {json_file} 失败: {e}")

    # 计算每个领域的最佳策略
    best_per_domain = {}
    # collect all domains encountered
    all_domains = set()
    for strategy, domains in scores.items():
        for d in domains.keys():
            all_domains.add(d)

    for domain in sorted(all_domains):
        best_strategy = None
        best_rate = -1.0
        for strategy, domains in scores.items():
            s, t = domains.get(domain, [0.0, 0.0])
            rate = 0.0
            if t > 0:
                rate = s / t
            # 只在存在有效比分时考虑
            if t > 0 and rate > best_rate:
                best_rate = rate
                best_strategy = strategy

        if best_strategy is None:
            # 没有任何策略有有效分数，设置为空/零
            best_per_domain[domain] = (None, 0.0)
        else:
            best_per_domain[domain] = (best_strategy, best_rate)

    return best_per_domain


def create_bar_chart(best_per_domain: dict, output_path: str = "../image/bar_chart_best_strategies_per_domain.png"):
    """根据 best_per_domain 绘制柱状图并保存。

    best_per_domain: {domain: (strategy, rate)}
    """
    if not best_per_domain:
        print("错误: 没有领域数据可绘图")
        return None

    domains = list(best_per_domain.keys())
    strategies = [best_per_domain[d][0] or "-" for d in domains]
    rates = [best_per_domain[d][1] for d in domains]

    # 转换为百分比
    rates_pct = [r * 100 for r in rates]

    # 确保输出目录存在
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 绘图：扩大画布以容纳长 x 轴标签
    fig, ax = plt.subplots(figsize=(14, 7))
    colors = plt.cm.tab20.colors
    bars = ax.bar(range(len(domains)), rates_pct,
                  color=[colors[i % len(colors)] for i in range(len(domains))],
                  edgecolor='k')

    # x 轴标签：倾斜并靠右以避免重叠
    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels(domains, rotation=40, ha='right', fontsize=10)
    ax.set_ylabel('score rate (%)')

    # 动态设置 y 上限：在最大值上再留出空间以避免标签被截断（允许超过 100% 显示到 110%）
    max_val = max(rates_pct) if rates_pct else 0
    upper = max(100, max_val + 8)
    upper = min(110, upper)
    ax.set_ylim(0, upper)
    ax.set_title('The highest-scoring strategy in each area and its score')

    # 在柱子上方/柱内智能标注策略名和百分比（当柱子接近顶部时放到柱内）
    for rect, strat, val in zip(bars, strategies, rates_pct):
        height = rect.get_height()
        label = f"{strat}\n{val:.2f}%"
        # 如果柱子高度接近上限（例如 >= 90% 上限），则把标签放在柱内，使用白色加粗字体
        if height >= upper * 0.90:
            ax.text(rect.get_x() + rect.get_width() / 2, height - upper * 0.03, label,
                    ha='center', va='top', fontsize=9, color='white', fontweight='bold', clip_on=False)
        else:
            ax.text(rect.get_x() + rect.get_width() / 2, height + upper * 0.02, label,
                    ha='center', va='bottom', fontsize=9, color='black', clip_on=False)

    # 美化：网格、紧凑布局并保存
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ 柱状图已保存: {out}")
    return str(out)


def main():
    results_dir = "../Results/deepseek"
    print("步骤1: 计算每个领域的最佳策略...")
    best = calculate_best_per_domain(results_dir)
    if not best:
        print("未找到任何有效数据，退出。")
        return

    print("步骤2: 生成并保存柱状图...")
    out = create_bar_chart(best, output_path="../image/bar_chart_best_strategies_per_domain.png")

    # 打印摘要
    if best:
        print("\n每个领域的最佳策略: ")
        for domain, (strategy, rate) in best.items():
            if strategy:
                print(f"  {domain}: {strategy} -> {rate:.2%}")
            else:
                print(f"  {domain}: 没有有效数据")

    if out:
        print(f"完成: 输出文件 {out}")


if __name__ == '__main__':
    main()
