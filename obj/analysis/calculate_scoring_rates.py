import os
import json
import matplotlib.pyplot as plt
import csv
import sys

# 确保可以从项目根目录导入 core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.Fields import FIELDS
from core.Strategies import STRATEGIES

# 设置模型列表
MODELS = ["DeepSeek-R1", "deepseek-v3.2", "qwen3-235b-a22b","qwen2.5-vl-72b"]

# 数据根目录
RESULTS_DIR = "results"
ANALYSIS_RESULTS_DIR = "analysis_results"

def calculate_scoring_rates():
    """统计每个模型在不同领域、不同策略下的得分率并绘图"""

    os.chdir("..")
    print(os.getcwd())

    # 确保图片根目录存在
    if not os.path.exists(ANALYSIS_RESULTS_DIR):
        os.makedirs(ANALYSIS_RESULTS_DIR)

    for model in MODELS:
        print(f"正在处理模型: {model}")
        for field in FIELDS:
            field_results = []
            
            # 对应的结果目录
            field_dir = os.path.join(RESULTS_DIR, model, field)
            if not os.path.exists(field_dir):
                print(f"警告: 目录不存在 {field_dir}")
                continue
                
            for strategy in STRATEGIES:
                strategy_name = strategy["name"]
                # 文件名格式: Strategy_0_CoT.json
                # strategy_name 格式: _0_CoT
                file_name = f"Strategy{strategy_name}.json"
                file_path = os.path.join(field_dir, file_name)
                
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        total_score = 0
                        total_model_score = 0
                        
                        # 如果 data 是字典且包含 questions 键
                        if isinstance(data, dict) and "questions" in data:
                            for item in data["questions"]:
                                total_score += item.get("score", 0)
                                total_model_score += item.get("model_score", 0)
                        elif isinstance(data, list):
                            for item in data:
                                total_score += item.get("score", 0)
                                total_model_score += item.get("model_score", 0)
                        
                        scoring_rate = (total_model_score / total_score) if total_score > 0 else 0
                        field_results.append({
                            "strategy": strategy_name.lstrip('_'), # 去掉前导下划线用于显示
                            "scoring_rate": scoring_rate,
                            "total_score": total_score,
                            "total_model_score": total_model_score
                        })
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错: {e}")
                else:
                    # print(f"文件不存在: {file_path}")
                    pass

            if field_results:
                save_results(model, field, field_results)

def save_results(model, field, results):
    """保存数据结果和生成图片"""
    # 目标目录
    target_dir = os.path.join(ANALYSIS_RESULTS_DIR, model, field)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    # 1. 保存 CSV 数据
    csv_path = os.path.join(target_dir, "scoring_rates.csv")
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["strategy", "scoring_rate", "total_score", "total_model_score"])
        writer.writeheader()
        writer.writerows(results)
    
    # 2. 生成条形图
    strategies = [r["strategy"] for r in results]
    rates = [r["scoring_rate"] for r in results]
    
    # 找出得分率最高的索引
    max_rate = max(rates) if rates else 0
    # 设置条形图颜色列表 (使用用户指定的 RGB 颜色)
    color_blue = (125/255, 180/255, 249/255)
    color_red = (255/255, 102/255, 102/255)
    colors = [color_red if r == max_rate and r > 0 else color_blue for r in rates]
    
    plt.figure(figsize=(10, 6))
    # 倒序排列，使 Strategy 0 在最上面
    # 注意：plt.barh 需要对应的颜色列表也倒序
    plt.barh(strategies[::-1], rates[::-1], color=colors[::-1])
    plt.xlabel('得分率 (Scoring Rate)')
    plt.ylabel('策略 (Strategy)')
    plt.title(f'{model} - {field}')
    plt.xlim(0, 1.1)
    
    # 在条形图上添加数值标签
    for i, v in enumerate(rates[::-1]):
        plt.text(v + 0.01, i, f"{v:.2%}", va='center')
        
    plt.tight_layout()
    plot_path = os.path.join(target_dir, "scoring_rate_chart.png")
    plt.savefig(plot_path)
    plt.close()
    
    print(f"已保存结果到: {target_dir}")

if __name__ == "__main__":
    # 设置支持中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei'] # Windows 常用中文字体
    plt.rcParams['axes.unicode_minus'] = False
    
    calculate_scoring_rates()
