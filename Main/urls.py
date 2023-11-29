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
    path('group/<int:pk>/approved-loans/', views.view_approved_loan, name='view_approved_loans'),
    path('group/<int:pk>/pending-loans/', views.view_pending_loan, name='view_pending_loans'),

    path('group/<int:pk>/fines/',views.create_view_fines, name='group_fines'),

    path('group/<int:pk>/apply-for-loans/', views.apply_loan, name='apply_loans'),
    #path('process_payment/<int:loan_id>/', views.process_payment, name='process_payment'),
    #path('pay_loan/<int:loan_id>/',views.pay_loan, name='pay_loan'),


    path('group_paid_loan/<int:pk>/', views.view_Paid_loan, name='loan_paid'),
    

    #path('remove_member/<int:member_id>/', views.remove_member, name='remove_member'),

]

