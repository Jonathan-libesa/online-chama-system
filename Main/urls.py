from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
#from.views import PostDetail

urlpatterns = [  
    path('', views.index),
    path('create_group/', views.creategroup, name="add_group"),
    path('dashboard/<int:pk>/',views.dashboard,name="dashboard"),

    path('view_members/<int:group_id>/', views.view_members, name='view_members'),
    path('group_contributions/<int:pk>/', views.group_contributions, name='group_contributions'),
    path('group_cashcollected/<int:pk>/', views.cash_collected, name='cash_collected'),
    path('group_expenses/<int:pk>/',views. expense_view, name='group_expenses'),
    #path('remove_member/<int:member_id>/', views.remove_member, name='remove_member'),

]
