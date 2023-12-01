from django.shortcuts import render, reverse, redirect,get_object_or_404
#from voting.models import Voter, Position, Candidate, Votes
from Users.models import User
from Users.forms import*
#from voting.forms import *
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from Users.views import account_login
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
import requests
import json
from Users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from loan.models import*
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from Main.forms import*
import openpyxl
from django.http import HttpResponse
from openpyxl.styles import Font
from django import template
register = template.Library()
from django.utils.timezone import now
#from paypalrestsdk import Payment
import paypalrestsdk
user = get_user_model()
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment, Font

from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

from django.utils.dateformat import format as date_format



@login_required(login_url='account_login')
def view_Paid_loan_excel(request, pk):
    groups = get_object_or_404(Group, id=pk)
    Paid_loans = Loan.objects.filter(groups=groups, loan_status=3)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="{groups.Name}_paid_loans.xlsx"'

   # Create Excel workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Add group name to Excel
    worksheet.merge_cells('A1:F1')
    cell = worksheet['A1']
    cell.value = f'Group: {groups.Name}'
    cell.font = Font(size=18, bold=True)
    cell.alignment = Alignment(horizontal='center')

    # Add headers
    headers = ["Date_Paid", "Full Name", "Period", "Interest Rate/PM", "Borrowed Amount", "Status", "Total Amount"]
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        worksheet[f'{col_letter}2'] = header
        worksheet[f'{col_letter}2'].font = Font(size=14, bold=True)
        worksheet.column_dimensions[col_letter].width = 15  # Adjust column width

    # Add loan details
    for row_num, contribution in enumerate(Paid_loans, 3):
        worksheet.cell(row=row_num, column=1, value=contribution.payment_set.first().payment_date.strftime('%Y-%m-%d'))
        worksheet.cell(row=row_num, column=2, value=f"{contribution.member.user.first_name} {contribution.member.user.last_name}")
        worksheet.cell(row=row_num, column=3, value=contribution.duration_months)
        worksheet.cell(row=row_num, column=4, value=f"{groups.loan_interest_rate}%")
        worksheet.cell(row=row_num, column=5, value=f"{contribution.amount} Ksh")
        worksheet.cell(row=row_num, column=6, value=contribution.get_loan_status_display())
        worksheet.cell(row=row_num, column=7, value=f"{round(contribution.calculate_total_amount(), 2)} Ksh")  # Round to two decimal places

    # Add row for total sum in the center
    total_sum_row = row_num + 1
    total_sum = round(sum(contribution.calculate_total_amount() for contribution in Paid_loans), 2)  # Round the total sum
    worksheet.cell(row=total_sum_row, column=1, value=f'Total Sum:')
    worksheet.merge_cells(start_row=total_sum_row, start_column=1, end_row=total_sum_row, end_column=5)
    worksheet['A' + str(total_sum_row)].alignment = Alignment(horizontal='center', vertical='center')
    worksheet.cell(row=total_sum_row, column=6, value=f'{total_sum} Ksh')  # Use the rounded total sum
    worksheet['F' + str(total_sum_row)].alignment = Alignment(horizontal='center', vertical='center')

    workbook.save(response)
    return response




def get_member_loans_and_total_amount(member_id, group_id):
    # Get the group and member
    groups = get_object_or_404(Group, id=group_id)
    member = get_object_or_404(Members, id=member_id, groups=groups)


    # Get all loans in the group for the specific member
    #loans = Loan.objects.filter(groups=groups, member=member)
    member_loans = Loan.objects.filter(member__id=member_id, groups__id=group_id)

    # Calculate the total amount borrowed by the member
    #total_loans = member_loans.count()
    total_amount_to_return = sum([loan.calculate_total_amount() for loan in member_loans])
    #total_amount_to_return = member_loans.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    #total_borrowed_amount = sum([loan.calculate_total_amount() for loan in loans if loan.calculate_total_amount() is not None])

    # Return the loans and total amount
    return  member_loans , total_amount_to_return

   


