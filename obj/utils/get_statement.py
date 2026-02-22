import json
import os

filename = "/2010-2025_Physics_MCQs.json"  
# filename = "/2010-2025_Chemistry_MCQs.json"  
# filename = "/2010-2025_Biology_MCQs.json"  
# filename = "/2010-2025_Political_Science_MCQs.json"  
# filename = "/2010-2025_History_MCQs.json"  
# filename = "/2010-2025_Geography_MCQs.json"  

source_file_prename= "../ObjectiveProblems"
target_file_prename="ObjectiveProblemStatements"
source_file=source_file_prename+filename
target_file=target_file_prename+filename


# ---- 读取已有文件 ----
with open(source_file, "r", encoding="utf-8") as f:
    source_data= json.load(f)

source_questions = source_data["questions"]


# ---- 若目标文件不存在 → 创建空模板 ----
if not os.path.exists(target_file):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    empty_content = {"keywords": "", "questions": []}
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(empty_content, f, ensure_ascii=False, indent=4)

with open(target_file, "r", encoding="utf-8") as f:

    target_data= json.load(f)
    target_data["questions"]=source_questions
    for q in target_data["questions"]:
        q.pop("year")
        q.pop("category")
        q.pop("answer")
        q.pop("analysis")
        q.pop("score")



# ---- 写回文件（不覆盖已有 questions，只是追加） ----
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(target_data, f, ensure_ascii=False, indent=4)

print(f"已写入：{target_file} 追加 {len(source_questions)} 个题目")

