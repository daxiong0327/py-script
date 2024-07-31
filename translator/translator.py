from langdetect import detect
from typing import Optional
from azure import chat, AzureMessage
import json


def read_role_card() -> str:
    try:
        with open('role_card.md', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading role card: {e}")
        return ""


class TranslatorInput:
    def __init__(self, input: str):
        self.input = input

    def llm_input(self) -> str:
        # 读入角色信息
        role_card_content = read_role_card()
        if role_card_content == "":
            print("无法读入角色卡片。")
            return ""
        system_message = AzureMessage("system", role_card_content)
        messages = [system_message, AzureMessage("user", self.input)]
        return json.dumps(AzureMessage.to_openai_format(messages))


class WordExplanation:
    def __init__(self, word: str, phonetic: str, chinese: str, phrases: str):
        self.word = word
        self.phonetic = phonetic
        self.chinese = chinese
        self.phrases = phrases

    # @staticmethod
    # def from_json_t_explanation(json_str: str) -> 'WordExplanation':
    #     try:
    #         data = json.loads(json_str)
    #         return WordExplanation(data['word'], data['phonetic'], data['chinese'], data['phrases'])
    #     except (json.JSONDecodeError, KeyError) as e:
    #         print(f"Error parsing JSON: {e}")
    #         return WordExplanation("", "", "", "")


result_test = """{
  "output": "女孩",
  "word_explanation": [
    {
      "word":"girl",
      "phonetic": "/ɡɜːrl/",
      "chinese": "女孩",
      "phrases":"little girl (小女孩), school girl (女学生)"
    }
  ]
}"""


class TranslatorResult:
    def __init__(self):
        self.output: Optional[str] = None
        self.word_explanation: Optional[list[WordExplanation]] = None

    @staticmethod
    def from_json_t_result(json_str: str) -> Optional['TranslatorResult']:
        try:
            data = json.loads(json_str)
            if data['output'] is None:
                return TranslatorResult()
            result = TranslatorResult()
            result.output = data['output']
            if data.get('word_explanation') is not None:
                if isinstance(data['word_explanation'], list):
                    for item in data['word_explanation']:
                        ex_word = WordExplanation(item['word'], item['phonetic'], item['chinese'], item['phrases'])
                        result.word_explanation = result.word_explanation or []
                        result.word_explanation.append(ex_word)

            return result
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing JSON: {e}")
            return None

    @staticmethod
    def to_json_t_result(res: 'TranslatorResult') -> str:
        if res.word_explanation is not None:
            word_explanations = [we.__dict__ for we in res.word_explanation]
        else:
            word_explanations = None
        return json.dumps({
            'output': res.output,
            'word_explanation': word_explanations
        }, ensure_ascii=False, indent=2)


def analyze_input(text: str) -> Optional[str]:
    input_info: str = text[2:]
    print(detect(input_info))
    #if detect(input_info) not in ['zh-cn', 'zh-tw', 'en', 'tr']:
    #    print("无效的输入，请重新输入。")
    #    return None

    t_input = TranslatorInput(input_info)
    input_info = t_input.llm_input()
    if input_info == "":
        return None

    res_info, err = chat(input_info)
    if err is not None:
        print(err)
        return None

    return res_info.get('content')


def main():
    print("欢迎使用中英文翻译程序！")
    print("输入'q>'退出程序。")
    print('输入时需要输入标记字符":",后接目标语言（zh或en）。')
    print('添加陌生单词到笔记本时，输入":w count_number",')
    print('\n----------------------------------------')
    while True:
        text = input("input：")
        print('\n***************************************')
        if text.lower() == 'q>':
            break
        if len(text) < 2:
            print("无效的输入，请重新输入。")
            continue
        mark = text[:2]
        if mark != 'I>' and mark != 'W>':
            print("无效的输入，请重新输入。")
            continue

        if mark == 'W>':
            # TODO: add word to notebook
            pass
            continue
        res = analyze_input(text)
        if res is None:
            continue
        result = TranslatorResult.from_json_t_result(res)
        if result is None:
            continue
        print(result.to_json_t_result(result))
        print('\n----------------------------------------')


if __name__ == "__main__":
    main()
