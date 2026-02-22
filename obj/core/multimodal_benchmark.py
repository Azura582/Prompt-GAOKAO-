import json
import os

from Model import Model  # 模型
from api_key import api_key_HUAWEI

from Fields import FIELDS
from Strategies import STRATEGIES
from core.benchmark_utils import load_questions_from_file, to_tackle_questions
from Multimodal_Field import Multimodal_Field

def main():
    api_key = api_key_HUAWEI

    # 参数：v1
    base_url = "https://api.modelarts-maas.com/v1/chat/completions"

    # 模型
    model_name = "qwen2.5-vl-72b"


    MODEL = Model(api_key, base_url, model_name, temperature=0.3)

    current_root = os.path.dirname(os.path.abspath(__file__))
    prompt_file_path = os.path.join(current_root, "Obj_Prompt.json")

    try:
        with open(prompt_file_path, 'r', encoding="utf-8") as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Error: 无法加载提示词文件 {prompt_file_path}: {e}")
        return

    total_fields = len(Multimodal_Field)

    print(f"====== 正在测试模型：{model_name} ======")
    for field_index, field in enumerate(Multimodal_Field):
        print(f"\n{'=' * 50}")
        print(f"正在处理领域 [{field_index + 1}/{total_fields}]: {field}")
        print(f"{'=' * 50}")

        for strategy_index, strategy in enumerate(STRATEGIES):
            strategy_name = strategy.get('name', 'Unknown')
            strategy_description = strategy['description']
            print(f"\n>>> 策略 [{strategy_index + 1}/{len(STRATEGIES)}]: {strategy_name}:{strategy_description}")

            try:
                # general_prompt = prompts["examples"][field_index]["prefix_prompt"]
                general_prompt = "请解答下面的问题\n仔细阅读题目,解答其中的问题，请你严格使用如下的思考解答策略和回答格式来解答问题并将思考过程写在【解析】和<eoe>之间。你的答案请写在【答案】和<eoa>之间\n完整的题目回答格式如下：\n【解析】 ...<eoe>\n【答案】...<eoa>\n \n请你严格按照上述格式作答；如果不止一道题，请分别作答，最终所有答案排好顺序全都写在【答案】...<eoa>中，只写答案字母，如【解析】 ...<eoe>\n【答案】A A B B C<eoa>。\n策略、题目、图片如下：",

                project_root = os.path.dirname(current_root)
                source_file_path = os.path.join(project_root, r"Data\Multimodal_Information", field + ".json")

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
                    strategy=strategy,
                )
            except IndexError:
                print(f"警告: 领域索引 {field_index} 在 Obj_Prompt.json 中无对应配置")
            except Exception as e:
                print(f"执行异常 (领域:{field}, 策略:{strategy_name}): {e}")
                continue


if __name__ == "__main__":
    main()
