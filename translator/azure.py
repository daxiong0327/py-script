import json
from openai import AzureOpenAI
from typing import List, Optional, Dict, Tuple
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取值
API_KEY = os.getenv('api_key')
API_ENDPOINT = os.getenv('endpoint')
MODEL = os.getenv('model')
VERSION = os.getenv('api_version')

if not API_KEY or not API_ENDPOINT or not MODEL or not VERSION:
    print("缺少必要的环境变量。")
    exit(1)


class AzureMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    @staticmethod
    def from_json_list(json_str: str) -> List['AzureMessage']:
        """
        将 JSON 字符串转换为 Message 对象的列表。
        """
        try:
            data = json.loads(json_str)
            return [AzureMessage(item['role'], item['content']) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON: {e}")
            return []

    @staticmethod
    def to_openai_format(messages: list) -> List[dict[str, str]]:
        """
        将 Message 对象的列表转换为 OpenAI 所需的消息格式。
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]


def chat(messages_str: str) -> Tuple[Optional[dict], Optional[str]]:
    # serialize messages
    messages_list = AzureMessage.from_json_list(messages_str)
    if not messages_list:
        return None, "messages is empty"
    # send request
    client = AzureOpenAI(
        azure_endpoint=API_ENDPOINT,
        api_key=API_KEY,
        api_version=VERSION,
    )

    messages = AzureMessage.to_openai_format(messages_list)
    response = client.chat.completions.create(
        model=MODEL,  # TODO: 暂时只支持gpt-4o
        messages=messages
    )

    # deserialize response
    if not response or not response.choices or not response.choices[0].message:
        return None, "response is empty"
    return {"role": response.choices[0].message.role, "content": response.choices[0].message.content}, None
