# AI答题生成器使用说明

## 功能概述

这个程序使用不同的思维策略让AI回答subdata文件夹中的所有问题。

### 核心逻辑

```
外层循环: 10种策略 (CoT, SC, ToT, GoT, ...)
    内层循环: 8个分类文件
        遍历每个问题
            构造提示词 = 模板 + 策略 + 题目
            调用AI API
            保存答案
```

## 文件说明

- **ai_answer_generator.py** - 核心程序，实现所有功能
- **config.py** - 配置文件，管理API密钥和参数
- **run_ai_answer.py** - 快速启动脚本
- **strategy.py** - 10种思维策略定义
- **Sub_Prompt.json** - 8个分类的提示词模板

## 快速开始

### 1. 配置API

编辑 `config.py` 文件：

```python
API_CONFIG = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key": "你的API密钥",  # ← 修改这里
        "model": "gpt-4"
    }
}

CURRENT_API = "openai"  # 使用哪个API
```

### 2. 运行程序

```bash
cd /home/azura/code/python/GAOKAO-Bench-main\ \(Copy\)/Bench
python3 run_ai_answer.py
```

### 3. 查看结果

结果保存在 `Results/` 目录：

```
Results/
├── Strategy_0_CoT/
│   ├── Commonsense&WorldKnowledge.json
│   ├── Creative&Open-ended_Questions.json
│   ├── Data&StatisticalLiteracy.json
│   ├── Lang_Comp&Produc.json
│   ├── LogicalReansoning.json
│   ├── MathematicalReasoning.json
│   ├── Scientific_Inquiry.json
│   └── Socialcultural_Understanding.json
├── Strategy_1_SC/
│   └── ...
└── ...
```

## 输出格式

每个结果文件包含：

```json
{
    "category": "分类名称",
    "strategy": "使用的策略",
    "model_name": "模型名称",
    "example": [
        {
            "index": 0,
            "year": "2023",
            "category": "全国卷",
            "question": "题目内容...",
            "answer": "标准答案",
            "analysis": "题目解析",
            "model_output": "AI的回答",  ← 新增
            "strategy": "CoT",           ← 新增
            "timestamp": "2024-01-11 10:30:00"  ← 新增
        }
    ]
}
```

## 自定义配置

### 修改策略

编辑 `strategy.py`，添加或修改策略：

```python
STRATEGIES = [
    '你的自定义策略1',
    '你的自定义策略2',
    # ...
]
```

### 修改API参数

编辑 `config.py` 中的 `RUN_CONFIG`：

```python
RUN_CONFIG = {
    "max_retries": 3,           # 重试次数
    "timeout": 60,              # 超时时间
    "sleep_between_calls": 0.5, # 调用间隔
    "temperature": 0.7,         # 温度参数
    "max_tokens": 2000          # 最大token
}
```

## 故障排除

### 1. API调用失败

- 检查API密钥是否正确
- 检查网络连接
- 检查API配额是否用完

### 2. 提示词模板找不到

确保 `Sub_Prompt.json` 中的 `keyword` 和 subdata 文件名一致：

```
Sub_Prompt.json 中: "keyword": "Commonsense&WorldKnowledge"
subdata 文件名:      Commonsense&WorldKnowledge.json
```

### 3. 程序运行缓慢

- 减少 `sleep_between_calls` 参数（但可能触发限流）
- 使用更快的API
- 考虑并行处理（需修改代码）

## 进阶功能

### 只运行特定策略

修改 `ai_answer_generator.py`：

```python
def run(self):
    # 只运行前3个策略
    for strategy_idx, strategy in enumerate(self.strategies[:3]):
        # ...
```

### 只处理特定分类

修改 `ai_answer_generator.py`：

```python
def run(self):
    # 只处理数学推理
    category_files = ['MathematicalReasoning.json']
    # ...
```

## 估算时间和成本

假设：
- 8个分类文件
- 每个文件平均100道题
- 10种策略
- 每次API调用0.5秒

**总题目数**: 8 × 100 × 10 = 8000 次API调用  
**预计时间**: 8000 × 0.5秒 = 4000秒 ≈ 1.1小时  
**预计成本** (GPT-4): ~$80-160 (取决于问题长度)

## 联系与支持

如有问题，请检查：
1. API配置是否正确
2. 网络连接是否正常
3. 数据文件格式是否正确