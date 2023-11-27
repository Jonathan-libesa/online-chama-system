from django import forms
from .models import *
from Users.forms import FormSettings
from Users.models import*
from django.contrib.auth.forms import UserCreationForm
from loan.models import*

class userForm(FormSettings):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone','is_email_verified']


class GroupForm(FormSettings):
    class Meta:
        model =  Group
        fields = ['Name','grouptype']


class MemberForm(FormSettings):
    class Meta:
        model =  Members
        fields = []
    #def clean_member_usernames(self):
        # = self.cleaned_data.get('member_usernames')
        #if member_usernames:
            #return [username.strip() for username in member_usernames.split(',')]
        #return []

class ContributionForm(FormSettings):
    class Meta:
        model = Contribution
        fields = ['amount', 'categories']


class CashForm(FormSettings):
    class Meta:
        model = Cash
        fields = [ 'amount', 'categories']  # Add or remove fields as needed


class ExpensesForm(FormSettings):
    class Meta:
        model = expenses
        fields = ['name', 'description', 'amount',]



#class CandidateForm(FormSettings):
   # class Meta:
        #model = Candidate
        #fields = [ 'User', 'position', 'photo','status',]



#class ApplyForm(FormSettings):
    #class Meta:
        #model = Candidate
        #fields = [ 'position', 'photo',]