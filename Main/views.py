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
from.forms import*
from loan.models import*
from django.db.models import Sum
from reportlab.pdfgen import canvas
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import openpyxl
from django.http import HttpResponse
from openpyxl.styles import Font
from django import template
register = template.Library()
#from paypalrestsdk import Payment
import paypalrestsdk
user = get_user_model()


#TO DISPLAY THE HOME PAGE AND THE TEAM OF ZETECH


def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}





@login_required(login_url='account_login')
def creategroup(request):
    #member=Members.objects.get(user=request.user)
    user = request.user
    #member = Members.objects.filter(user=user).first()
    member, created = Members.objects.get_or_create(user=user)
    groups = member.groups.all()
    
    #group=member.groups.all()
    form = GroupForm()
   
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.Chairperson = request.user
            new_group.save()
            member.groups.add(new_group)
            messages.success(request, "New Group Created")
            return redirect('add_group')
        else:
            messages.error(request, "Form errors")
   
    context = {
        'groups': groups,
        'form1': form,
        #'user_groups':user_groups,
    }
    return render(request, "Main/Create_group.html", context)


@login_required(login_url='account_login')
def dashboard(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group
    total_members = members.count()  # Count the total number of members

    # Get cash contributions made by all members of the group
    group_cash_contributions = Cash.objects.filter(groups=groups)
    # Get contributions made by all members of the group
    group_contributions = Contribution.objects.filter(groups=groups)

    # Calculate the total contribution
    total_contribution = group_contributions.aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate the total cash collected
    total_cash_collected = group_cash_contributions.aggregate(Sum('amount'))['amount__sum'] or 0
    # Calculate the combined total amount
    combined_total = total_contribution + total_cash_collected

    # Get all expenses related to the group
    group_expenses = expenses.objects.filter(groups=groups)

    # Calculate the total sum of expenses
    total_expenses = group_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    # Get total pending loans for the group
    total_pending_loans = Loan.objects.filter(groups=groups, loan_status=0).count()

    # Get total approved loans for the group
    total_approved_loans = Loan.objects.filter(groups=groups, loan_status=1).count()
    
    # Get total Paid loans for the group
    Total_paid_loans =Loan.objects.filter(groups=groups,loan_status=3).count()

    # Get all loans in the group
    group_loans = Loan.objects.filter(groups=groups)

    # Calculate the sum of all paid amounts and remaining amount for the group
    total_paid_amount = sum([loan.calculate_total_amount() for loan in group_loans if loan.get_payment_status() == 'Fully Paid'])
    remaining_amount_to_pay = sum([loan.calculate_remaining_amount() for loan in group_loans if loan.get_payment_status() != 'Fully Paid'])
 



    context = {
        'groups': groups,
        'total_members': total_members,
        'total_contribution': total_contribution,
        'total_cash_collected': total_cash_collected,
        'combined_total': combined_total,
        'total_expenses': total_expenses,
        'total_pending_loans': total_pending_loans,
        'total_approved_loans': total_approved_loans,
        'Total_paid_loans':Total_paid_loans,
        'total_paid_amount':total_paid_amount,
        'remaining_amount_to_pay':  remaining_amount_to_pay,
        'members' : members ,

    }

    return render(request, "loan/Home.html", context)


@login_required(login_url='account_login')
def iew_members(request, group_id):
    groups = get_object_or_404(Group, id=group_id)
    members = Members.objects.filter(groups=groups)

    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        user_selection_form = UserSelectionForm(request.POST)

        if user_selection_form.is_valid():
            # Get the selected users
            selected_users = user_selection_form.cleaned_data['users']

            # If there are selected users, add them to the group
            if selected_users:

                Members.objects.create(user=user, groups=groups)
                #groups.members.add(member)

                return redirect('view_members', group_id=groups.id)

        # If no existing users were selected, check if the MemberForm is valid
        if member_form.is_valid():
            # Save the member information
            member = member_form.save(commit=False)

            # Add the member's user to the group
            groups.members.add(member.user)

            return redirect('view_members', group_id=groups.id)
    else:
        member_form = MemberForm()
        user_selection_form = UserSelectionForm()

    context = {
        'groups': groups,
        'member_form': member_form,
        'user_selection_form': user_selection_form,
        'members': members,
    }
    return render(request, "loan/members.html", context)





@login_required(login_url='account_login')
def view_members(request, group_id):
    groups = get_object_or_404(Group, id=group_id)
    members = Members.objects.filter(groups=groups)

    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        user_form = userForm(request.POST)

        if member_form.is_valid() and user_form.is_valid():
            # Save the user information
            user = user_form.save()

            # Save the member information
            member = member_form.save(commit=False)
            member.user = user
            member.save()

            # Add the member to the group
            groups.members.add(member)

            return redirect('view_members', group_id=groups.id)
    else:
        member_form = MemberForm()
        user_form = userForm()

    context = {
        'groups': groups,
        'member_form': member_form,
        'user_form': user_form,
        'members': members,
    }
    return render(request, "loan/members.html", context)




@login_required(login_url='account_login')
def group_contributions(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)
    #contribute=Contribution.objects.filter(members=member)

    member_contributions = []
    for member in members:
        contribute = Contribution.objects.filter(member=member,groups=groups)
        total_contribution = Contribution.objects.filter(member=member).aggregate(Sum('amount'))['amount__sum'] or 0
        member_contributions.append({'member': member, 'total_contribution': total_contribution})

  

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = Members.objects.get(user=request.user)
            contribution.groups=groups
            contribution.save()
            form.save_m2m()
            return render(request,"loan/Make_contribution.html",{' member_contributions': member_contributions,'groups': groups} )
    else:
        form = ContributionForm()

    context = {
        'groups': groups,
        'member_contributions': member_contributions,
        'contribution_form': form,
        'members' : members ,
    }

    return render(request, "loan/Contribution.html", context)





@login_required(login_url='account_login')
def cash_collected(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)

    # Get cash collected by all members of the group
    group_cash = Cash.objects.filter(member__in=members,groups=groups)
    if request.method == 'POST':
        form = CashForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = Members.objects.get(user=request.user)
            contribution.groups = groups
            contribution.save()
            form.save_m2m()
            messages.success(request, "Cash added successfully")
            return redirect( 'cash_collected',pk=pk)
        else:
            messages.error(request, "Form errors")
           
    else:
        form =CashForm()

    # Create a list to store member-wise totals
    member_totals = []

    # Calculate the total cash collected for each member and add to the list
    for member in members:
        member_cash = group_cash.filter(member=member)
        member_total_cash = member_cash.aggregate(Sum('amount'))['amount__sum'] or 0
        member_totals.append({'member': member,'total_cash': member_total_cash,})

    # Calculate the total cash collected for the entire group
    total_cash = group_cash.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'groups': groups,
        'members': member_totals,  # Pass the member-wise totals to the template
        'total_cash': total_cash,
        'contribution_form': form,
        'members' : members ,
        'member_totals':member_totals,
    }

    return render(request, "loan/cash_collected.html", context)



