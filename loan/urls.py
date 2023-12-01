from django.urls import path
from.import views

urlpatterns = [
    #path('',views.homeview,name="home"),
    path('group/<int:pk>/Paid-Loan-Excel/', views.view_Paid_loan_excel, name='paid_loan_excel'),
    path('group/<int:pk>/apply-for-loans/', views.apply_loan, name='apply_loans'),
    path('group/<int:pk>/rejected_loans/', views. view_rejected_loans, name='rejected_loans'),
    path('generate_excel_loan_details/<int:pk>/', views.generate_excel_loan_details, name='generate_excel_loan_details'),
    
    
 ] 