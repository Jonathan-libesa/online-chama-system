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
    group_cash_contributions = Cash.objects.filter(member__in=members)
    # Get contributions made by all members of the group
    group_contributions = Contribution.objects.filter(member__in=members)

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
        contribute = Contribution.objects.filter(member=member)
        total_contribution = Contribution.objects.filter(member=member).aggregate(Sum('amount'))['amount__sum'] or 0
        member_contributions.append({'member': member, 'total_contribution': total_contribution})

  

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = Members.objects.get(user=request.user)
            contribution.save()
            return render(request,"loan/Make_contribution.html",{'contribute':contribute,'groups': groups} )
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
    group_cash = Cash.objects.filter(member__in=members)
    if request.method == 'POST':
        form = CashForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.member = Members.objects.get(user=request.user)
            contribution.save()
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





def process_payment(request,loan_id):
    # Process payment and update loan status here
    loan_id = request.POST.get('loan_id')
    payment_id = request.POST.get('payment_id')
    amount_paid = request.POST.get('amount_paid')

    # Perform necessary actions (e.g., update loan status, record payment in the database)

    return JsonResponse({'status': 'success'})



@login_required(login_url='account_login')
def view_pending_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group

    pending_loans = Loan.objects.filter(groups=groups, loan_status=0)
       # Get total pending loans for the group
    total_pending_loans = Loan.objects.filter(groups=groups, loan_status=0).count()

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


    # Get total approved loans for the group
    Total_paid_loans = Loan.objects.filter(groups=groups, loan_status=3).count()
    Paid_loans = Loan.objects.filter(groups=groups, loan_status=3)

    total_amount_to_return = sum([loan.calculate_total_amount() for loan in Paid_loans])

    context = {
        'groups': groups,
        'Total_paid_loans': Total_paid_loans,
        'Paid_loans': Paid_loans,
        'members' : members ,
        'total_amount_to_return': total_amount_to_return,

    }

    return render(request, "loan/paid_loan.html", context)
