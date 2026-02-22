import json
import os
import time
import requests
from typing import Dict, List
from tqdm import tqdm
import codecs


class AIAnswerGenerator:
    """AI答题生成器类"""
    
    def __init__(self, 
                 api_url,
                 api_key,
                 model_name,
                 subdata_dir,
                 results_dir):
        """
        初始化AI答题生成器
        
        :param api_url: AI API的URL地址
        :param api_key: API密钥
        :param model_name: 使用的模型名称
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        
        # 加载策略列表
        self.strategies = self.load_strategies()
        
        # 加载提示词模板
        self.prompt_templates = self.load_prompt_templates()
        
        # 设置路径
        self.subdata_dir = subdata_dir
        self.results_dir = results_dir
        
        # 创建结果目录
        #os.makedirs(self.results_dir, exist_ok=True)
    
    def load_strategies(self) -> List[str]:
        """加载策略列表"""
        from strategy import STRATEGIES
        return STRATEGIES
    
    def load_prompt_templates(self) -> Dict[str, str]:
        """加载提示词模板"""
        with codecs.open('Sub_Prompt.json', 'r', 'utf-8') as f:
            data = json.load(f)
        
        templates = {}
        for example in data['examples']:
            keyword = example['keyword']
            templates[keyword] = example['prefix_prompt']
        
        return templates
    
    def call_ai_api(self, prompt: str,question:str, max_retries: int = 3) -> str:
        """
        调用AI API获取回答
        
        :param prompt: 完整的提示词
        :param max_retries: 最大重试次数
        :return: AI的回答
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system","content":prompt},
                {"role": "user", "content": question}
            ],
            "temperature": 0.5,
            "max_tokens": 500
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=1000
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    print(f"API请求失败，状态码: {response.status_code}")
                    time.sleep(2 ** attempt)  # 指数退避
                    
            except Exception as e:
                print(f"API调用出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return "API调用失败，无法获取答案"
        
        return "API调用失败，无法获取答案"
    
    def construct_prompt(self, 
                        question_data: Dict, 
                        template: str, 
                        strategy: str) -> str:
        """
        构造完整的提示词
        
        :param question_data: 问题数据
        :param template: 提示词模板
        :param strategy: 当前使用的策略
        :return: 完整的提示词
        """
        question_text = question_data.get('question', '')
        
        # 组合：模板 + 策略 + 题目
        full_prompt = f"{template}\n\n【解题策略】\n{strategy}\n"
        question = f"\n【题目】\n{question_text}"
        return full_prompt,question
    
    def process_single_question(self, 
                                question_data: Dict, 
                                template: str, 
                                strategy: str) -> Dict:
        """
        处理单个问题
        
        :param question_data: 问题数据
        :param template: 提示词模板
        :param strategy: 当前策略
        :return: 包含AI回答的问题数据
        """
        # 构造提示词
        prompt,question = self.construct_prompt(question_data, template, strategy)
        
        # 调用AI API
        ai_answer = self.call_ai_api(prompt,question)
        
        # 创建结果数据
        result = question_data.copy()
        result['model_output'] = ai_answer
        result['strategy'] = strategy
        
        # 添加API调用时间戳
        result['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return result
    
    def process_category_file(self, 
                             category_file: str, 
                             strategy: str, 
                             strategy_idx: int) -> None:
        """
        处理单个分类文件
        
        :param category_file: 分类文件名
        :param strategy: 当前策略
        :param strategy_idx: 策略索引
        """
        # 读取问题数据
        file_path = os.path.join(self.subdata_dir, category_file)
        with codecs.open(file_path, 'r', 'utf-8') as f:
            data = json.load(f)
        
        # 获取对应的提示词模板
        category_name = category_file.replace('.json', '')
        template = self.prompt_templates.get(category_name, '')
        
        if not template:
            print(f"警告: 未找到 {category_name} 的提示词模板")
            return
        
        # 处理每个问题
        results = []
        examples = data.get('example', [])
        
        print(f"  处理类别: {category_name} (共 {len(examples)} 道题)")
        
        for question in tqdm(examples, desc=f"    {category_name}"):
            result = self.process_single_question(question, template, strategy)
            results.append(result)
            
            # 避免API限流
            time.sleep(0.5)
        
        # 保存结果
        strategy_name = f"Strategy_{strategy_idx}_{strategy.split('(')[1].split(')')[0] if '(' in strategy else strategy[:10]}"
        strategy_dir = os.path.join(self.results_dir, strategy_name)
        os.makedirs(strategy_dir, exist_ok=True)
        
        output_file = os.path.join(strategy_dir, category_file)
        output_data = {
            'category': category_name,
            'strategy': strategy,
            'model_name': self.model_name,
            'example': results
        }
        
        with codecs.open(output_file, 'w', 'utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        
        print(f"  ✓ 已保存: {output_file}")
    
    def run(self):
        """运行主程序"""
        print("=" * 70)
        print("AI答题生成器 - 开始运行")
        print("=" * 70)
        print(f"模型: {self.model_name}")
        print(f"策略数量: {len(self.strategies)}")
        print(f"数据目录: {self.subdata_dir}")
        print(f"结果目录: {self.results_dir}")
        print("=" * 70)
        
        # 获取所有分类文件
        category_files = [f for f in os.listdir(self.subdata_dir) if f.endswith('.json')]
        print(f"找到 {len(category_files)} 个分类文件")
        print("=" * 70)
        
        # 外层循环: 遍历策略
        for strategy_idx, strategy in enumerate(self.strategies[6:7]):
            print(f"\n[策略 {strategy_idx + 1}/{len(self.strategies)}] {strategy}")
            print("-" * 70)
            
            # 内层循环: 遍历每个分类文件
            for category_file in category_files:
                try:
                    self.process_category_file(category_file, strategy, strategy_idx)
                except Exception as e:
                    print(f"处理失败: {category_file}, 错误: {str(e)}")
            
            print("-" * 70)
            print(f"策略 {strategy_idx + 1} 完成\n")
        
        print("=" * 70)
        print("✓ 所有任务完成！")
        print("=" * 70)


def main():
    """主函数"""
    # 配置参数
    API_URL = "https://api.modelarts-maas.com/v2/chat/completions"  # 替换为实际的API地址
    API_KEY = "o8sPZqgLh7F2n2kDHl-Y_GaJVoMQkfjCVbY7_yXSN7Ss95l88XB3e-stW0jbAOBOc6FqYWJ4ZMI6pzo11vOwAQ"  # 替换为实际的API密钥
    MODEL_NAME = "qwen3-235b-a22b"  # 或其他模型名称
    
    
    subdata_dir="../reclassData/subdata"
    results_dir="../Results/qwen"
    # 创建生成器实例
    generator = AIAnswerGenerator(
        api_url=API_URL,
        api_key=API_KEY,
        model_name=MODEL_NAME,
        subdata_dir=subdata_dir,
        results_dir=results_dir
    )
    
    # 运行
    generator.run()


if __name__ == "__main__":
    main()