import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import openai
from django.conf import settings
from web.models import ChatMessage
from utils.chatGPT_answer import get_chatgpt_answer



@csrf_exempt  # 仅用于简化测试，线上建议使用 CSRF 保护
def chat_ai(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        if user_message:
            ChatMessage.objects.create(user=request.tracer.user, role='user', content=user_message)
            ai_message=get_chatgpt_answer(user_message)
            ChatMessage.objects.create(user=request.tracer.user, role='gpt', content=ai_message)
            return JsonResponse({'response': ai_message})
    return JsonResponse({'response': '请使用 POST 方法提交消息。'}, status=400)



def chat_page(request):
    messages = ChatMessage.objects.filter(user=request.tracer.user).order_by('timestamp')
    return render(request, 'chat_page.html', {'messages': messages})
