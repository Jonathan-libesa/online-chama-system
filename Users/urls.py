from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from.views import CompletePasswordReset,RequestPasswordReset

urlpatterns = [
    path('', views.account_login, name="account_login"),
    path('register/', views.account_register, name="account_register"),
    path('logout/', views.account_logout, name="account_logout"),
    #path('profile_view_user', views.profile_view_user, name="user_profile"),
    path('activate-user/<uidb64>/<token>',views.activate_user, name='activate'),
    path('request-password-reset-link/',RequestPasswordReset.as_view(),name="request-password"),
    path('set-new-password/<uidb64>/<token>',CompletePasswordReset.as_view(), name='reset-user-password'),
]


   

    