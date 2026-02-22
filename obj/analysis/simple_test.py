#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试版本 - 只进行评分，不计算统计
"""

import json
from pathlib import Path
from auto_scoring import AutoScorer

def simple_test():
    """简单测试评分功能"""
    print("开始简化测试...")
    
    # 创建评分器
    scorer = AutoScorer()
    
    # 测试文件
    test_file = Path("../results/DeepSeek-R1/Commonsense_and_WorldKnowledge/Strategy_0_CoT.json")
    
    if not test_file.exists():
        print(f"测试文件不存在: {test_file}")
        return False
    
    print(f"测试文件: {test_file.name}")
    
    # 处理文件
    processed_count, _ = scorer._process_single_file(test_file, {})
    
    print(f"处理完成，共评分 {processed_count} 道题目")
    
    # 验证结果
    with open(test_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 检查前几个题目的评分结果
    print("\n前3个题目的评分结果:")
    for i in range(min(3, len(data['questions']))):
        q = data['questions'][i]
        print(f"题目 {i}:")
        print(f"  标准答案: {q['standard_answer']}")
        print(f"  模型答案: {q['model_answer']}")
        print(f"  题目分值: {q['score']}")
        print(f"  模型得分: {q.get('model_score', '未评分')}")
        print()
    
    return True

if __name__ == "__main__":
    simple_test()