import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
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






@csrf_exempt  # 测试时使用，生产环境建议使用正常的 CSRF 保护
def human_support(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            print(message)
            if not message:
                return JsonResponse({'response': '请输入有效的问题内容。'}, status=400)
            ChatMessage.objects.create(user=request.tracer.user, role='person', content=message)
            return JsonResponse({'response': '您的请求已收到，我们的人工客服稍后将与您联系。'})
        except Exception as e:
            return JsonResponse({'response': '出现错误，请稍后再试。'}, status=500)
    return JsonResponse({'response': '请使用 POST 方法提交消息。'}, status=405)
