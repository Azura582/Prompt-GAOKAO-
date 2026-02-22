import json

filename = "../ObjectiveProblems/2010-2025_Chemistry_MCQs.json"  # 源文件

# 1. 读取文件
with open(filename, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 遍历 questions 列表并删除每个对象中的 field 字段
for q in data["questions"]:
    if "field" in q:
        del q["field"]

# 3. 写回原文件
with open(filename, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("删除完成：所有 field 字段已移除")
