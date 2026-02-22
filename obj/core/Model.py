# -*- coding: utf-8 -*-
import json

import requests
import base64

import time
from PIL import Image
import io

from random import choice
from typing import List

from pyexpat.errors import messages


class Model:
    def __init__(self, api_key, base_url, model_name, temperature):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.url = base_url

    def encode_image(self, image_path):
        with Image.open(image_path) as img:
            # 1. 缩小尺寸：限制最大宽度为 1024 像素
            max_width = 1024
            if img.width > max_width:
                height = int(max_width * img.height / img.width)
                img = img.resize((max_width, height), Image.Resampling.LANCZOS)

            # 2. 颜色量化：将图片转换为 256 色的调色板模式 (P模式)
            # 这对 PNG 压缩非常有效，且对文字/图表类题目清晰度影响极小
            img = img.convert('P', palette=Image.ADAPTIVE)

            byte_arr = io.BytesIO()
            # 3. 启用优化压缩
            img.save(byte_arr, format='PNG', optimize=True)
            return base64.b64encode(byte_arr.getvalue()).decode('utf-8')

    def execute(self, full_prompt,pictures = None):

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        user_content = full_prompt

        if pictures :
            full_prompt += "【题目图片】:"
            # 构造符合 MaaS 接口要求的消息内容列表
            user_content = [
                {
                    "type": "text",
                    "text": full_prompt
                }
            ]


            for pict in pictures:
                user_content.append(
                    {
                    "type": "image_url",
                    "image_url":
                        {
                            "url": f"data:image/png;base64,{self.encode_image(pict)}"
                        }
                    }
                )

        while True:
            try:
                data = {
                    "model": f"{self.model_name}",  # model参数
                    "temperature": self.temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_content
                        }
                    ]
                }

                response = requests.post(self.url, headers=headers, data=json.dumps(data), verify=True)

                break

            except Exception as e:
                print('Exception:', e)
                time.sleep(1)
                continue

        return response






