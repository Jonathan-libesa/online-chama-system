from django.db import models
from Main.models import *
# Create your models here.


STATUS = (
    (0,"Pending"),
    (1,"Approved"),
    (2,"Rejected"),
    (3,"Paid"),
    (4,"Partially Paid")

 )


class Loantype(models.Model):
    Name = models.CharField(max_length=50, unique=True)
    

    def __str__(self):
        return self.Name





class expenses(models.Model):
	name=models.CharField(max_length=255,null=False)
	description=models.CharField(max_length=700,null=False)
	amount=models.IntegerField(null=False)
	groups = models.ManyToManyField(Group, related_name='expenses', blank=True)
	date=models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.name

class Loan(models.Model):
    groups = models.ForeignKey(Group, related_name='loans', null=True, on_delete=models.SET_NULL)
    member = models.ForeignKey(Members,on_delete=models.SET_NULL,null=True)
    employment_terms = models.CharField(max_length=255)
    security_details = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField()
    loan_status = models.IntegerField(choices=STATUS, default=0)
    date_applied = models.DateTimeField(auto_now_add=True)
    is_fully_paid = models.BooleanField(default=False)  # New field

    class Meta:
        ordering=['-date_applied']

    #def calculate_total_amount(self):
    #if self.groups is None or self.groups.loan_interest_rate is None or self.amount is None or self.duration_months is None:
        #return None 


    def calculate_total_amount(self):
        if self.groups is None or self.groups.loan_interest_rate is None or self.amount is None or self.duration_months is None:
            return None  # or any other appropriate value

        # Assuming the interest is applied monthly
        monthly_interest_rate = self.groups.loan_interest_rate / 100 
        total_amount = self.amount
        for _ in range(self.duration_months):
            total_amount += total_amount * monthly_interest_rate

        return total_amount

    def __str__(self):
        total_amount = self.calculate_total_amount()
        return f"Loan for {self.member.user.username} in {self.groups.Name}. Total amount to be paid: {total_amount}"

    def calculate_remaining_amount(self):
        if self.groups is None or self.groups.loan_interest_rate is None:
            return None  # or any other appropriate value

        monthly_interest_rate = self.groups.loan_interest_rate / 100 
        remaining_amount = self.amount
        for _ in range(self.duration_months):
            remaining_amount += remaining_amount * monthly_interest_rate

        payments = Payment.objects.filter(loan=self)
        total_paid_amount = sum(payment.amount_paid for payment in payments)
        remaining_amount -= total_paid_amount

        return remaining_amount

    def __str__(self):
        remaining_amount = self.calculate_remaining_amount()
        payment_status = self.get_payment_status()

        return f"Loan for {self.member.user.username} in {self.groups.Name}. Remaining amount: {remaining_amount}. Payment Status: {payment_status}"

    # ... (existing code)

    def get_payment_status(self):
        total_amount = self.calculate_total_amount()
        remaining_amount = self.calculate_remaining_amount()

        if remaining_amount <= 0:
            return "Fully Paid"
        elif remaining_amount < total_amount:
            return "Partially Paid"
        else:
            return "Not Paid"

      
    def pay_loan(self, amount_paid):


        payment = Payment(loan=self, amount_paid=amount_paid)
        payment.save()

        # Update the loan status based on the payment
        payment.update_loan_status()

        # Check if the loan is fully paid after the payment
        remaining_amount = self.calculate_remaining_amount()
        if remaining_amount <= 0:
            self.is_fully_paid = True
            self.save()

    #def __str__(self):
        #return f"Loan for {self.member.user.username} in {self.groups.Name}"


   # def# calculate_total_amount(self):
        #interest_amount = (self.amount * self.group.interest_rate * self.duration_months) / 100
        #total_amount = self.amount + interest_amount
        #return total_amount
class Payment(models.Model):
    loan = models.ForeignKey(Loan, null=True, on_delete=models.SET_NULL)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    objects = models.Manager()  # Add this line if not already present

    def __str__(self):
        return f"Payment of {self.amount_paid} made on {self.payment_date} for loan {self.loan}"

    def update_loan_status(self):
        loan = self.loan
        loan_status = loan.loan_status

        remaining_amount = loan.calculate_total_amount() - self.amount_paid

        if remaining_amount <= 0:
            loan_status = 2  # Fully paid
        elif remaining_amount < loan.amount:
            loan_status = 1  # Partially paid
        else:
            loan_status = 0  # Not paid

        loan.loan_status = loan_status
        loan.save()

   





class fine(models.Model):
	Full_Name=models.CharField(max_length=255)
	reason=models.CharField(max_length=255)
	amount=models.IntegerField(null=False)
	groups=models.ManyToManyField(Group, related_name='fine', blank=True)


	def __str__(self):
		return self.Name