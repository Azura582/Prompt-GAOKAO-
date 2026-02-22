#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动评分程序
对results目录中的JSON结果文件进行自动评分
支持单选题和多选题的评分
"""

import os
import json
import time
from typing import List, Dict, Union
from pathlib import Path
import argparse

class AutoScorer:
    def __init__(self, results_dir: str = "../results", analysis_dir: str = "."):
        self.results_dir = Path(results_dir).resolve()
        self.analysis_dir = Path(analysis_dir).resolve()
        
        # 确保分析目录存在
        self.analysis_dir.mkdir(exist_ok=True)

    def _normalize_answer(self, answer: Union[List[str], str]) -> List[str]:
        """标准化答案格式"""
        if isinstance(answer, str):
            # 如果是字符串，提取其中的大写字母
            import re
            letters = re.findall(r'[A-Z]', answer.upper())
            return sorted(list(set(letters)))
        elif isinstance(answer, list):
            # 如果是列表，确保都是大写字母并去重排序
            normalized = []
            for item in answer:
                if isinstance(item, str):
                    import re
                    letters = re.findall(r'[A-Z]', item.upper())
                    normalized.extend(letters)
            return sorted(list(set(normalized)))
        else:
            return []
    
    def _calculate_score(self, standard_answer: List[str], model_answer: List[str], 
                        question_score: float, question_type: str = "single") -> float:
        """
        计算题目得分
        根据标准答案格式判断题型：
        - 如果标准答案是分离的选项（如["A", "C", "D"]），按比例得分
        - 如果标准答案是合并的选项（如["BC"]），多选题，有错误选项则0分
        """
        standard_set = set(standard_answer)
        model_set = set(model_answer)
        
        # 检查标准答案是否为分离格式（每个选项只有一个字母）
        is_separate_format = all(len(opt) == 1 for opt in standard_answer)
        
        if is_separate_format:
            # 分离格式：单选题在一块，按比例得分
            correct_matches = len(standard_set.intersection(model_set))
            total_standard = len(standard_set)
            
            if total_standard == 0:
                ratio = 1.0 if len(model_set) == 0 else 0.0
            else:
                # 计算正确率，不惩罚多选
                ratio = correct_matches / total_standard
            
        else:
            # 合并格式：多选题，如果有错误选项则0分
            # 将标准答案合并为单个集合
            all_standard_options = set()
            for opt in standard_answer:
                all_standard_options.update(self._normalize_answer(opt))
            
            # 检查模型答案是否完全匹配
            if model_set == all_standard_options:
                ratio = 1.0  # 完全匹配得满分
            else:
                # 检查是否有错误选项（模型选了不在标准答案中的选项）
                incorrect_selections = model_set - all_standard_options
                if incorrect_selections:
                    # 有多选错误选项，直接得0分
                    ratio = 0.0
                else:
                    # 没有多选错误，按正确选项比例得分
                    correct_matches = len(all_standard_options.intersection(model_set))
                    total_standard = len(all_standard_options)
                    if total_standard == 0:
                        ratio = 1.0 if len(model_set) == 0 else 0.0
                    else:
                        ratio = correct_matches / total_standard
        
        # 返回实际得分（题目分值 × 得分比例）
        return round(question_score * ratio, 2)
    
    def _determine_question_type(self, standard_answer: List[str]) -> str:
        """判断题目类型（单选或多选）"""
        # 根据标准答案格式判断
        is_separate_format = all(len(opt) == 1 for opt in standard_answer)
        return "separate" if is_separate_format else "combined"
    
    def _process_single_file(self, file_path: Path, progress_data: Dict) -> tuple:
        """处理单个JSON文件"""
        relative_path = str(file_path.relative_to(self.results_dir))
        
        print(f"\n处理文件: {relative_path}")
        
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data.get("questions", [])
            total_questions = len(questions)
            processed_count = 0
            total_score = 0.0  # 修复：添加总分变量
            
            for i, question in enumerate(questions):
                
                try:
                    # 提取标准答案和模型答案
                    standard_answer = question.get("standard_answer", [])
                    model_answer = question.get("model_answer", [])
                    
                    # 标准化答案
                    std_normalized = self._normalize_answer(standard_answer)
                    model_normalized = self._normalize_answer(model_answer)
                    
                    # 获取题目分值
                    question_score = question.get("score", 3.0)  # 默认3分
                    
                    # 计算得分
                    score = self._calculate_score(std_normalized, model_normalized, question_score)
                    
                    # 添加得分字段
                    question["model_score"] = score
                    
                    # 累计统计
                    total_score += score  # 累计总分
                    processed_count += 1
                    
                    # 每处理10题显示一次进度
                    if processed_count % 10 == 0:
                        print(f"  进度: {i+1}/{total_questions}")
                
                except Exception as e:
                    print(f"  错误处理题目 {i}: {e}")
                    continue
            
            # 文件处理完成
            if processed_count > 0:
                # 保存更新后的JSON文件（原地修改）
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 修复：计算平均分并打印结果
                avg_score = total_score / processed_count if processed_count > 0 else 0
                print(f"✓ 完成: {relative_path} | 题目数: {processed_count} | "
                      f"平均分: {avg_score:.3f}")
                
                return processed_count, avg_score
            else:
                print(f"⚠ 文件无题目需要处理: {relative_path}")
                return 0, 0
                
        except Exception as e:
            print(f"✗ 处理文件失败 {relative_path}: {e}")
            return 0, 0
    
    def scan_result_files(self) -> List[Path]:
        """扫描所有需要处理的JSON结果文件"""
        json_files = []
        
        if not self.results_dir.exists():
            print(f"错误: results目录不存在: {self.results_dir}")
            return json_files
        
        # 递归查找所有JSON文件
        for json_file in self.results_dir.rglob("*.json"):
            json_files.append(json_file)
        
        print(f"找到 {len(json_files)} 个JSON文件待处理")
        return json_files
    
    def run_scoring(self, max_files: int = None):
        """运行自动评分"""
        print("=" * 60)
        print("自动评分程序启动")
        print("=" * 60)
        
        # 扫描文件
        json_files = self.scan_result_files()
        if not json_files:
            print("没有找到需要处理的文件")
            return
        
        # 限制处理文件数量（用于测试）
        if max_files:
            json_files = json_files[:max_files]
            print(f"限制处理前 {max_files} 个文件")
        
        completed_files = 0
        total_processed = 0
        total_score_sum = 0.0
        
        # 处理每个文件
        for file_path in json_files:
            processed_count, avg_score = self._process_single_file(file_path, {})
            
            if processed_count > 0:
                completed_files += 1
                total_processed += processed_count
                total_score_sum += avg_score * processed_count
        
        print("\n" + "=" * 60)
        overall_avg = total_score_sum / total_processed if total_processed > 0 else 0
        print(f"评分完成! 处理文件数: {completed_files}, 处理题目数: {total_processed}, 总平均分: {overall_avg:.3f}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="自动评分程序")
    parser.add_argument("--results-dir", default="../results", 
                       help="results目录路径（默认: ../results）")
    parser.add_argument("--analysis-dir", default=".", 
                       help="分析结果保存目录（默认: 当前目录）")
    parser.add_argument("--max-files", type=int, 
                       help="最大处理文件数（用于测试）")
    
    args = parser.parse_args()
    
    # 创建评分器并运行
    scorer = AutoScorer(args.results_dir, args.analysis_dir)
    scorer.run_scoring(args.max_files)


if __name__ == "__main__":
    main()