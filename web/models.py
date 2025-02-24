from django.db import models
from django.conf import settings

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

    def __str__(self):
        return self.username




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
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)




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
    bucket = models.CharField(verbose_name='S3桶', max_length=128, null=True, blank=True)


class ProjectUser(models.Model):
    user=models.ForeignKey(verbose_name='用户', to='UserInfo', related_name='projects', on_delete=models.CASCADE)
    project=models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    star=models.BooleanField(verbose_name='星标', default=False)
    create_datetime = models.DateTimeField(verbose_name='加入时间', auto_now_add=True)




class Wiki(models.Model):
    project=models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    title=models.CharField(verbose_name='标题', max_length=32)
    content=models.TextField(verbose_name='内容')
    parent =models.ForeignKey(verbose_name='父文章', to='Wiki', null=True, blank=True, on_delete=models.CASCADE)
    depth = models.IntegerField(verbose_name='深度', default=1)

    def __str__(self):
        return self.title





class FileRepository(models.Model):
    project=models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    file_type_choices=(
        (1,'文件'),
        (2,'文件夹 '),
    )
    file_type=models.SmallIntegerField(verbose_name='类型',choices=file_type_choices)
    name=models.CharField(verbose_name='文件夹名称', max_length=32, help_text='文件/文件夹名')
    key=models.CharField(verbose_name='文件储存key', max_length=32, unique=True, blank=True, null=True)
    file_size=models.IntegerField(verbose_name='文件大小', null=True, blank=True)
    file_path=models.CharField(verbose_name='文件路径', max_length=256, null=True, blank=True)
    parent=models.ForeignKey(verbose_name='父级目录',to='self',related_name='child', null=True, blank=True, on_delete=models.CASCADE)
    update_user=models.ForeignKey(verbose_name='最近更新者', to='UserInfo',on_delete=models.CASCADE)
    update_datetime=models.DateTimeField(verbose_name='更新时间', auto_now_add=True)





class Module(models.Model):
    project=models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    title=models.CharField(verbose_name='模块名称', max_length=32)
    def __str__(self):
        return self.title






class IssuesType(models.Model):
    PROJECT_INIT_LIST=['任务','功能','Bug']

    colors_choice = (
        (1, '#FFDAB9'),
        (2, '#98F5FF'),
        (3, '#76EEC6'),
        (4, '#CD5C5C'),
        (5, '#9370DB'),
        (6, '#FF7F00'),
    )
    title=models.CharField(verbose_name='类型名称', max_length=32)
    color=models.SmallIntegerField(verbose_name='颜色', choices=colors_choice, default=1)
    project = models.ForeignKey(verbose_name='项目', to='Project',on_delete=models.CASCADE)
    def __str__(self):
        return self.title






class Issues(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    issues_type=models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.CASCADE)
    module=models.ForeignKey(verbose_name='模块', to='module', on_delete=models.CASCADE, null=True, blank=True)
    subject=models.CharField(verbose_name='主题', max_length=80)
    priority_choices=(
        ('danger','高'),
        ('warning','中'),
        ('success','低'),
    )
    priority=models.CharField(verbose_name='优先级', choices=priority_choices, max_length=12,default='danger')
    status_choices=(
        (1,'新建'),
        (2,'处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status=models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    assign=models.ForeignKey(verbose_name='指派',to='UserInfo',on_delete=models.CASCADE,related_name='task')
    mode_choices=(
        (1,'公开模式'),
        (2,'隐私模式')
    )
    mode=models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)
    desc=models.TextField(verbose_name='描述',null=True, blank=True)
    parent=models.ForeignKey(verbose_name='父问题',to='self',related_name='child', null=True, blank=True, on_delete=models.CASCADE)
    creator=models.ForeignKey(verbose_name='创建者', to='UserInfo',on_delete=models.CASCADE)
    end_datetime = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    start_datetime = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    create_datetime=models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    lastest_datetime=models.DateTimeField(verbose_name='最近更新时间',auto_now_add=True)
    attention=models.ManyToManyField(verbose_name='关注者', to='UserInfo',blank=True,related_name='attention')
    def __str__(self):
        return self.subject





class IssueReply(models.Model):

    reply_type_choices=(
        (1,'修改记录'),
        (2,'回复')
    )
    reply_type=models.IntegerField(verbose_name='类型', choices=reply_type_choices)
    issues=models.ForeignKey(verbose_name='问题',to='Issues',on_delete=models.CASCADE)
    content=models.TextField(verbose_name='描述')
    creator=models.ForeignKey(verbose_name='创建者', to='UserInfo',on_delete=models.CASCADE,related_name='create_reply')
    create_datetime=models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    reply=models.ForeignKey(verbose_name='回复',to='self',on_delete=models.CASCADE,null=True,blank=True)






class ProjectInvite(models.Model):
    project = models.ForeignKey(verbose_name='项目', to='Project', on_delete=models.CASCADE)
    code=models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    count=models.PositiveIntegerField(verbose_name='限制数量',null=True,blank=True,help_text='空表示无限制数量')
    use_count=models.PositiveIntegerField(verbose_name='已邀请数量',default=0)
    period_choices=(
        (30,'30分钟'),
        (60,'1小时'),
        (300,'5小时'),
        (1440,'24小时'),
    )
    period=models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', on_delete=models.CASCADE, related_name='invite')
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)








class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ('user', '用户'),
        ('gpt', 'AI客服'),
        ('person', '人工客服'),
    )
    # 如果你使用自定义用户模型，请确保 settings.AUTH_USER_MODEL 已正确配置
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE, verbose_name="用户")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    content = models.TextField(verbose_name="内容")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="时间")

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user} - {self.role} - {self.timestamp}"









class CalendarEvent(models.Model):
    TYPE_CHOICES = (
        ('1', '问题截止'),
        ('2', '自定义事件'),
    )
    user = models.ForeignKey(to=UserInfo, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    issue = models.ForeignKey(to=Issues, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='1')

    def __str__(self):
        return self.title
