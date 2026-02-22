#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师AI评分系统
功能：遍历 Results/deepseek 下的所有 JSON 文件，使用教师AI对模型输出进行评分
评分依据：question, answer, analysis, score 和 model_output
输出：teacher_analysis（评分分析）和 teacher_score（最终得分）
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import codecs
import argparse


class TeacherGradingSystem:
    """教师AI评分系统"""
    
    def __init__(self, 
                 api_url: str,
                 api_key: str,
                 model_name: str ,
                 results_dir: str ,
                 backup: bool = True,
                 max_retries: int = 3):
        """
        初始化教师AI评分系统
        
        :param api_url: 教师AI的API地址
        :param api_key: API密钥
        :param model_name: 使用的模型名称
        :param results_dir: 结果目录路径
        :param backup: 是否备份原文件
        :param max_retries: API调用最大重试次数
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.results_dir = Path(results_dir)
        self.backup = backup
        self.max_retries = max_retries
        
        # 构建评分提示词模板
        self.grading_prompt_template = self._build_grading_prompt()
        
        print("=" * 70)
        print("教师AI评分系统 - 初始化完成")
        print("=" * 70)
        print(f"模型: {self.model_name}")
        print(f"结果目录: {self.results_dir}")
        print(f"备份原文件: {self.backup}")
        print("=" * 70)
    
    def _build_grading_prompt(self) -> str:
        """构建评分提示词模板"""
        return """你是一位经验丰富的高考阅卷教师，需要对AI模型的答题结果进行评分。

请根据以下信息进行评分：
1. **题目（Question）**：AI需要回答的问题
2. **标准答案（Answer）**：正确答案参考
3. **解析（Analysis）**：题目的详细解析和评分标准
4. **满分（Score）**：本题的满分分值
5. **模型输出（Model Output）**：AI模型给出的答案

评分要求：
- 请仔细对比模型输出与标准答案
- 参考解析中的评分标准
- 给出详细的评分分析，说明得分和扣分的理由
- 给出最终得分（0到满分之间的数值）

请按以下JSON格式返回结果：
{
    "teacher_analysis": "详细的评分分析，包括答案的正确性、完整性、准确性等方面的评价",
    "teacher_score": 最终得分（数值类型）
}
- teacher_score范围在 0 到满分之间
- 评分要公平公正，严格参考标准答案和解析"""

    def construct_grading_prompt(self, question_data: Dict) -> str:
        """
        构造具体的评分提示词
        
        :param question_data: 包含题目信息的字典
        :return: 完整的评分提示词
        """
        question = question_data.get('question', '未提供题目')
        answer = question_data.get('answer', '未提供标准答案')
        analysis = question_data.get('analysis', '未提供解析')
        score = question_data.get('score', 0)
        model_output = question_data.get('model_output', '未提供模型输出')
        
        # 处理answer可能是列表的情况
        if isinstance(answer, list):
            answer = ', '.join(str(a) for a in answer)
        
        specific_prompt = f"""
