import json
import os


# Physics Objective 

# classification_filename = {
#     "Fields\Mathematical_Reasoning.json": [
#         0, 1, 2, 4, 7, 8, 9, 12, 15, 16, 17, 18, 20, 21, 23, 24,
#         28, 29, 32, 33, 34, 36, 37, 39, 40, 41, 42, 44, 45, 47,
#         49, 50, 51, 53, 54, 56, 57, 59, 60, 62, 63, 65, 66, 68,
#         69, 71, 72, 74, 75, 77, 78, 80
#     ],
#     "Fields\Logical_Reasoning.json": [
#         0, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 19, 22, 25,
#         26, 27, 30, 31, 35, 38, 43, 46, 48, 50, 52, 55, 58, 61,
#         64, 67, 70, 73, 76, 79
#     ],
#     "Fields\Lang_Comp_and_Produc.json": [],
#     "Fields\Natural_Science.json": [],
#     "Fields\Sociocultural_Understanding.json": [],
#     "Fields\Data_and_StatisticalLiteracy.json": [],
#     "Fields\Commonsense_and_WorldKnowledge.json": [
#         1, 5, 6, 7, 10, 13, 21, 31, 52, 67, 70
#     ],
#     "Fields\Creative_and_Open-ended_Questions.json": [],
# }

# Chemistry Objective 

# classification_filename = {
#     "Fields/Mathematical_Reasoning.json": [
#         1, 4, 6, 7, 14, 15, 16, 25, 26, 35, 36, 44, 45, 47, 60, 67, 74, 79, 82, 92, 98, 107, 121, 126
#     ],
#     "Fields/Logical_Reasoning.json": [
#         0, 2, 3, 5, 8, 9, 10, 11, 12, 13, 18, 20, 21, 22, 23, 24, 27, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, 42, 43, 46, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 61, 62, 64, 65, 66, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78, 80, 81, 83, 84, 85, 86, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 99, 100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 122, 123, 124, 125, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142
#     ],
#     "Fields/Lang_Comp_and_Produc.json": [
#     ],
#     "Fields/Natural_Science.json": [
#     ],
#     "Fields/Sociocultural_Understanding.json": [
#     ],
#     "Fields/Data_and_StatisticalLiteracy.json": [
#         17, 39, 73, 84, 123
#     ],
#     "Fields/Commonsense_and_WorldKnowledge.json": [
#         1, 12, 13, 19, 28, 32, 37, 41, 46, 50, 57, 62, 63, 66, 71, 76, 77, 85, 89, 91, 95, 100, 104, 106, 110, 113, 116, 119, 124, 131, 133, 136, 139
#     ],
#     "Fields/Creative_and_Open-ended_Questions.json": []
# }

# Biology Objective

# classification_filename = {
#     "Fields/Mathematical_Reasoning.json": [
#         17, 41, 52, 57, 63, 71, 105, 111, 113, 138, 149, 154, 159, 164],
#     "Fields/Logical_Reasoning.json": [
#         4, 8, 13, 28, 38, 40, 42, 58, 63, 67, 70, 77, 90, 91, 92, 94, 96, 99, 102, 104, 109, 116, 117, 120, 121, 123, 125, 127, 128, 129, 132, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179],
#     "Fields/Lang_Comp_and_Produc.json": [],
#     "Fields/Natural_Science.json": [],
#     "Fields/Sociocultural_Understanding.json": [
#         ],
#     "Fields/Data_and_StatisticalLiteracy.json": [
#         17, 41, 57, 76, 94, 105, 111, 113, 117, 138, 149, 154, 159, 163, 164],
#     "Fields/Commonsense_and_WorldKnowledge.json": [
#         5, 7, 25, 27, 32, 37, 51, 54, 59, 61, 62, 65, 69, 75, 80, 86, 87, 90, 91, 93, 95, 97, 98, 103, 104, 106, 107, 108, 110, 112, 114, 115, 118, 119, 122, 125, 126, 128, 130, 131, 134, 135, 136, 140, 141, 145, 146, 147, 148, 151, 152, 153, 154, 155, 156, 157, 158, 160, 161, 162, 165, 166, 167, 168, 170, 171, 173, 176, 177, 178, 179],
#     "Fields/Creative_and_Open-ended_Questions.json": []
# }

