import re

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View
from itsdangerous import SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from apps.user.models import User, Address

# from celery_tasks.tasks import send_register_active_mail

"""授权码：REYVECRYOZEZIFKL"""


# Create your views here.

# def register(request):
#     if request.method == 'GET':
#         return render(request, 'register.html')
#     else:
#
#         """进行注册处理"""
#         # 接收数据
#         user_name = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         # 数据校验
#         if not all([user_name, password, email]):
#             return render(request, 'register.html', {'errmsg': '数据不完整'})
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, 'register.html', {'errmsg': '邮箱不合法'})
#         if allow != 'on':
#             return render(request, 'register.html', {'errmsg': '未勾选用户同意协议'})
#         try:
#             user = User.objects.get(username=user_name)
#         except User.DoesNotExist:
#             # 说明可用
#             user = None
#         if user:
#             return render(request, 'register.html', {'errmsg': '用户已存在'})
#
#         # 业务处理
#         # user = User()
#         # user.username = user_name
#         # user.password = password
#         # user.email = email
#         # ...
#         # user.save()
#
#         user = User.objects.create_user(username=user_name, password=password, email=email, )
#         user.is_active = 0
#         user.save()
#         # 返回应答,跳转到首页
#         return redirect(reverse('goods:index'))


class RegisterView(View):
    """注册"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        """进行注册处理"""
        # 接收数据
        user_name = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 数据校验
        if not all([user_name, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱不合法'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '未勾选用户同意协议'})
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            # 说明可用
            user = None
        if user:
            return render(request, 'register.html', {'errmsg': '用户已存在'})

        # 业务处理
        # user = User()
        # user.username = user_name
        # user.password = password
        # user.email = email
        # ...
        # user.save()

        user = User.objects.create_user(username=user_name, password=password, email=email, )
        user.is_active = 0
        user.save()

        # 发送激活邮件 身份加密

        # 加密身份信息 生成激活token
        serializer = Serializer(settings.SECRET_KEY, 300)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf8')
        # print(token)
        # send_register_active_mail.delay(email, user_name, token)
        subject = '天天生鲜欢迎您'
        message = '请点击以下链接来激活账号'
        receiver = [email]
        sender = settings.EMAIL_FROM
        html_message = '<a href = "http://127.0.0.1:8000/user/active/%s" >http://127.0.0.1:8000/user/active/%s</a>' % (
            token, token)
        send_mail(subject=subject, message=message, from_email=sender, recipient_list=receiver,
                  html_message=html_message,
                  fail_silently=False)
        # 返回应答,跳转到首页
        # reverse:url反转，优点：url改动时方便，不会出现批量该地址的问题
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 300)

        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired:
            # 激活链接过期
            return HttpResponse('激活链接已过期')


class LoginView(View):
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 获取登录信息
        user_name = request.POST.get('username')
        password = request.POST.get('pwd')
        # 校验登录信息
        if not all([user_name, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        user = authenticate(request, username=user_name, password=password)
        if user is not None:
            if user.is_active:
                # 记录状态
                login(request=request, user=user)
                next_url = request.GET.get('next', reverse('goods:index'))
                response = redirect(next_url)

                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', user_name, max_age=7 * 24)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {'errmsg': '用户未激活'})
        else:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LogoutView(View):
    def get(self, request):
        logout(request=request)
        return redirect(reverse('user:login'))


# /user
# /user

class UserInfoView(View):
    @method_decorator(login_required(login_url='/user/login'))
    def get(self, request):
        # request.user.is_authenticated
        user = request.user
        try:
            address1 = Address.objects.get(user=user)
        # TODO 查找关于抛出异常类型问题
        except Address.DoesNotExist:
            address1 = None
        return render(request=request, template_name='user_center_info.html',
                      context={'page': 'user', 'address1': address1})


# /user/

class UserOrderView(LoginRequiredMixin, View):
    login_url = '/user/order'

    def get(self, request):
        return render(request=request, template_name='user_center_order.html', context={'page': 'order'})


# /user/

class UserAddressView(LoginRequiredMixin, View):
    login_url = '/user/address'

    def get(self, request):
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None

        return render(request=request, template_name='user_center_site.html',
                      context={'page': 'address', 'address': address})

    def post(self, request):
        # 获取前台数据
        receiver = request.POST.get("receiver")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        tel = request.POST.get("tel")
        # 前台数据校验
        if not all([receiver, addr, zip_code, tel]):
            return render(request, 'user_center_site.html', {'errmsg': '地址信息存在未填数据，请填写完整数据'})
        # 写入数据库
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', tel):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式非法'})
        # 校验地址是否存在默认
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
        except Address.DoesNotExist:
            address = None
        if address is not None:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user, receiver=receiver, addr=addr, zip_code=zip_code,
                               phone=tel, is_default=is_default)

        return redirect(reverse('user:address'))
