from django.db import models

# Create your models here.

"""
python manage.py makemigrations
python manage.py migrate
"""

class UserInfo(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32,db_index=True)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    mobile_phone = models.CharField(verbose_name='手机号', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=32)



class PricePolicy(models.Model):
    category_choice = (
        (1,'免费版'),
        (2,'收费版'),
        (3,'其他'),
    )
    category=models.SmallIntegerField(verbose_name='收费类型',choices=category_choice,default=2)
    title=models.CharField(verbose_name='标题',max_length=32)
    price=models.PositiveIntegerField(verbose_name='价格')
    project_num=models.PositiveIntegerField(verbose_name='项目数')
    project_member=models.PositiveIntegerField(verbose_name='项目成员数')
    project_space=models.PositiveIntegerField(verbose_name='单项目空间')
    project_file_size= models.PositiveIntegerField(verbose_name='单文件大小（M）')
    create_datetime=models.DateTimeField(verbose_name='创建实际',auto_now_add=True)




class Transaction(models.Model):
    status_choice = (
        (1,'未支付'),
        (2,'已支付')
    )
    status=models.SmallIntegerField(verbose_name='状态',choices=status_choice)
    order=models.CharField(verbose_name='订单号',max_length=64,unique=True)
    user=models.ForeignKey(verbose_name='用户', to='UserInfo',on_delete=models.CASCADE)
    price_policy=models.ForeignKey(verbose_name='价格策略', to='PricePolicy',on_delete=models.CASCADE)
    count=models.IntegerField(verbose_name='数量（年）', help_text='0表示无限期')
    price=models.IntegerField(verbose_name='实际支付价格')
    start_datetime=models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_datetime=models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name='创建实际', auto_now_add=True)




class Project(models.Model):
    colors_choice = (
        (1, '#FFDAB9'),
        (2, '#98F5FF'),
        (3, '#76EEC6'),
        (4, '#CD5C5C'),
        (5, '#9370DB'),
        (6, '#FF7F00'),
    )
    name=models.CharField(verbose_name='项目名', max_length=32)
    color=models.SmallIntegerField(verbose_name='颜色', choices=colors_choice, default=1)
    desc=models.CharField(verbose_name='项目描述', max_length=256, null=True, blank=True)
    use_space=models.IntegerField(verbose_name='项目已使用空间',default=0)
    star=models.BooleanField(verbose_name='星标', default=False)
    join_count=models.SmallIntegerField(verbose_name='参与人数', default=1)
    creator=models.ForeignKey(verbose_name='创建者', to='UserInfo',on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建实际', auto_now_add=True)





class ProjectUser(models.Model):
    user=models.ForeignKey(verbose_name='用户', to='UserInfo', related_name='projects', on_delete=models.CASCADE)
    project=models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    star=models.BooleanField(verbose_name='星标', default=False)
    create_datetime = models.DateTimeField(verbose_name='加入实际', auto_now_add=True)
