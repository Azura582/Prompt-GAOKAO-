#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新评分系统
功能：检查 Results/deepseek 文件夹中所有评分为 0.0 的问题，进行重新评分
"""

import json
import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm
import codecs


class ReGradingSystem:
    """重新评分系统 - 专门处理评分为0.0的问题"""
    
    def __init__(self, 
                 api_url: str,
                 api_key: str,
                 model_name: str,
                 results_dir: str = "../Results/deepseek",
                 backup: bool = True,
                 max_retries: int = 3):
        """
        初始化重新评分系统
        
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
        print("重新评分系统 - 初始化完成")
        print("=" * 70)
        print(f"模型: {self.model_name}")
        print(f"结果目录: {self.results_dir}")
        print(f"备份原文件: {self.backup}")
        print(f"目标: 重新评分所有 teacher_score = 0.0 的题目")
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
- 即使答案不完全正确，也要根据部分得分原则给予适当分数
- 给出详细的评分分析，说明得分和扣分的理由
- 给出最终得分（0到满分之间的数值）

请按以下JSON格式返回结果：
{
    "teacher_analysis": "详细的评分分析，包括答案的正确性、完整性、准确性等方面的评价",
    "teacher_score": 最终得分（数值类型）
}

注意：
- teacher_score 必须是数值类型，范围在 0 到满分之间
- 如果模型输出包含部分正确内容，应给予部分分数
- 只有在模型输出完全错误或无效时才给0分
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

