#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略-领域得分率分析与雷达图可视化
功能：分析Results/deepseek下10个策略文件夹中8个领域的平均得分率，生成两张雷达图
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D
from pathlib import Path as PathLib
from collections import defaultdict

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def radar_factory(num_vars, frame='circle'):
    """
    创建雷达图的工厂函数
    
    :param num_vars: 雷达图的变量（顶点）数量
    :param frame: 雷达图外框形状 ('circle', 'polygon')
    """
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = 'radar'
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def calculate_domain_scores(results_dir="../Results/deepseek"):
    """
    计算每个策略在每个领域的平均得分率
    
    :param results_dir: 结果文件夹路径
    :return: 字典 {strategy_name: {domain_name: score_rate}}
    """
    results_path = PathLib(results_dir)
    
    # 存储结构：{strategy: {domain: [teacher_scores], [total_scores]}}
    data = defaultdict(lambda: defaultdict(lambda: {'teacher': [], 'total': []}))
    
    print("=" * 70)
    print("开始分析策略-领域得分率")
    print("=" * 70)
    
    # 遍历策略文件夹
    strategy_dirs = sorted([d for d in results_path.iterdir() if d.is_dir()])
    
    for strategy_dir in strategy_dirs:
        strategy_name = strategy_dir.name
        print(f"\n处理策略: {strategy_name}")
        
        # 遍历该策略下的所有JSON文件（领域文件）
        json_files = list(strategy_dir.glob("*.json"))
        
        for json_file in json_files:
            domain_name = json_file.stem  # 文件名（不含扩展名）作为领域名
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_json = json.load(f)
                
                examples = data_json.get('example', [])
                
                # 统计该文件中所有题目的得分
                for example in examples:
                    teacher_score = example.get('teacher_score', 0)
                    total_score = example.get('score', 0)
                    
                    # 只统计有效分数（非零）
                    if total_score > 0:
                        data[strategy_name][domain_name]['teacher'].append(teacher_score)
                        data[strategy_name][domain_name]['total'].append(total_score)
                
                print(f"  - {domain_name}: {len(examples)} 道题")
                
            except Exception as e:
                print(f"  ✗ 读取文件失败: {json_file.name}, 错误: {e}")
    
    # 计算平均得分率
    score_rates = {}
    
    for strategy_name, domains in data.items():
        score_rates[strategy_name] = {}
        
        for domain_name, scores in domains.items():
            teacher_scores = scores['teacher']
            total_scores = scores['total']
            
            if teacher_scores and total_scores:
                # 计算平均得分率 = sum(teacher_score) / sum(score)
                avg_rate = sum(teacher_scores) / sum(total_scores)
                score_rates[strategy_name][domain_name] = avg_rate
            else:
                score_rates[strategy_name][domain_name] = 0.0
    
    return score_rates


def create_radar_charts(score_rates, output_dir):
    """
    创建两张雷达图：前5个策略和后5个策略
    
    :param score_rates: 得分率数据 {strategy: {domain: rate}}
    :param output_dir: 输出目录
    """
    # 获取所有策略名（排序）
    strategies = sorted(score_rates.keys())
    
    # 获取所有领域名（从第一个策略中提取）
    if not strategies:
        print("错误: 没有找到任何策略数据")
        return
    
    domains = sorted(score_rates[strategies[0]].keys())
    num_domains = len(domains)
    
    print("\n" + "=" * 70)
    print(f"生成雷达图")
    print(f"策略数量: {len(strategies)}")
    print(f"领域数量: {num_domains}")
    print(f"领域: {', '.join(domains)}")
    print("=" * 70)
    
    # 创建雷达图框架
    theta = radar_factory(num_domains, frame='polygon')
    
    # 定义颜色
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # 分成两组
    group1 = strategies[:5]
    group2 = strategies[5:10] if len(strategies) > 5 else []
    
    # 创建第一张雷达图(前5个策略)
    if group1:
        fig1 = plt.figure(figsize=(10, 10))
        ax1 = fig1.add_subplot(111, projection='radar')
        ax1.set_ylim(0.6, 1)
        
        for idx, strategy in enumerate(group1):
            # 获取该策略在各领域的得分率
            values = [score_rates[strategy].get(domain, 0) for domain in domains]
            
            # 绘制折线
            ax1.plot(theta, values, 'o-', linewidth=2, label=strategy, 
                     color=colors[idx], markersize=6)
            ax1.fill(theta, values, alpha=0.15, color=colors[idx])
        
        ax1.set_varlabels(domains)
        ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax1.set_title('strategy 1-5 score rate in 8 field', pad=20, fontsize=14, fontweight='bold')
        ax1.grid(True)
        
        output_path1 = "../image/radar_chart_strategies_1-5.png"
        plt.savefig(output_path1, dpi=300, bbox_inches='tight')
        print(f"✓ 雷达图1已保存: {output_path1}")
        plt.close()
    
    # 创建第二张雷达图(后5个策略)
    if group2:
        fig2 = plt.figure(figsize=(10, 10))
        ax2 = fig2.add_subplot(111, projection='radar')
        ax2.set_ylim(0.6, 1)
        
        for idx, strategy in enumerate(group2):
            values = [score_rates[strategy].get(domain, 0) for domain in domains]
            
            ax2.plot(theta, values, 'o-', linewidth=2, label=strategy, 
                     color=colors[idx + 5], markersize=6)
            ax2.fill(theta, values, alpha=0.15, color=colors[idx + 5])
        
        ax2.set_varlabels(domains)
        ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax2.set_title('strategy 6-10 score rate in 8 field', pad=20, fontsize=14, fontweight='bold')
        ax2.grid(True)
        
        output_path2 = "../image/radar_chart_strategies_6-10.png"
        plt.savefig(output_path2, dpi=300, bbox_inches='tight')
        print(f"✓ 雷达图2已保存: {output_path2}")
        plt.close()
    
    # 打印统计数据
    print("\n" + "=" * 70)
    print("策略-领域得分率统计")
    print("=" * 70)
    
    for strategy in strategies:
        print(f"\n{strategy}:")
        for domain in domains:
            rate = score_rates[strategy].get(domain, 0)
            print(f"  {domain}: {rate:.2%}")


def main():
    """主函数"""
    results_dir = "../Results/deepseek"
    
    # 计算得分率
    print("步骤1: 计算得分率...")
    score_rates = calculate_domain_scores(results_dir)
    
    if not score_rates:
        print("错误: 没有找到任何数据")
        return
    
    # 生成雷达图
    print("\n步骤2: 生成雷达图...")
    create_radar_charts(score_rates, results_dir)
    
    print("\n" + "=" * 70)
    print("✓ 所有任务完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()