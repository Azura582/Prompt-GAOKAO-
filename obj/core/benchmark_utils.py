import codecs
import os
import re
import json
from tqdm import tqdm
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from core.Model import Model

# 文件写入锁
file_write_lock = threading.Lock()

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 指数退避 1s, 2s, 4s...
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type((requests.exceptions.HTTPError, requests.exceptions.Timeout))
)
def rate_limited_request(model, prompt,pictures = None):
    """带重试和退避的API请求"""
    response = model.execute(prompt,pictures)
    if response.status_code == 429:  # Too Many Requests
        raise requests.exceptions.HTTPError("Rate limit exceeded")
    if hasattr(response, 'raise_for_status'):
        response.raise_for_status()  # 抛出其他HTTP错误
    return response


def extract_choices(answer_part):
    """
    从文本中提取选项字母（保序去重）
    """
    found = re.findall("[A-Z]", answer_part)
    result = []
    for c in found:
        result.append(c)
    return result


def extract_objective_answer(model_output, question_type, answer_length=None):
    """
    从模型输出中提取选择题答案。

    预期的模型输出格式：
    'single_choice' (单选题): 答案应为 model_output 中的最后一个大写字母，例如："...【答案】 A <eoa>"
    'multi_question_choice' (组合选择题): "...【答案】A ... 【答案】C ..." 或者在输出开头写下答案，例如 "A C D E F...."
    'multi_choice' (多选题): "...【答案】 ABD " 或者在输出末尾写下答案，例如 "... ACD"
    'five_out_of_seven' (七选五): 答案应为 model_output 中的前五个大写字母，例如 "A C D F B ...."
    """
    model_answer = []
    try:
        # 统一预处理
        content = re.sub(r'\s+', '', model_output)

        # 正则匹配 - 先尝试寻找 【答案】(.*?)<eoa> 格式
        match = re.search(r'【答案】(.*?)<eoa>', content)
        if match:
            answer_part = match.group(1).strip()
        else:
            # 如果没有找到 <eoa> 标记，则尝试寻找 【答案】 后面的内容
            alt_match = re.search(r'【答案】([A-Z\s]+?)(?:\n|$|[^\w\s])', content)
            if alt_match:
                answer_part = alt_match.group(1).strip()
            else:
                answer_part = None

    except Exception as e:
        print(f"解析失败:{e}")
        print(model_output)


    # ===== 选择题 =====
    if question_type == 'single_question_choice':
        choices = extract_choices(answer_part)
        if not choices:
            choices = extract_choices(content[-20:], 'A-Z')

        model_answer = choices

    # ===== 组合选择题（多个单选）=====
    elif question_type == 'multi_question_choice':
        choices = extract_choices(answer_part, 'A-Z')
        if not choices:
            choices = extract_choices(content, 'A-Z')
        if answer_length:
            model_answer = choices[:answer_length]
        else:
            model_answer = choices

    # ===== 七选五 =====
    elif question_type == 'five_out_of_seven':
        choices = extract_choices(content, 'ABCDEFG')
        model_answer = choices[:5]


    return model_answer

def load_questions_from_file(source_file_path:str):
    """
    从文件中加载题目集
    """
    with open(source_file_path, "r",encoding="utf-8") as f:
        data = json.load(f)['questions']
    f.close()

    return data


