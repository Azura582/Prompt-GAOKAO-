import json

# 科目分类
# filename = "ObjectiveProblems/2010-2025_Physics_MCQs.json"  
# filename = "ObjectiveProblems/2010-2025_Chemistry_MCQs.json"  
# filename = "ObjectiveProblems/2010-2025_Biology_MCQs.json"  
# filename = "ObjectiveProblems/2010-2025_Political_Science_MCQs.json"  
# filename = "ObjectiveProblems/2010-2025_History_MCQs.json"  
# filename = "ObjectiveProblems/2010-2025_Geography_MCQs.json"  

# 领域分类
# filename = "Fields\Mathematical_Reasoning.json"  
# filename = "Fields\Logical_Reasoning.json"  
# filename = "Fields\Lang_Comp_and_Produc.json"  
# filename = "Fields\Natural_Science.json"  
# filename = "Fields\Sociocultural_Understanding.json"  
# filename = "Fields\Data_and_StatisticalLiteracy.json"  
# filename = "Fields\Commonsense_and_WorldKnowledge.json"  
# filename = "Fields\Creative_and_Open-ended_Questions.json"  

files=[
        "../Data/Multimodal_Information/Multimodal_Information.json"
    ]

for filename in files:
    # 1. 读取原文件
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 重排 index
    for new_index, question in enumerate(data["questions"]):
        print(new_index, end=' ')
        
        question["index"] = new_index
    print()

    # 3. 覆盖写回原文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)