# Political_Science Objective

# classification_filename = {
#     "Fields/Mathematical_Reasoning.json": [
#     ],
#     "Fields/Logical_Reasoning.json": [
#         2, 3, 5, 6, 8, 9, 10, 11, 18, 19, 20, 21, 22, 23, 25, 26, 31, 34, 35, 43, 45, 46, 47, 56, 57, 58, 68, 69, 70, 72, 82, 83, 93, 94, 105, 106, 107, 117, 118, 119,        122, 128, 129, 130, 131, 134, 135, 137, 139, 140, 141, 142, 146, 150, 151, 152, 153, 154, 159, 164, 165, 166, 169, 170, 173, 175, 176, 177, 178, 180, 188, 189, 200, 201, 202, 206, 210, 211, 212,        247, 250, 251, 254, 255, 264, 265, 274, 275, 276, 285, 286, 296, 297, 307, 308, 317, 318, 319, 337, 338, 339, 340, 344, 348, 358, 359, 360, 372, 379, 384
#     ],
#     "Fields/Lang_Comp_and_Produc.json": [
#         7, 8, 29, 31, 32, 33, 44, 55, 67, 79, 80, 92,127, 131, 138, 142, 162, 163, 174, 186, 208,252, 272, 284, 285, 293, 304, 325, 326, 356, 371
#     ],
#     "Fields/Natural_Science.json": [
#     ],
#     "Fields/Sociocultural_Understanding.json": [
#     ],
#     "Fields/Data_and_StatisticalLiteracy.json": [
#         61, 74, 86, 98, 120, 143, 157, 168, 181, 182, 186, 193,279, 289, 300, 345, 352, 375
#     ],
#     "Fields/Commonsense_and_WorldKnowledge.json": [
#         4, 7, 15, 16, 27, 28, 30, 33, 40, 41, 44, 52, 54, 66, 73, 77, 78, 90, 91, 93, 121,132, 161, 176, 190,253, 255, 274, 303, 316, 321, 336, 350, 351
#     ],
#     "Fields/Creative_and_Open-ended_Questions.json": [
#     ],
# }

# History Objective

# classification_filename = {
#     "Fields/Mathematical_Reasoning.json": [],
    # "Fields/Logical_Reasoning.json": [
        # 4, 10, 13, 30, 42, 49, 61, 65, 72, 97, 102, 112, 127, 136, 142, 148, 152, 159, 169, 179, 190, 195, 204, 220, 225, 230, 263, 272, 276, 283, 294, 305, 311, 316, 334, 352],
    # "Fields/Lang_Comp_and_Produc.json": [
    #     0, 1, 2, 3, 6, 11, 12, 14, 20, 21, 23, 26, 32, 43, 44, 45, 46, 50, 53, 54, 55, 56, 58, 64, 68, 69, 77, 84, 85, 88, 89, 96, 98, 104, 107, 116, 118, 120, 122, 125, 128, 137, 138, 146, 149, 150, 155, 162, 165, 166, 170, 174, 175, 185, 188, 196, 203, 204, 208, 213, 215, 221, 224, 235, 247, 256, 257, 267, 269, 273, 276, 279, 281, 287, 289, 290, 295, 298, 310, 322, 328, 330, 333, 346],
    # "Fields/Natural_Science.json": [

    # ],
    # "Fields/Sociocultural_Understanding.json": [
    #     ],
    # "Fields/Data_and_StatisticalLiteracy.json": [
    #     78, 126, 127, 134, 147, 156, 172, 178, 181, 182, 202, 216, 245, 251, 284, 315, 326, 337, 347],
    # "Fields/Commonsense_and_WorldKnowledge.json": [
    #     31, 41, 57, 60, 66, 67, 71, 79, 80, 87, 91, 92, 95, 99, 100, 101, 105, 106, 108, 109, 110, 111, 114, 115, 119, 121, 124, 129, 130, 131, 132, 135, 139, 140, 141, 143, 144, 151, 153, 154, 157, 158, 160, 163, 164, 167, 168, 171, 176, 177, 180, 183, 184, 187, 189, 191, 193, 197, 198, 199, 200, 201, 205, 206, 207, 209, 210, 211, 212, 217, 218, 219, 222, 223, 227, 228, 229, 231, 232, 233, 236, 238, 239, 240, 241, 242, 243, 244, 246, 248, 249, 250, 252, 253, 255, 258, 259, 260, 261, 262, 264, 265, 266, 268, 270, 271, 274, 275, 277, 278, 280, 282, 284, 286, 288, 291, 292, 293, 296, 297, 299, 300, 301, 302, 303, 304, 306, 307, 308, 312, 313, 314, 317, 319, 320, 321, 323, 324, 325, 327, 331, 335, 336, 341, 342, 343, 347, 348, 350, 352, 353, 355],
    # "Fields/Creative_and_Open-ended_Questions.json": []
