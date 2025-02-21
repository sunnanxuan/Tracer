import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tracer.settings")  # 假设你的 settings 文件在 Tracer 目录下
import django
django.setup()

from openai import OpenAI
from django.conf import settings



def get_chatgpt_answer(question: str, temperature: float = 0.7) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个友好且高效的AI客服，帮助解答用户提出的问题。"},
            {"role": "user", "content": question},
        ],
        temperature=temperature)
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = "抱歉，出现错误，请稍后重试。"
    return answer