def to_tackle_questions(data, start_index, end_index, model: Model, general_prompt, field=None, strategy=None, max_workers=3):
    """
    进行题目解答测试，支持断点续传与并发处理
    """
    model_answer_dictlist = []
    
    # 尝试加载现有结果
    result_file_path = None
    if field and strategy:
        strategy_name = strategy['name'] if isinstance(strategy, dict) else strategy
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result_file_path = os.path.join(project_root, "results", model.model_name, field, "Strategy" + strategy_name + ".json")

        if os.path.exists(result_file_path):
            try:
                with open(result_file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    model_answer_dictlist = existing_data.get('questions', [])
                    print(f"找到现有进度，已完成 {len(model_answer_dictlist)} 道题")
            except Exception as e:
                print(f"读取进度文件失败: {e}")

    completed_indices = {item['index'] for item in model_answer_dictlist}

    # 添加速率控制变量
    request_lock = threading.Lock()
    last_request_time = {'time': time.time()}
    request_counter = {'count': 0}

    def process_item(i):
        index = data[i]['index']
        if index in completed_indices:
            return None

        # 请求前等待（保证至少1.5秒间隔）
        with request_lock:
            current_time = time.time()
            elapsed = current_time - last_request_time['time']
            if elapsed < 1.5:
                time.sleep(1.5 - elapsed)
            last_request_time['time'] = time.time()
            request_counter['count'] += 1
            
            # 获取当前线程编号 (简单提取线程名末尾数字)
            thread_name = threading.current_thread().name
            worker_id = thread_name.split('_')[-1] if '_' in thread_name else thread_name
            print(f"\n[线程 {worker_id}] 正在处理题目 {index}...")

        question = data[i]['question'].strip() + '\n'
        year = data[i]['year']
        category = data[i]['category']
        score = data[i]['score']
        standard_answer = data[i]['answer']
        analysis = data[i]['analysis']
        strategy_description = strategy["description"]

        # 图片数据
        pictures = data[i].get('picture', None)
        model_output = None

        full_prompt = f"{general_prompt}\n\n【解题策略】\n{strategy_description}\n\n【题目】\n{question}"

        try:
            # 使用带重试机制的请求
            response = rate_limited_request(model, full_prompt,pictures)
            
            response_data = response.json()
            model_output = response_data["choices"][0]["message"]["content"]
            model_answer = extract_objective_answer(model_output, question_type='single_question_choice')

            if request_counter['count'] % 50 == 0:
                print(f"已发送 {request_counter['count']} 个请求，建议检查配额使用情况")

            print(f"\n[线程 {worker_id}] 题目 {index} 处理完成。")

            return {
                'index': index,
                'year': year,
                'category': category,
                'score': score,
                'question': question,
                'standard_answer': standard_answer,
                'analysis': analysis,
                'model_answer': model_answer,
                'model_output': model_output
            }
        except Exception as e:
            print(f"\n处理题目 {index} 时发生错误: {e}")
            if model_output:
                print(f"模型输出内容: {model_output}")
            return None

    # 执行并发测试
    max_workers = min(max_workers, 3)
    results_batch = []

    # 一次写入量
    BATCH_SIZE = 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_item, i) for i in range(start_index, end_index)]
        
        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                result = future.result()
                if result:
                    results_batch.append(result)
                    # 批量写入，减少IO竞争
                    if len(results_batch) >= BATCH_SIZE and field and strategy:
                        with file_write_lock:
                            model_answer_dictlist.extend(results_batch)
                            write_results_to_file(field, strategy, model, model_answer_dictlist, result_file_path)
                        results_batch = []
            except Exception as e:
                print(f"\n子线程执行异常: {e}")

        # 写入剩余结果
        if results_batch and field and strategy:
            with file_write_lock:
                model_answer_dictlist.extend(results_batch)
                write_results_to_file(field, strategy, model, model_answer_dictlist, result_file_path)

    return model_answer_dictlist


def write_results_to_file(field, strategy, model: Model, model_answer_dictlist,result_file_path):
    model_name = model.model_name
    strategy_name = strategy['name'] if isinstance(strategy, dict) else strategy

    # 确保保存目录存在
    save_directory = os.path.dirname(result_file_path)
    if save_directory and not os.path.exists(save_directory):
        os.makedirs(save_directory)

    output = {
        'field': field,
        'strategy': strategy_name,
        'model_name': model_name,
        'questions': model_answer_dictlist
    }

    with codecs.open(result_file_path, 'w', 'utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
