import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from web.models import PricePolicy, Transaction


# 如果使用自定义用户模型，请确保 settings.AUTH_USER_MODEL 配置正确


def purchase_policy(request, policy_id):
    try:
        policy = PricePolicy.objects.get(id=policy_id)
    except PricePolicy.DoesNotExist:
        return JsonResponse({'status': False, 'error': '价格策略不存在。'})

    if request.method == 'GET':
        # 显示购买页面，展示套餐详细信息
        return render(request, 'purchase_policy.html', {'policy': policy})

    elif request.method == 'POST':
        # 获取购买年数，0 表示无限期
        count = request.POST.get('count', '1').strip()
        try:
            count = int(count)
        except ValueError:
            count = 1
        # 模拟支付成功，生成订单号并创建交易记录
        order_id = str(uuid.uuid4())
        price = policy.price  # 价格直接从策略中读取（收费版）
        now = timezone.now()
        if count == 0:
            end_datetime = None  # 无限期
        else:
            # 例如一年为365天
            end_datetime = now + timezone.timedelta(days=365 * count)

        Transaction.objects.create(
            status=2,  # 2 表示已支付
            order=order_id,
            user=request.tracer.user,
            price_policy=policy,
            count=count,
            price=price,
            start_datetime=now,
            end_datetime=end_datetime,
        )
        # 此处你可以更新用户的套餐信息或额度记录
        # 最后返回支付成功页面或直接跳转到项目列表等
        return render(request, 'purchase_success.html', {'policy': policy, 'count': count, 'order_id': order_id})

    return JsonResponse({'status': False, 'error': '不支持的方法'}, status=405)
