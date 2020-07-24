
from apps.user import views
from django.urls import path
from django.conf.urls import url
from apps.user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserAddressView, LogoutView

urlpatterns = [
    # url(r'^register$', view=views.register, name='register'),
    path(r'register', RegisterView.as_view(), name='register'),
    url(r'active/(?P<token>.*)', ActiveView.as_view(), name='active'),
    path(r'login', LoginView.as_view(), name='login'),
    path(r'logout', LogoutView.as_view(), name='logout'),
    url(r'^info$', UserInfoView.as_view(), name='info'),
    url(r'^order$', UserOrderView.as_view(), name='order'),
    url(r'^address$', UserAddressView.as_view(), name='address')
]
