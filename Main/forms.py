from django import forms
from .models import *
from Users.forms import FormSettings
from Users.models import*
from django.contrib.auth.forms import UserCreationForm
from loan.models import*
from Users.models import*
from django.contrib.auth import get_user_model
user = get_user_model()
class userForm(FormSettings):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone','is_email_verified']


class GroupForm(FormSettings):
    class Meta:
        model =  Group
        fields = ['Name','grouptype','loan_interest_rate']


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
        fields = ['name', 'description', 'amount']



class FineForm(FormSettings):
    class Meta:
        model = fine
        fields = ['Full_Name', 'reason', 'amount']



class LoanApplicationForm(FormSettings):    
    class Meta:
        model = Loan
        fields = ['employment_terms', 'security_details', 'amount', 'duration_months']


class UserSelectionForm(forms.Form):
    search_user = forms.CharField(label='Search User', required=False)
    users = forms.ModelMultipleChoiceField(queryset=User.objects.none(), widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(UserSelectionForm, self).__init__(*args, **kwargs)
        self.fields['users'].queryset = User.objects.all()


class PaymentForm(FormSettings):
    class Meta:
        model = Payment
        fields = ['amount_paid']



class GroupEditForm(FormSettings):
    class Meta:
        model =  Group
        fields = ['Name','grouptype','loan_interest_rate','Group_Logo']



#class ApplyForm(FormSettings):
    #class Meta:
        #model = Candidate
        #fields = [ 'position', 'photo',]