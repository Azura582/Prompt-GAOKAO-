"""
配置文件
"""

# API配置
API_CONFIG = {
    # OpenAI API (示例)
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "model": "gpt-4"
    },
    
    # Claude API (示例)
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "key": "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "model": "claude-3-sonnet-20240229"
    }
}

# 当前使用的API
CURRENT_API = "openai"  # 可以改为 "claude" 或 "custom"

# 路径配置
PATHS = {
    "subdata": "../reclassData/subdata",
    "results": "../Results",
    "prompt_template": "Sub_Prompt.json",
    "strategy": "strategy.py"
}

# 运行配置
RUN_CONFIG = {
    "max_retries": 3,           # API调用最大重试次数
    "timeout": 60,              # API调用超时时间(秒)
    "sleep_between_calls": 0.5, # API调用间隔(秒)
    "temperature": 0.7,         # 模型温度参数
    "max_tokens": 2000          # 最大生成token数
}