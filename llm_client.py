import os
import csv
from dotenv import load_dotenv
from openai import OpenAI

# 读取环境变量
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 初始化 DeepSeek 客户端
client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def load_story_overview(filepath: str = "data/story_overview.md") -> str:
    """加载小说总纲文件"""
    if os.path.exists(filepath):
        with open(filepath, encoding="utf-8") as f:
            return f.read()
    return ""

def load_storyline(filepath: str = "data/storyline.csv", chapter_number: int = 1) -> str:
    """根据章节号加载对应阶段描述"""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            start_ch = int(row["start_chapter"])
            end_ch = int(row["end_chapter"])
            if start_ch <= chapter_number <= end_ch:
                return row["description"]
    return ""

def generate_text(prompt: str, chapter_number: int = 1, model: str = "deepseek-chat") -> str:
    """调用 DeepSeek API 生成文本"""
    overview = load_story_overview()
    storyline = load_storyline(chapter_number=chapter_number)

    if overview or storyline:
        prompt = f"【总纲约束】\n{overview}\n\n【阶段约束】\n{storyline}\n\n{prompt}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个小说写作助手"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def stream_chat(prompt: str, chapter_number: int = 1, model: str = "deepseek-chat"):
    """流式调用 LLM，返回一个迭代器"""
    overview = load_story_overview()
    storyline = load_storyline(chapter_number=chapter_number)

    if overview or storyline:
        prompt = f"【总纲约束】\n{overview}\n\n【阶段约束】\n{storyline}\n\n{prompt}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个小说写作助手"},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )
    for chunk in response:
        piece = getattr(chunk.choices[0].delta, "content", None)
        if piece:
            yield piece
