from django.urls import path
from.import views

urlpatterns = [
    #path('',views.homeview,name="home"),
    path('group/<int:pk>/Paid-Loan-Excel/', views.view_Paid_loan_excel, name='paid_loan_excel'),
    path('group/<int:pk>/apply-for-loans/', views.apply_loan, name='apply_loans'),
    path('group/<int:pk>/rejected_loans/', views. view_rejected_loans, name='rejected_loans'),
    path('generate_excel_loan_details/<int:pk>/', views.generate_excel_loan_details, name='generate_excel_loan_details'),
    path('group_investment/<int:pk>/',views. investment_view, name='group_investment'),
    # Add a new URL pattern for downloading Excel file
    path('group/<int:group_id>/download_excel/', views.generate_excel_contribution_details, name='download_group_contributions_excel'),
    path('download_loan_payments/<int:pk>/', views.download_payment, name='download_loan_payment'),
    
    
 ] 