@login_required(login_url='account_login')
def expense_view(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group
    total_members = members.count()  # Count the total number of members

    # Get all expenses related to the group
    group_expenses = expenses.objects.filter(groups=groups)

    if request.method == 'POST':
        form = ExpensesForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            #contribution.groups.set([groups])
            #contribution.groups= Group.objects.get(groups=groups)
            contribution.save()
             # Make sure to save the instance before adding the group
            form.save_m2m()  

            contribution.groups.set([groups]) 
            messages.success(request, "Group expense added successfully")
            return redirect( 'group_expenses',pk=pk)
        else:
            messages.error(request, "Form errors")
           
    else:
        form =ExpensesForm()

    # Calculate the total sum of expenses
    total_expenses = group_expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'groups': groups,
        'total_expenses': total_expenses,
        'group_expenses':group_expenses,
        'contribution_form': form,
        'members' : members ,
       

    }
    return render(request, "loan/expenses.html", context)


@login_required(login_url='account_login')
def view_approved_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group


    # Get total approved loans for the group
    total_approved_loans = Loan.objects.filter(groups=groups, loan_status=1).count()
    approved_loans = Loan.objects.filter(groups=groups, loan_status=1)

    context = {
        'groups': groups,
        'total_approved_loans': total_approved_loans,
        'approved_loans': approved_loans,
        'members' : members ,

    }

    return render(request, "loan/loan_approved.html", context)





@login_required(login_url='account_login')
def view_pending_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group

    pending_loans = Loan.objects.filter(groups=groups, loan_status=0)
       # Get total pending loans for the group
    total_pending_loans = Loan.objects.filter(groups=groups, loan_status=0).count()

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        new_status = request.POST.get('new_status')
        
        loan = get_object_or_404(Loan, id=loan_id, groups=groups, loan_status=0)

        if request.user == groups.Chairperson:
            # Update the loan status based on the button clicked
            if new_status == 'approved':
                loan.loan_status = 1  # 1 represents approved status, adjust based on your model
                messages.success(request, 'The Loan is  has been approved successfully.')
            elif new_status == 'rejected':
                loan.loan_status = 2  # 2 represents rejected status, adjust based on your model
                messages.success(request, 'The Loan is  has been disapproved successfully.')
            loan.save()


    context = {
        'groups': groups,
        'total_pending_loans': total_pending_loans,
        'pending_loans': pending_loans,
        'members' : members ,

    }

    return render(request, "loan/loan_pending.html", context)



