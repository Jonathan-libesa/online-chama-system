

from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
#from.views import PostDetail

urlpatterns = [  
    path('', views.index),
    path('create_group/', views.creategroup, name="add_group"),
    #path('create_groups/', views.reategroup, name="add_groups"),
    path('dashboard/<int:pk>/',views.dashboard,name="dashboard"),

    path('view_members/<int:group_id>/', views.view_members, name='view_members'),
    path('group_contributions/<int:pk>/', views.group_contributions, name='group_contributions'),
    path('group_cashcollected/<int:pk>/', views.cash_collected, name='cash_collected'),
    path('group_expenses/<int:pk>/',views. expense_view, name='group_expenses'),
    path('group/<int:pk>/approved-loans/', views.view_approved_loan, name='view_approved_loans'),
    path('group/<int:pk>/pending-loans/', views.view_pending_loan, name='view_pending_loans'),

    path('group/<int:pk>/fines/',views.create_view_fines, name='group_fines'),


    path('group_paid_loan/<int:pk>/', views.view_Paid_loan, name='loan_paid'),


    path('group_information/<int:pk>/', views.view_Group_info, name='view_Group'),

    path('group/<int:pk>/Loan-Applications/', views.view_Loan_Applications, name='view_Loan_Applications'),
    
    

    path('add_selected_members/<int:group_id>/', views.add_selected_members, name='add_selected_members'),



    path('group_account/<int:pk>/',views.group_accounts,name="accounts"),

    path('set_pin_withdrawal/<int:pk>/', views.create_pin, name="create pin"),

    path('group_contributions_lists/<int:pk>/', views.group_contributions_list, name='group_contribution-list'),

    path('download_excel/<int:pk>/', views.download_excel, name='download_excel'),
]

