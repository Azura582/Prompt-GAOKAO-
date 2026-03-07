#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成提示词策略在不同领域的得分率热力图 (主观题)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from matplotlib import font_manager
import matplotlib
import warnings
import re

# 忽略字体警告
warnings.filterwarnings('ignore', category=UserWarning)

# 设置中文字体
def setup_chinese_font():
    # Linux系统常见中文字体列表(按优先级排序) - 优先使用宋体
    font_candidates = [
        'SimSun',                # 宋体 (优先)
        'Noto Serif CJK SC',     # 思源宋体简体
        'Noto Serif CJK TC',     # 思源宋体繁体
        'AR PL UMing CN',        # 文鼎明体(类似宋体)
        'Noto Sans CJK SC',      # 思源黑体简体
        'Noto Sans CJK TC',      # 思源黑体繁体
        'Noto Sans SC',
        'Noto Sans TC',
        'WenQuanYi Micro Hei',  # 文泉驿微米黑
        'WenQuanYi Zen Hei',    # 文泉驿正黑
        'AR PL UKai CN',        # 文鼎楷体
        'SimHei',                # Windows黑体
        'Microsoft YaHei',       # 微软雅黑
    ]
    
    # 获取系统可用字体
    available_fonts = set([f.name for f in font_manager.fontManager.ttflist])
    
    # 选择第一个可用的中文字体
    font_found = False
    for font in font_candidates:
        if font in available_fonts:
            # 同时设置中文字体和英文字体
            matplotlib.rcParams['font.sans-serif'] = [font, 'DejaVu Sans', 'Arial']
            matplotlib.rcParams['axes.unicode_minus'] = False
            print(f"使用字体: {font}")
            font_found = True
            break
    
    if not font_found:
        print("警告: 未找到合适的中文字体")
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False

setup_chinese_font()

# 定义领域和对应的中文名称
DOMAINS = {
    'Commonsense&WorldKnowledge': '常识知识',
    'Creative&Open-ended_Questions': '创造性问题',
    'Data&StatisticalLiteracy': '数据统计',
    'Lang_Comp&Produc': '阅读理解',
    'LogicalReasoning': '逻辑推理',
    'MathematicalReasoning': '数学推理',
    'Scientific_Inquiry': '科学探究',
    'Socialcultural_Understanding': '社会文化理解'
}

# 定义策略的中文名称
STRATEGY_NAMES = {
    'Strategy_0_CoT': 'CoT',
    'Strategy_1_SC': 'SC',
    'Strategy_2_ToT': 'ToT',
    'Strategy_3_GoT': 'GoT',
    'Strategy_4_Auto-CoT': 'Auto-CoT',
    'Strategy_5_GKP': 'GKP',
    'Strategy_6_ART': 'ART',
    'Strategy_7_ReAct': 'ReAct',
    'Strategy_8_APE': 'APE',
    'Strategy_9_RAG': 'RAG'
}


def read_scoring_rates_from_md(md_path='score rate.md'):
    """
    从Markdown文件读取所有领域的得分率数据
    
    Args:
        md_path: score rate.md 文件的路径
    
    Returns:
        DataFrame: 策略-领域得分率矩阵
    """
    md_path = Path(md_path)
    scoring_data = {}
    
    if not md_path.exists():
        print(f"错误: 文件不存在 {md_path}")
        return pd.DataFrame()
    
    # 读取文件内容
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析每个策略的数据
    # 匹配 Strategy_X_Name: 后面的内容
    strategy_pattern = r'(Strategy_\d+_[^:]+):\s*\n((?:  [^\n]+\n)+)'
    matches = re.findall(strategy_pattern, content)
    
    for strategy_name, scores_text in matches:
        # 解析每个领域的得分
        score_pattern = r'  ([^:]+):\s*([\d.]+)%'
        scores = re.findall(score_pattern, scores_text)
        
        strategy_cn = STRATEGY_NAMES.get(strategy_name, strategy_name)
        
        if strategy_cn not in scoring_data:
            scoring_data[strategy_cn] = {}
        
        for domain_en, score in scores:
            domain_cn = DOMAINS.get(domain_en, domain_en)
            scoring_data[strategy_cn][domain_cn] = float(score) / 100.0  # 转换为小数
    
    # 转换为DataFrame
    df_scoring = pd.DataFrame(scoring_data).T
    
    # 按照领域顺序排列列
    domain_order = [DOMAINS[d] for d in DOMAINS.keys()]
    df_scoring = df_scoring[domain_order]
    
    # 按照策略顺序排列行
    strategy_order = [STRATEGY_NAMES[s] for s in sorted(STRATEGY_NAMES.keys())]
    df_scoring = df_scoring.reindex(strategy_order)
    
    return df_scoring