@login_required(login_url='account_login')
def apply_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    member = Members.objects.get(user=request.user, groups=groups)
    # Get specific member's loans and total amount
    member_loans, total_member_amount = get_member_loans_and_total_amount(member_id=member.id, group_id=pk)

    # Calculate each member's total loans and total amount to return in the group
    #total_loans, total_amount_to_return = get_member_total_loans_and_amount(member_id=member.id, group_id=pk)
    member_loans , total_amount_to_return = get_member_loans_and_total_amount(member_id=member.id, group_id=pk)
    
    # Calculate the total amount of each loan applied by the member
    total_loan_amounts = {loan.id: loan.calculate_total_amount() for loan in member_loans}

    # Include total amount, remaining amount, and other loan details in the context
    loan_details = []
    for loan in member_loans:
        total_amount_to_return = total_loan_amounts.get(loan.id, 0)
        remaining_amount = max(0, loan.calculate_remaining_amount())
        loan_details.append({
            'loan': loan,
            'total_amount_to_return': total_amount_to_return,
            'remaining_amount': remaining_amount,
            'status_display': loan.get_loan_status_display()
        })
   

    # Include total amount for each loan in the context
    #loan_details = [{'loan': loan, 'total_amount_to_return': total_loan_amounts.get(loan.id, 0)} for loan in member_loans]

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = Members.objects.get(user=request.user)
            loan.groups = groups
            total_amount = loan.calculate_total_amount()
            loan.total_amount = total_amount
             #if not member_loans or any
             #if not member_loans and any
            # Check if the member has no existing loans and if there are any loans with status 3 or 4
            if any(loan.loan_status in [0,2 ] for loan in member_loans):
                messages.warning(request,  'You cannot apply for a new loan while you have a pending or approved loan.')
                return redirect('apply_loans', pk=pk)
            elif any(loan.loan_status in [0, 1] for loan in member_loans):
                messages.warning(request,'You cannot apply for a new loan until your existing loan is fully paid or partially paid.')
                return redirect('apply_loans', pk=pk)
            else:
                loan.save()
                form.save_m2m()
                messages.success(request, f'Loan application submitted successfully! Total loan repayment amount: {total_amount} Ksh')
                return redirect('apply_loans', pk=pk)

        elif payment_form.is_valid():
            amount_paid = payment_form.cleaned_data['amount_paid']
            loan_id = request.POST.get('loan_id')
            loan = get_object_or_404(Loan, id=loan_id)

          # Check if the loan status is approved and partially paid before allowing payment
            if loan.loan_status != 1 and loan.loan_status != 4:
                messages.error(request, 'You can only pay approved and partially paid loans!')
                return redirect('apply_loans', pk=pk)



            # Check if the payment exceeds the total loan amount
            if amount_paid > loan.calculate_total_amount():
                messages.error(request, 'You are paying more than your total loan amount!')
                return redirect('apply_loans', pk=pk)

            # Update the remaining amount based on the payment
            remaining_amount = max(0, loan.calculate_remaining_amount())

            

            # Check if the loan is fully paid or partially paid
            if remaining_amount <= 0:
                loan.loan_status = 4  # Fully paid
                loan.is_fully_paid = True
            else:
                loan.loan_status = 3  # Partially paid
                loan.is_fully_paid = False


            # Check if the loan is fully paid
            if sum(payment.amount_paid for payment in Payment.objects.filter(loan=loan)) + amount_paid >= loan.calculate_total_amount():

                loan.loan_status = 3 
                loan.is_fully_paid = True

            else:
                loan.is_fully_paid = False
                loan.loan_status = 4
           # Save the loan status
          
            loan.save()

            # Record the payment
            Payment.objects.create(loan=loan, amount_paid=amount_paid)
            

            #loan.pay_loan(amount_paid)
            messages.success(request, f'Loan payment of {amount_paid} Ksh successfully processed!')

            # If the loan is fully paid, prevent further payments
            if loan.is_fully_paid:
                messages.warning(request, 'This loan is fully paid. No further payments allowed.')

            return redirect('apply_loans', pk=pk)

    else:
        form = LoanApplicationForm(initial={'groups': groups})
        payment_form = PaymentForm()

    context = {
        'groups': groups,
        'member': member,
        'form': form,
        'member_loans': member_loans,
        'total_amount_to_return': total_amount_to_return,
        'payment_form': payment_form,
        ' total_loan_amounts ': total_loan_amounts, 
        'loan_details': loan_details,
    }

    return render(request, "loan/apply_loan.html", context)




