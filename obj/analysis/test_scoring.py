#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评分程序的简化版本
"""

import json
from pathlib import Path

# 导入评分逻辑
from auto_scoring import AutoScorer

def test_single_file():
    """测试单个文件的评分"""
    scorer = AutoScorer()
    
    # 测试文件路径
    test_file = Path("../results/DeepSeek-R1/Commonsense_and_WorldKnowledge/Strategy_0_CoT.json")
    
    if not test_file.exists():
        print(f"测试文件不存在: {test_file}")
        return
    
    print("开始测试评分...")
    
    # 加载进度
    progress_data = scorer._load_progress()
    
    # 处理单个文件
    processed_count, avg_score = scorer._process_single_file(test_file, progress_data)
    
    print(f"\n测试结果:")
    print(f"处理题目数: {processed_count}")
    print(f"平均得分: {avg_score}")
    
    # 查看前几个题目的评分结果
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n前5个题目的评分结果:")
    for i, question in enumerate(data['questions'][:5]):
        print(f"题目 {i}: 标准答案={question['standard_answer']}, "
              f"模型答案={question['model_answer']}, "
              f"得分={question.get('model_score', '未评分')}")

if __name__ == "__main__":
    test_single_file()