【题目】
{question}
【标准答案】
{answer}
【题目解析】
{analysis}
【满分】
{score} 分
【模型输出】
{model_output}
"""
        
        return self.grading_prompt_template + "\n\n" + specific_prompt
    
    def call_teacher_api(self, prompt: str) -> Optional[Dict]:
        """
        调用教师AI的API进行评分
        
        :param prompt: 评分提示词
        :return: 包含 teacher_analysis 和 teacher_score 的字典，失败返回None
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的高考阅卷教师，负责对AI模型的答题进行公正、严格的评分。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4,  # 较低的温度以获得更稳定的评分
            "max_tokens": 1500
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=1000
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 尝试解析JSON格式的返回
                    try:
                        # 提取JSON部分（可能包含在markdown代码块中）
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        grading_result = json.loads(content)
                        
                        # 验证返回格式
                        if 'teacher_analysis' in grading_result and 'teacher_score' in grading_result:
                            # 确保分数是数值类型
                            try:
                                grading_result['teacher_score'] = float(grading_result['teacher_score'])
                            except (ValueError, TypeError):
                                grading_result['teacher_score'] = 0.0
                            
                            return grading_result
                        else:
                            print(f"  ⚠ API返回格式不正确，缺少必要字段")
                            
                    except json.JSONDecodeError:
                        print(f"  ⚠ 无法解析API返回的JSON: {content[:200]}")
                        # 尝试从文本中提取信息
                        return {
                            "teacher_analysis": content,
                            "teacher_score": 0.0
                        }
                else:
                    print(f"  ⚠ API请求失败，状态码: {response.status_code}")
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                print(f"  ⚠ API调用出错 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def grade_single_question(self, question_data: Dict) -> Dict:
        """
        对单个问题进行评分
        
        :param question_data: 问题数据
        :return: 添加了评分信息的问题数据
        """
        # 如果已经有教师评分，跳过
        if 'teacher_score' in question_data and 'teacher_analysis' in question_data:
            return question_data
        
        # 构造评分提示词
        prompt = self.construct_grading_prompt(question_data)
        
        # 调用教师AI
        grading_result = self.call_teacher_api(prompt)
        
        if grading_result:
            question_data['teacher_analysis'] = grading_result['teacher_analysis']
            question_data['teacher_score'] = grading_result['teacher_score']
        else:
            # API调用失败，给默认值
            question_data['teacher_analysis'] = "评分系统调用失败，无法给出评分"
            question_data['teacher_score'] = 0.0
        
        # 添加评分时间戳
        question_data['grading_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return question_data
    
    def process_json_file(self, file_path: Path) -> bool:
        """
        处理单个JSON文件
        
        :param file_path: JSON文件路径
        :return: 处理是否成功
        """
        try:
            # 读取文件
            with codecs.open(file_path, 'r', 'utf-8') as f:
                data = json.load(f)
            
            examples = data.get('example', [])
            if not examples:
                print(f"  ⚠ 文件为空或没有example字段: {file_path.name}")
                return False
            
            # 统计信息
            total = len(examples)
            already_graded = sum(1 for ex in examples if 'teacher_score' in ex)
            need_grading = total - already_graded
            
            print(f"\n处理文件: {file_path.name}")
            #print(f"  总题目数: {total}, 已评分: {already_graded}, 待评分: {need_grading}")
            
            if need_grading == 0:
                print(f"  ✓ 所有题目已评分，跳过")
                return True
            
            # 备份原文件
            if self.backup:
                backup_path = file_path.with_suffix('.json.backup')
                if not backup_path.exists():
                    with codecs.open(backup_path, 'w', 'utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 对每个问题进行评分
            graded_count = 0
            for i, example in enumerate(tqdm(examples, desc=f"  评分进度")):
                if 'teacher_score' not in example:
                    examples[i] = self.grade_single_question(example)
                    graded_count += 1
                    # 每评分5道题保存一次，防止中断丢失
                    if graded_count % 5 == 0:
                        with codecs.open(file_path, 'w', 'utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    # 避免API限流
                    time.sleep(0.5)
            
            # 最终保存
            with codecs.open(file_path, 'w', 'utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f"  ✓ 完成评分: {graded_count} 道题")
            return True
            
        except Exception as e:
            print(f"  ✗ 处理文件失败: {file_path.name}, 错误: {str(e)}")
            return False
    
    def run(self, strategy_filter: Optional[str] = None):
        """
        运行评分系统
        
        :param strategy_filter: 可选的策略过滤器，如 "Strategy_0_CoT"
        """
        if not self.results_dir.exists():
            print(f"错误: 结果目录不存在: {self.results_dir}")
            return
        
        # 获取所有策略文件夹
        strategy_dirs = [d for d in self.results_dir.iterdir() if d.is_dir()]
        
        if strategy_filter:
            strategy_dirs = [d for d in strategy_dirs if strategy_filter in d.name]
        
        if not strategy_dirs:
            print(f"未找到任何策略文件夹")
            return
        
        print(f"\n找到 {len(strategy_dirs)} 个策略文件夹")
        
        total_files = 0
        total_questions = 0
        total_graded = 0
        
        # 遍历每个策略文件夹
        for strategy_dir in sorted(strategy_dirs):
            print(f"\n{'='*70}")
            print(f"策略: {strategy_dir.name}")
            print(f"{'='*70}")
            
            # 获取所有JSON文件
            json_files = list(strategy_dir.glob("*.json"))
            
            if not json_files:
                print(f"  未找到JSON文件")
                continue
            
            # 处理每个JSON文件
            for json_file in sorted(json_files):
                total_files += 1
                success = self.process_json_file(json_file)
                
                if success:
                    # 统计评分数量
                    with codecs.open(json_file, 'r', 'utf-8') as f:
                        data = json.load(f)
                    examples = data.get('example', [])
                    total_questions += len(examples)
                    total_graded += sum(1 for ex in examples if 'teacher_score' in ex)
        
        # 打印总结
        print(f"\n{'='*70}")
        print(f"评分完成！")
        print(f"{'='*70}")
        print(f"处理文件数: {total_files}")
        print(f"总题目数: {total_questions}")
        print(f"已评分数: {total_graded}")
        print(f"评分率: {total_graded/total_questions*100:.1f}%" if total_questions > 0 else "评分率: 0%")
        print(f"{'='*70}")


def main():
    """主函数"""
    
    # 创建评分系统
    grading_system = TeacherGradingSystem(
        api_url="https://api.modelarts-maas.com/v2/chat/completions",
        api_key="b8cqSto69jOQF-D7AqVkqB_yIhrTUSk4VIR-yjwMn6cGLSo7HDYr8T8bn4JfyULRh2emudTgCAVxM7v_RNdbTA",
        model_name="qwen3-235b-a22b",
        results_dir="../Results/deepseek",
        backup=False
    )
    
    # 运行评分
    try:
        grading_system.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