def find_best_domain_for_strategy(df_scoring):
    """
    找出每个策略最适合的领域（得分最高的领域）
    
    Args:
        df_scoring: 策略-领域得分率矩阵
    
    Returns:
        dict: {策略: 最佳领域}
    """
    best_domains = {}
    for strategy in df_scoring.index:
        best_domain = df_scoring.loc[strategy].idxmax()
        best_score = df_scoring.loc[strategy].max()
        best_domains[strategy] = (best_domain, best_score)
    
    return best_domains


def plot_heatmap(df_scoring, best_domains, output_path='heatmap_strategy_domain_sub.png'):
    """
    绘制热力图
    
    Args:
        df_scoring: 策略-领域得分率矩阵
        best_domains: 每个策略的最佳领域
        output_path: 输出图片路径
    """
    # 转换为百分比并保留两位小数
    df_percentage = df_scoring * 100
    
    # 找出每个领域（列）的最高分
    max_per_domain = df_percentage.idxmax(axis=0)  # 每列的最大值所在行
    
    # 创建图形，调整大小以适应更大的字体
    fig, ax = plt.subplots(figsize=(18, 10))
    
    # 五号字 = 10.5pt
    cell_font_size = 15    # 单元格内数字字体
    tick_font_size = 15    # 刻度标签字体  
    label_font_size = 18     # 轴标签字体
    cbar_font_size = 15    # 色标字体
    
    # 使用更专业的配色方案 - RdYlGn (红-黄-绿配色，绿色表示高分)
    sns.heatmap(df_percentage, 
                annot=True,  # 显示数值
                fmt='.2f',   # 保留两位小数
                cmap='RdYlGn',  # 红-黄-绿配色，绿色表示高分
                cbar_kws={'label': '得分率 (%)'},
                linewidths=1.5,
                linecolor='white',
                ax=ax,
                vmin=68,  # 设置最小值以增强对比度
                vmax=100,  # 设置最大值
                annot_kws={'fontsize': cell_font_size, 'fontweight': 'heavy'})  # heavy = 900权重
    
    # 设置色标字体大小
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=cbar_font_size)
    cbar.ax.yaxis.label.set_size(cbar_font_size)
    cbar.ax.yaxis.label.set_weight('heavy')  # heavy = 900权重
    # 设置色标刻度数字加粗
    for label in cbar.ax.get_yticklabels():
        label.set_fontweight('heavy')
    
    # 标记每个领域的最高分方框
    for col_idx, domain in enumerate(df_percentage.columns):
        # 找到该领域最高分的策略
        best_strategy = max_per_domain[domain]
        row_idx = df_percentage.index.get_loc(best_strategy)
        
        # 在最高分的方框周围画粗边框
        ax.add_patch(plt.Rectangle((col_idx, row_idx), 1, 1, 
                                   fill=False, 
                                   edgecolor='blue', 
                                   linewidth=4,
                                   linestyle='-'))
    
    # 设置标题和标签
    ax.set_xlabel('问题领域', fontsize=label_font_size, fontweight='heavy')
    ax.set_ylabel('提示词策略', fontsize=label_font_size, fontweight='heavy')
    
    # 设置刻度标签字体大小和加粗
    ax.tick_params(axis='both', labelsize=tick_font_size)
    # 设置刻度标签加粗 - 使用最大粗细
    for label in ax.get_xticklabels():
        label.set_fontweight('heavy')  # heavy = 900权重
    for label in ax.get_yticklabels():
        label.set_fontweight('heavy')  # heavy = 900权重
    
    # 旋转x轴标签以便阅读
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # 添加图例说明
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='none', edgecolor='blue', 
                            linewidth=4, label='该领域最高分')]
    ax.legend(handles=legend_elements, loc='upper left', 
             bbox_to_anchor=(1.15, 1), fontsize=10.5, frameon=True, 
             prop={'weight': 'heavy'})  # heavy = 900权重
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"热力图已保存到: {output_path}")
    
    # 显示图形
    plt.show()
    
    # 打印最佳匹配结果
    print("\n" + "="*60)
    print("各策略最适合的领域（得分率最高）:")
    print("="*60)
    for strategy, (domain, score) in best_domains.items():
        print(f"{strategy:12s} -> {domain:12s} (得分率: {score*100:.2f}%)")
    print("="*60)
    
    # 打印每个领域的最佳策略
    print("\n" + "="*60)
    print("各领域表现最佳的策略:")
    print("="*60)
    for domain in df_percentage.columns:
        best_strategy = max_per_domain[domain]
        best_score = df_percentage.loc[best_strategy, domain]
        print(f"{domain:12s} -> {best_strategy:12s} (得分率: {best_score:.2f}%)")
    print("="*60)


def main():
    """主函数"""
    print("开始读取数据...")
    
    # 读取得分率数据
    df_scoring = read_scoring_rates_from_md('score rate.md')
    
    print("\n得分率数据矩阵:")
    print(df_scoring)
    
    # 找出每个策略的最佳领域
    best_domains = find_best_domain_for_strategy(df_scoring)
    
    # 绘制热力图
    plot_heatmap(df_scoring, best_domains)


if __name__ == '__main__':
    main()
