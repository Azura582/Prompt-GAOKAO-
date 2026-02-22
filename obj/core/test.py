from core.benchmark_utils import extract_objective_answer

answer_part = "【答案】C"


answer = extract_objective_answer(answer_part,"single_question_choice")

print(answer)