请重新评分，注意部分得分原则。
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
                    "content": "你是一位专业的高考阅卷教师，负责对AI模型的答题进行公正、严格的评分。注意部分得分原则。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 5000
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # 尝试解析JSON格式的返回
                    try:
                        # 提取JSON部分
                        if '```json' in content:
                            content = content.split('```json')[1].split('```')[0].strip()
                        elif '```' in content:
                            content = content.split('```')[1].split('```')[0].strip()
                        
                        # 尝试解析JSON
                        try:
                            grading_result = json.loads(content)
                        except json.JSONDecodeError as e1:
                            # 如果失败，尝试修复常见的转义问题
                            print(f"  🔧 尝试修复JSON转义问题...")
                            
                            import re
                            # 修复单独的反斜杠（但保留已转义的）
                            fixed_content = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', content)
                            
                            try:
                                grading_result = json.loads(fixed_content)
                                print(f"  ✓ JSON修复成功")
                            except json.JSONDecodeError as e2:
                                print(f"  ⚠ JSON修复失败: {str(e2)}")
                                print(f"  原始内容预览: {content[:200]}...")
                                # 降级处理：从文本中提取信息
                                return self._extract_from_raw_text(content)
                        
                        # 验证返回格式
                        if 'teacher_analysis' in grading_result and 'teacher_score' in grading_result:
                            try:
                                grading_result['teacher_score'] = float(grading_result['teacher_score'])
                            except (ValueError, TypeError):
                                grading_result['teacher_score'] = 0.0
                            
                            return grading_result
                        else:
                            print(f"  ⚠ API返回格式不正确，缺少必要字段")
                            return self._extract_from_raw_text(content)
                            
                    except json.JSONDecodeError as e:
                        print(f"  ⚠ 无法解析API返回的JSON: {str(e)}")
                        print(f"  返回内容长度: {len(content)}")
                        return self._extract_from_raw_text(content)
                else:
                    print(f"  ⚠ API请求失败，状态码: {response.status_code}")
                    time.sleep(2 ** attempt)
                    
            except Exception as e:
                print(f"  ⚠ API调用出错 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        
        return None
    
    def _extract_from_raw_text(self, content: str) -> Dict:
        """
        从原始文本中提取评分信息（降级处理）
        当JSON解析失败时使用
        
        :param content: 原始返回内容
        :return: 评分结果字典
        """
        import re
        
        # 尝试提取分数
        score = 0.0
        score_patterns = [
            r'"?teacher_score"?\s*[：:]\s*([0-9.]+)',
            r'最终得分\s*[：:]\s*([0-9.]+)',
            r'得分\s*[：:]\s*([0-9.]+)',
            r'评分\s*[：:]\s*([0-9.]+)',
            r'(\d+\.?\d*)\s*分'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    score = float(match.group(1))
                    break
                except:
                    pass
        
        # 使用原始内容作为分析（清理可能的JSON标记）
        analysis = content.strip()
        analysis = re.sub(r'```json|```', '', analysis).strip()
        
        print(f"  ⚠ 使用降级处理，提取到分数: {score}")
        
        return {
            "teacher_analysis": analysis,
            "teacher_score": score
        }
    
    def regrade_question(self, question_data: Dict) -> Dict:
        """
        重新评分单个问题
        
        :param question_data: 问题数据
        :return: 更新后的问题数据
        """
        # 构造评分提示词
        prompt = self.construct_grading_prompt(question_data)
        
        # 调用教师AI
        grading_result = self.call_teacher_api(prompt)
        
        if grading_result:
            # 直接覆盖原有的评分信息
            question_data['teacher_analysis'] = grading_result['teacher_analysis']
            question_data['teacher_score'] = grading_result['teacher_score']
            # 更新评分时间戳
            question_data['grading_timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # API调用失败，保持原评分
            print(f"  ⚠ 重新评分失败，保持原评分")
        
        return question_data
    
    def scan_and_collect_zero_scores(self) -> Dict[str, List]:
        """
        扫描所有文件，收集评分为0.0的问题
        
        :return: 字典，key为文件路径，value为需要重新评分的问题索引列表
        """
        zero_score_map = {}
        
        if not self.results_dir.exists():
            print(f"错误: 结果目录不存在: {self.results_dir}")
            return zero_score_map
        
        # 遍历所有策略文件夹
        strategy_dirs = [d for d in self.results_dir.iterdir() if d.is_dir()]
        
        print("\n开始扫描评分为0.0的问题...")
        print("=" * 70)
        
        total_zero_count = 0
        
        for strategy_dir in sorted(strategy_dirs):
            json_files = list(strategy_dir.glob("*.json"))
            
            for json_file in json_files:
                try:
                    with codecs.open(json_file, 'r', 'utf-8') as f:
                        data = json.load(f)
                    
                    examples = data.get('example', [])
                    zero_indices = []
                    
                    for idx, ex in enumerate(examples):
                        teacher_score = ex.get('teacher_score', None)
                        if teacher_score is not None and float(teacher_score) == 0.0:
                            zero_indices.append(idx)
                    
                    if zero_indices:
                        zero_score_map[str(json_file)] = zero_indices
                        total_zero_count += len(zero_indices)
                        print(f"  {strategy_dir.name}/{json_file.name}: {len(zero_indices)} 道题")
                
                except Exception as e:
                    print(f"  ✗ 读取文件失败: {json_file}, 错误: {str(e)}")
        
        print("=" * 70)
        print(f"扫描完成！共找到 {total_zero_count} 道评分为0.0的题目")
        print("=" * 70)
        
        return zero_score_map
    
    def process_file(self, file_path: str, zero_indices: List[int]) -> bool:
        """
        处理单个文件，重新评分指定的问题
        
        :param file_path: 文件路径
        :param zero_indices: 需要重新评分的问题索引列表
        :return: 处理是否成功
        """
        try:
            file_path_obj = Path(file_path)
            
            # 读取文件
            with codecs.open(file_path_obj, 'r', 'utf-8') as f:
                data = json.load(f)
            
            examples = data.get('example', [])
            
            print(f"\n处理文件: {file_path_obj.name}")
            print(f"  需要重新评分: {len(zero_indices)} 道题")
            
            # 备份原文件
            if self.backup:
                backup_path = file_path_obj.with_suffix('.json.regrade_backup')
                if not backup_path.exists():
                    with codecs.open(backup_path, 'w', 'utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
            
            # 重新评分
            regraded_count = 0
            improved_count = 0
            
            for idx in tqdm(zero_indices, desc=f"  重新评分进度"):
                if idx < len(examples):
                    old_score = examples[idx].get('teacher_score', 0.0)
                    examples[idx] = self.regrade_question(examples[idx])
                    new_score = examples[idx].get('teacher_score', 0.0)
                    
                    regraded_count += 1
                    
                    if new_score > old_score:
                        improved_count += 1
                    
                    # 每5道题保存一次
                    if regraded_count % 5 == 0:
                        with codecs.open(file_path_obj, 'w', 'utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                    
                    # 避免API限流
                    time.sleep(0.5)
            
            # 最终保存
            with codecs.open(file_path_obj, 'w', 'utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f"  ✓ 完成重新评分: {regraded_count} 道题")
            print(f"  📈 评分提高: {improved_count} 道题")
            
            return True
            
        except Exception as e:
            print(f"  ✗ 处理文件失败: {file_path}, 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """运行重新评分系统"""
        # 第一步：扫描并收集所有评分为0.0的问题
        zero_score_map = self.scan_and_collect_zero_scores()
        
        if not zero_score_map:
            print("\n没有找到需要重新评分的题目！")
            return
        
        # 第二步：询问用户是否继续
        total_questions = sum(len(indices) for indices in zero_score_map.values())
        print(f"\n共需要重新评分 {total_questions} 道题目")
        print(f"涉及 {len(zero_score_map)} 个文件")
        
        # 第三步：处理每个文件
        print("\n开始重新评分...")
        print("=" * 70)
        
        success_count = 0
        fail_count = 0
        total_improved = 0
        
        for file_path, zero_indices in zero_score_map.items():
            success = self.process_file(file_path, zero_indices)
            if success:
                success_count += 1
            else:
                fail_count += 1
        
        # 打印总结
        print("\n" + "=" * 70)
        print("重新评分完成！")
        print("=" * 70)
        print(f"成功处理文件数: {success_count}")
        print(f"失败文件数: {fail_count}")
        print(f"总共重新评分: {total_questions} 道题")
        print("=" * 70)
        
        # 统计最终结果
        print("\n正在统计最终结果...")
        self.print_final_statistics()
    
    def print_final_statistics(self):
        """打印最终统计信息"""
        if not self.results_dir.exists():
            return
        
        total_zero = 0
        total_questions = 0
        
        strategy_dirs = [d for d in self.results_dir.iterdir() if d.is_dir()]
        
        for strategy_dir in strategy_dirs:
            json_files = list(strategy_dir.glob("*.json"))
            
            for json_file in json_files:
                try:
                    with codecs.open(json_file, 'r', 'utf-8') as f:
                        data = json.load(f)
                    
                    examples = data.get('example', [])
                    total_questions += len(examples)
                    
                    for ex in examples:
                        teacher_score = ex.get('teacher_score', None)
                        if teacher_score is not None and float(teacher_score) == 0.0:
                            total_zero += 1
                
                except Exception:
                    pass
        
        print("\n当前评分统计:")
        print(f"  总题目数: {total_questions}")
        print(f"  评分为0.0的题目: {total_zero}")
        print(f"  评分为0.0的比例: {total_zero/total_questions*100:.1f}%" if total_questions > 0 else "  评分为0.0的比例: 0%")


def main():
    """主函数"""
    
    # 创建重新评分系统
    regrading_system = ReGradingSystem(
        api_url="https://api.modelarts-maas.com/v2/chat/completions",
        api_key="b8cqSto69jOQF-D7AqVkqB_yIhrTUSk4VIR-yjwMn6cGLSo7HDYr8T8bn4JfyULRh2emudTgCAVxM7v_RNdbTA",
        model_name="qwen3-235b-a22b",
        results_dir="../Results/deepseek",
        backup=False
    )
    
    # 运行重新评分
    try:
        regrading_system.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
