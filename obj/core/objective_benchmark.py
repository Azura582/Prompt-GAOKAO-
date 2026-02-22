import json
import os

from Model import Model # 模型
from api_key import api_key_HUAWEI

from Fields import FIELDS
from Strategies import STRATEGIES
from core.benchmark_utils import load_questions_from_file, to_tackle_questions


def main():
    api_key = api_key_HUAWEI
    # 参数：v2
    base_url = "https://api.modelarts-maas.com/v2/chat/completions"

    # 模型
    model_name = "DeepSeek-R1"
    # model_name = "deepseek-v3.2"
    # model_name = "qwen3-235b-a22b"

    MODEL = Model(api_key, base_url, model_name, temperature=0.3)

    current_root = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(current_root, "Obj_Prompt.json")
    
    try:
        with open(prompt_file_path, 'r', encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Error: 无法加载提示词文件 {prompt_file_path}: {e}")
        return

    total_fields = len(FIELDS)

    print(f"====== 正在测试模型：{model_name} ======")
    for field_index, field in enumerate(FIELDS):
        print(f"\n{'='*50}")
        print(f"正在处理领域 [{field_index + 1}/{total_fields}]: {field}")
        print(f"{'='*50}")

        for strategy_index, strategy in enumerate(STRATEGIES):
            strategy_name = strategy.get('name', 'Unknown')
            strategy_description  = strategy['description']
            print(f"\n>>> 策略 [{strategy_index + 1}/{len(STRATEGIES)}]: {strategy_name}:{strategy_description}")
            
            try:
                general_prompt = prompts["examples"][field_index]["prefix_prompt"]
                project_root = os.path.dirname(current_root)
                source_file_path = os.path.join(project_root, r"Data\Objective", field + ".json")

                if not os.path.exists(source_file_path):
                    print(f"跳过: 找不到题目文件 {source_file_path}")
                    continue

                data = load_questions_from_file(source_file_path)
                num = len(data)

                to_tackle_questions(
                    data,
                    0,
                    num,
                    MODEL,
                    general_prompt,
                    field=field,
                    strategy=strategy
                )
            except IndexError:
                print(f"警告: 领域索引 {field_index} 在 Obj_Prompt.json 中无对应配置")
            except Exception as e:
                print(f"执行异常 (领域:{field}, 策略:{strategy_name}): {e}")
                continue


if __name__ == "__main__" :
    main()