# }

# Geography Objective

classification_filename = {
    "Fields/Mathematical_Reasoning.json": [],
    "Fields/Logical_Reasoning.json": [
        13],
    "Fields/Lang_Comp_and_Produc.json": [],
    "Fields/Natural_Science.json": [
    ],
    "Fields/Sociocultural_Understanding.json": [
        0, 1, 2, 3, 6, 7, 8, 9, 11, 12, 14, 15, 16, 18, 21, 24, 27, 28, 29, 30, 31, 32, 34, 35, 36, 39, 40],
    "Fields/Data_and_StatisticalLiteracy.json": [
        5, 17, 30, 38],
    "Fields/Commonsense_and_WorldKnowledge.json": [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40],
    "Fields/Creative_and_Open-ended_Questions.json": []
}


# source_file = "ObjectiveProblems/2010-2025_Physics_MCQs.json"   # 题目源文件
# source_file = "ObjectiveProblems/2010-2025_Chemistry_MCQs.json"  
# source_file = "ObjectiveProblems/2010-2025_Biology_MCQs.json"  
# source_file = "ObjectiveProblems/2010-2025_Political_Science_MCQs.json"  
# source_file = "ObjectiveProblems/2010-2025_History_MCQs.json"  
source_file = "../ObjectiveProblems/2010-2025_Geography_MCQs.json"
# -------------------------------
# 1. 读取源 JSON（含 questions 数组）
# -------------------------------
with open(source_file, "r", encoding="utf-8") as f:
    source_data = json.load(f)

source_questions = source_data["questions"]

# 建一个 index → question 映射表
index_map = {q["index"]: q for q in source_questions}

# -------------------------------
# 2. 处理每个分类文件
# -------------------------------
for filename, idx_list in classification_filename.items():

    # # ---- 若目标文件不存在 → 创建空模板 ----
    # if not os.path.exists(filename):
    #     os.makedirs(os.path.dirname(filename), exist_ok=True)
    #     empty_content = {"keywords": "", "questions": []}
    #     with open(filename, "w", encoding="utf-8") as f:
    #         json.dump(empty_content, f, ensure_ascii=False, indent=4)

    # ---- 读取已有文件 ----
    with open(filename, "r", encoding="utf-8") as f:
        target_data = json.load(f)

    # 若不存在 questions 字段，补一个
    if "questions" not in target_data:
        target_data["questions"] = []

    # ---- 根据 index 追加内容 ----
    for idx in idx_list:
        if idx in index_map:
            target_data["questions"].append(index_map[idx])
        else:
            print(f"[警告] 源文件中找不到 index={idx}")

    # ---- 写回文件（不覆盖已有 questions，只是追加） ----
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(target_data, f, ensure_ascii=False, indent=4)

    print(f"已写入：{filename} 追加 {len(idx_list)} 个题目")


