from django.db import models
from Main.models import *
# Create your models here.


STATUS = (
    (0,"Pending"),
    (1,"Approved"),
    (2,"Rejected"),

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



class loan(models.Model):
	applicant_name=models.CharField(max_length=255)
	members=models.ForeignKey(Members,null=True,on_delete=models.SET_NULL)
	loan_type=models.ForeignKey(Loantype, on_delete=models.CASCADE)
	payment_period=models.CharField(max_length=255)
	employment_terms=models.CharField(max_length=255)
	security_details=models.CharField(max_length=255)
	amount=models.IntegerField(null=False)
	loan_status=models.IntegerField(choices=STATUS,default=0)
	groups = models.ManyToManyField(Group, related_name='loans', blank=True)
	date=models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.applicant_name
 
