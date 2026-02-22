import json

import requests

from api_key import api_key_HUAWEI
from core.Model import Model
from core.Strategies import STRATEGIES
from core.benchmark_utils import extract_objective_answer, extract_choices


api_key = api_key_HUAWEI
base_url = "https://api.modelarts-maas.com/v2/chat/completions"

# ========== 模型 ==========
# model_name = "DeepSeek-R1"
# model_name = "deepseek-v3.2"
# model_name = "qwen3-235b-a22b"
# model_name = "qwen2.5-vl-72b"

# MODEL = Model(api_key, base_url, model_name, temperature=0.3)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# 题目数据
question_data = {
    "year": "2024",
    "category": "全国甲卷",
    "question": "5. W、X、Y、 Z 为原子序数依次增大 ${ }^{\\square}$ 短周期元素。 W 和 X 原子序数之和等于 $\\mathrm{Y}^{-}$的核外电子数, 化合物 $\\mathrm{W}^{+}\\left[\\mathrm{ZY}_{6}\\right]^{-5}$ 可用作化学电源的电解质。下列叙述正确的是\nA. X 和 Z 属于同一主族\nB. 非属性： $\\mathrm{X}>\\mathrm{Y}>\\mathrm{Z}$\nC. 气态氢化物的稳定性： $\\mathrm{Z}>\\mathrm{Y}$\nD. 原子半径: $Y>X>W$",
    "answer": [
        "A"
    ],
    "analysis": "【分析】 $\\mathrm{W} 、 \\mathrm{X} 、 \\mathrm{Y} 、 \\mathrm{Z}$ 为原子序数依次增大的短周期元素，且能形成离子化合物 $\\mathrm{W}^{+}\\left[\\mathrm{ZY}_{6}\\right]$ ，则 W 为 Li 或 Na ；又由于 W 和 X 原子序数之和等于 $\\mathrm{Y}^{-}$的核外电子数，若 W 为 Na ， X 原子序数大于 Na ，则 W 和 X 原子序数之和大于 18 ，不符合题意，因此 W 只能为 Li 元素；由于 Y 可形成 $\\mathrm{Y}^{-}$，故 Y 为第VII主族元素，且原子序数 Z 大于 Y ，故 Y 不可能为 Cl 元素，因此 Y 为 F 元素， X 的原子序数为 $10-3=7, \\mathrm{X}$ 为 N 元素；根据 $\\mathrm{W} 、 \\mathrm{Y} 、 \\mathrm{Z}$ 形成离子化合物 $\\mathrm{W}^{+}\\left[\\mathrm{ZY}_{6}\\right]^{-}$，可知 Z 为 P 元素；综上所述， W 为 Li 元素， X 为 N 元素， Y 为 F 元素， $Z$ 为 $P$ 元素。\n【详解】A. 由分析可知, X 为 N 元素, Z 为 P 元素, X 和 Z 属于同一主族, A 项正确;\nB. 由分析可知, $X$ 为 $N$ 元素, $Y$ 为 $F$ 元素, $Z$ 为 $P$ 元素, 非金属性: $F>N>P, B$ 项错误;\nC. 由分析可知, Y 为 F 元素, Z 为 P 元素, 非金属性越强, 其简单气态氢化物的稳定性越强, 即气态氢化物的稳定性: $\\mathrm{HF}>\\mathrm{PH}_{3}$, C 项错误;\nD. 由分析可知, W 为 Li 元素, X 为 N 元素, Y 为 F 元素, 同周期主族元素原子半径随着原子序数的增大而减小, 故原子半径: $\\mathrm{Li}>\\mathrm{N}>\\mathrm{F}, \\mathrm{D}$ 项错误;\n故选 A。",
    "index": 219,
    "score": 6
}



# 数据字典 键
index  = question_data['index']
year = question_data['year']
category = question_data['category']
score = question_data['score']
standard_answer =question_data['answer']
answer_length = len(standard_answer)
analysis = question_data['analysis']

# 题目
question = question_data['question'].strip() + '\n'

# 图片
# pictures = question_data['picture']

# 领域通用提示词
# general_prompt = (
#     "请解答下面的自然科学问题\n仔细阅读题目,解答其中的问题，请你严格使用如下的思考解答策略和回答格式来解答问题并将思考过程写在【解析】和<eoe>之间。你的答案请写在【答案】和<eoa>之间\n完整的题目回答格式如下：\n【解析】 ...<eoe>\n【答案】...<eoa>\n \n请你严格按照上述格式作答；如果不止一道题，请分别作答，最终所有答案排好顺序全都写在【答案】...<eoa>中，只写答案字母，如【解析】 ...<eoe>\n【答案】A A B B C<eoa>。\n题目和思考策略如下："
# ,)

# 多模态领域提示词
general_prompt = "请解答下面的问题\n仔细阅读题目,解答其中的问题，请你严格使用如下的思考解答策略和回答格式来解答问题并将思考过程写在【解析】和<eoe>之间。你的答案请写在【答案】和<eoa>之间\n完整的题目回答格式如下：\n【解析】 ...<eoe>\n【答案】...<eoa>\n \n请你严格按照上述格式作答；如果不止一道题，请分别作答，最终所有答案排好顺序全都写在【答案】...<eoa>中，只写答案字母，如【解析】 ...<eoe>\n【答案】A A B B C<eoa>。\n策略、题目如下：",


# 策略
s_index = 9
strategy_description = STRATEGIES[s_index]["description"]
strategy_name = STRATEGIES[s_index]["name"]

full_prompt = f"{general_prompt}\n\n【解题策略】\n{strategy_description}\n\n【题目】\n{question}"

# full_prompt = "你是deepseek-v3.2吗？"
print(full_prompt)



# 请求
# response = MODEL.execute(full_prompt,pictures=pictures)
# print(json.dumps(response.text, indent=2, ensure_ascii=False))
# response_data = response.json()
# model_output = response_data["choices"][0]["message"]["content"]
# model_output = input("请输入模型输出:")
# model_answer = extract_objective_answer(model_output, question_type='single_question_choice')
#
# print(model_output)
# print(model_answer)

model_answer = []
choice = input("请输入模型答案：")

model_answer.append(choice)
print(strategy_name)
# 数据字典
model_answer_dict = {
    'index': index,
    'year': year,
    'category': category,
    'score': score,
    'question': question,
    'standard_answer': standard_answer,
    'analysis': analysis,
    'model_answer': model_answer,
    # 'model_output': model_output
}

print(json.dumps(model_answer_dict, indent=2, ensure_ascii=False))