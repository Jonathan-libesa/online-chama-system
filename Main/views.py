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
    total_pending_loans = loan.objects.filter(groups=groups, loan_status=0).count()

    # Get total approved loans for the group
    total_approved_loans = loan.objects.filter(groups=groups, loan_status=1).count()

    context = {
        'groups': groups,
        'total_members': total_members,
        'total_contribution': total_contribution,
        'total_cash_collected': total_cash_collected,
        'combined_total': combined_total,
        'total_expenses': total_expenses,
        'total_pending_loans': total_pending_loans,
        'total_approved_loans': total_approved_loans,

    }

    return render(request, "loan/Home.html", context)



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

            return redirect('view_members', group_id=group.id)
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
       

    }
    return render(request, "loan/expenses.html", context)


@login_required(login_url='account_login')
def view_approved_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group


    # Get total approved loans for the group
    total_approved_loans = loan.objects.filter(groups=groups, loan_status=1).count()
    approved_loans = loan.objects.filter(groups=groups, loan_status=1)

    context = {
        'groups': groups,
        'total_approved_loans': total_approved_loans,
        'approved_loans': approved_loans,

    }

    return render(request, "loan/loan_approved.html", context)





@login_required(login_url='account_login')
def view_pending_loan(request, pk):
    groups = get_object_or_404(Group, id=pk)
    members = Members.objects.filter(groups=groups)  # Filter members by the specific group

    pending_loans = loan.objects.filter(groups=groups, loan_status=0)
       # Get total pending loans for the group
    total_pending_loans = loan.objects.filter(groups=groups, loan_status=0).count()

    context = {
        'groups': groups,
        'total_pending_loans': total_pending_loans,
        'pending_loans': pending_loans,

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
       

    }
    return render(request, "loan/fine.html", context)


