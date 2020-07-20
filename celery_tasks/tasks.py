from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
# 创建对象
app = Celery('celery_tasks', broker='redis://127.0.0.1:6379/3')


# 定义任务函数
# 此处知识点有疑惑
# @app.task
# def send_register_active_mail(to_email, username, token):
#     """发送激活邮件"""
#     # 发邮件 subject:邮件标题
#     subject = '天天生鲜欢迎您'
#     message = '请点击以下链接来激活账号'
#     receiver = [to_email]
#     sender = settings.EMAIL_FROM
#     html_message = '<a href = "http://127.0.0.1:8000/user/active/%s" >http://127.0.0.1:8000/user/active/%s</a>' % (
#         token, token)
#     send_mail(subject=subject, message=message, from_email=sender, recipient_list=receiver,
#               html_message=html_message,
#               fail_silently=False)

