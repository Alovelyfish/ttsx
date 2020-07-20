
from apps.user import views
from django.urls import path
from django.conf.urls import url
from apps.user.views import RegisterView, ActiveView, LoginView

urlpatterns = [
    # url(r'^register$', view=views.register, name='register'),
    path(r'register', RegisterView.as_view(), name='register'),
    url(r'active/(?P<token>.*)', ActiveView.as_view(), name='active'),
    path(r'login', LoginView.as_view(), name='login')
]