@login_required(login_url='account_login')
def create_view_fines(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group
    fines = fine.objects.filter(groups=groups)

    if request.method == 'POST':
        form = FineForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            #contribution.groups.set([groups])
            #contribution.groups= Group.objects.get(groups=groups)
            contribution.save()
             # Make sure to save the instance before adding the group
            form.save_m2m()  

            contribution.groups.set([groups]) 
            messages.success(request, "Group Fine added successfully")
            return redirect( 'group_fines',pk=pk)
        else:
            messages.error(request, "Form errors")
           
    else:
        form =FineForm()

    total_fines = fines.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'groups': groups,
        'fines':fines,
        'contribution_form': form,
        'total_fines':total_fines,
        'members' : members ,
       

    }
    return render(request, "loan/fine.html", context)




@login_required(login_url='account_login')
def view_Paid_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group

    # Get all fully paid loans for the group
    Paid_loans = Loan.objects.filter(groups=groups, loan_status=3)

    total_amount_group = sum([loan.calculate_total_amount() for loan in Paid_loans])
    total_loan_amounts = {loan.id: loan.calculate_total_amount() for loan in  Paid_loans }

    # Create a dictionary to store loan ids and their corresponding total amounts
    loan_details = []

    for loan in Paid_loans:
        total_amount_to_return=total_loan_amounts.get(loan.id, 0)
        loan_details.append({
            'loan':loan,
            'total_amount_to_return':total_amount_to_return,
            'status_display': loan.get_loan_status_display(),

            })


    context = {
        'groups': groups,
        'Paid_loans': Paid_loans,
        'members': members,
        'loan_details':loan_details,
    }

    return render(request, "loan/paid_loan.html", context)





@login_required(login_url='account_login')
def view_Group_info(request, pk):
    groups= get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)

    if request.method == 'POST':
        form = GroupEditForm(request.POST,request.FILES, instance=groups)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your Group Profile has been updated successfully.')
            return redirect('view_Group', pk=pk)
        else:
            messages.error(request, 'There was an error updating your Group Profile. Please correct the errors below.')
    else:
        form = GroupEditForm(instance=groups)

    context = {
        'groups': groups,
        'members': members,
        'form': form,
    }

    return render(request, 'loan/group_information.html', context)






@login_required(login_url='account_login')
def view_Loan_Applications(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)

    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        new_status = request.POST.get('new_status')
        
        loan = get_object_or_404(Loan, id=loan_id, groups=groups, loan_status=0)

        if request.user == groups.Chairperson:
            # Update the loan status based on the button clicked
            if new_status == 'approved':
                loan.loan_status = 1  # 1 represents approved status, adjust based on your model
                messages.success(request, 'The Loan is  has been approved successfully.')
            elif new_status == 'rejected':
                loan.loan_status = 2  # 2 represents rejected status, adjust based on your model
                messages.success(request, 'The Loan is  has been disapproved successfully.')
            loan.save()

    pending_loans = Loan.objects.filter(groups=groups, loan_status=0)
    total_pending_loans = Loan.objects.filter(groups=groups, loan_status=0).count()

    context = {
        'groups': groups,
        'total_pending_loans': total_pending_loans,
        'pending_loans': pending_loans,
        'members': members,
    }
    if 'download_excel' in request.GET:
        # Generate Excel
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{groups.Name}_loan_applications.xlsx"'

        # Create Excel workbook and add a worksheet
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Add group name to Excel
        worksheet.merge_cells('A1:E1')
        cell = worksheet['A1']
        cell.value = f'Group: {groups.Name}'
        cell.font = Font(size=14, bold=True)
        cell.alignment = openpyxl.styles.Alignment(horizontal='center')

        # Create header row
        header_row = ["Date Applied", "Full Name", "Period of Payment", "Loan Status", "Borrowed Amount (Ksh)"]
        worksheet.append(header_row)

        # Add loan information to Excel
        for loan in pending_loans:
            row = [str(loan.date_applied), f"{loan.member.user.first_name} {loan.member.user.last_name}",
                   str(loan.duration_months), loan.get_loan_status_display(), str(loan.amount)]
            worksheet.append(row)

        # Save the workbook to the response
        workbook.save(response)

        return response

    return render(request, "loan/group_loan_applications.html", context)

    

# ...

# Add a new view to process PayPal payments
def process_paypal_payment(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        amount_paid = request.POST.get('amount_paid')
        paypal_order_id = request.POST.get('paypal_order_id')

        loan = get_object_or_404(Loan, id=loan_id)

        # Perform necessary checks before processing the payment

        # Save the payment details to the Payment model
        Payment.objects.create(
            loan=loan,
            amount_paid=amount_paid,
            paypal_order_id=paypal_order_id,
        )

        # Optionally, update the loan status based on the payment

        messages.success(request, 'Payment successful!')
        return redirect('apply_loans')  # Adjust the URL name accordingly
    else:
        messages.error(request, 'Invalid request method')
        return redirect('apply_loans')  # Adjust the URL name accordingly