@login_required(login_url='account_login')
def view_rejected_loans(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)

    rejected_loans = Loan.objects.filter(groups=groups, loan_status=2)  # Filter rejected loans
    total_rejected_loans = rejected_loans.count()

    if request.method == 'POST':
        if 'delete_all' in request.POST:
            # Delete all rejected loans
            rejected_loans.delete()
            messages.success(request, 'All rejected loans have been deleted successfully.')
            
        elif 'approve_all' in request.POST:
            # Approve all rejected loans
            for loan in rejected_loans:
                loan.loan_status = 1  # 1 represents approved status, adjust based on your model
                loan.save()
            messages.success(request, 'All rejected loans have been approved successfully.')
        
        elif 'approve_specific' in request.POST:
            # Get the loan ID from the form data
            loan_id = request.POST.get('loan_id')
            # Approve the specific rejected loan
            specific_loan = get_object_or_404(Loan, id=loan_id, groups=groups, loan_status=2)
            specific_loan.loan_status = 1  # 1 represents approved status, adjust based on your model
            specific_loan.save()
            messages.success(request, 'The selected loan has been approved successfully.')

    context = {
        'groups': groups,
        'total_rejected_loans': total_rejected_loans,
        'rejected_loans': rejected_loans,
        'members': members,
    }

    return render(request, "loan/rejected_loans.html", context)







@login_required(login_url='account_login')
def generate_excel_loan_details(request, pk):
    groups = get_object_or_404(Group, id=pk)
    member = Members.objects.get(user=request.user, groups=groups)
     #Get specific member's loans and total amount
    member_loans, total_member_amount = get_member_loans_and_total_amount(member_id=member.id, group_id=pk)
    # Calculate the total amount of each loan applied by the member
    total_loan_amounts = {loan.id: loan.calculate_total_amount() for loan in member_loans}

    # Include total amount, remaining amount, and other loan details in the context
    loan_details = []
    for loan in member_loans:
        total_amount_to_return = total_loan_amounts.get(loan.id, 0)
        remaining_amount = max(0, loan.calculate_remaining_amount())
        loan_details.append({
            'loan': loan,
            'total_amount_to_return': total_amount_to_return,
            'remaining_amount': remaining_amount,
            'status_display': loan.get_loan_status_display()
        })
   
    # Create a new Excel workbook and add a worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active

    # Add header row
    header = [
        "Date of Application",
        "Full Name",
        "Period (Months)",
        "Interest Rate/PM (%)",
        "Borrowed Amount (Ksh)",
        "Status",
        "Total to Return Amount (Ksh)",
        "Remaining Amount (Ksh)",
    ]
    for col_num, header_text in enumerate(header, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = header_text
    # Add data rows
    for row_num, contribution in enumerate(loan_details, 2):
        data = [
            date_format(contribution['loan'].date_applied, 'Y-m-d H:i:s'),
            f"{contribution['loan'].member.user.first_name} {contribution['loan'].member.user.last_name}",
            contribution['loan'].duration_months,
            f"{contribution['loan'].groups.loan_interest_rate}%",
            f"{contribution['loan'].amount}",
            "Paid" if contribution['loan'].is_fully_paid else contribution['loan'].get_loan_status_display(),
            f"{contribution['total_amount_to_return']}",
            f"{contribution['remaining_amount']}",
        ]
        for col_num, cell_value in enumerate(data, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value


    # Create a response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=loan_details_{pk}_{date_format(now(), "YmdHis")}.xlsx'
    workbook.save(response)

    return response

