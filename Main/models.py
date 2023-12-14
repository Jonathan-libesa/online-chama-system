
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models import CASCADE
from Users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

#from autoslug import AutoSlugField
# Create your models here.
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import make_password, check_password

STATUS = (
    (0,"Pending"),
    (1,"Approved"),
    (2,"Rejected"),
    (3,'Not_received'),
    (4,'Received'),

 )

class Grouptype(models.Model):
    Name = models.CharField(max_length=50, unique=True)
    

    def __str__(self):
        return self.Name



class Group(models.Model):
    Name=models.CharField(max_length=200)
    loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Enter the interest rate as a percentage")
    Chairperson=models.ForeignKey(User,on_delete=models.SET_NULL, null=True,blank=True)
    Group_Logo =models.ImageField(default="no_avatar.jpg",null=False,blank=False,upload_to='Group_Logo_picture/')
    grouptype=models.ForeignKey(Grouptype,on_delete=models.SET_NULL,null=True)
    withdrawal_minimum = models.FloatField(null=True, blank=True)
    withdrawal_maximum = models.FloatField(null=True, blank=True)

    #withdrawal_restriction_amount = models.DecimalField(
        #max_digits=10,
       # decimal_places=2,
        #default=0,
       # help_text="Enter the withdrawal restriction amount for group members",
   # )
    date_created=models.DateTimeField(auto_now_add=True)

    
    # ... (existing methods and fields)


    class Meta:
        ordering=['-date_created']

    def __str__(self):
        return self.Name


#class Members(models.Model):
    #user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    #groups = models.ManyToManyField(Group, related_name='membership')
    #date_created = models.DateTimeField(auto_now_add=True)
    #pin = models.IntegerField( null=True, blank=True)  # Add PIN field
    #account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Members(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group, related_name='membership')
    date_created = models.DateTimeField(auto_now_add=True)
    pin = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1000, message="PIN must be a four-digit number."),
            MaxValueValidator(9999, message="PIN must be a four-digit number."),
        ]
    )

    


    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Groups"
        else:
            return "Unassigned Member"


class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'group')

    #def __str__(self):
        #if self.user is not None:
            #group_names = ", ".join([group.name for group in self.groups.all()])
           # return f"{self.user.username}'s Groups: {group_names}"
        #else:
          #  return "Unassigned Member"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.sender.username} to {self.recipient.username}"

def send_group_message(group, sender, subject, body):
    members = group.members.all()

    for member in members:
        Message.objects.create(
            sender=sender,
            recipient=member.user,
            group=group,
            subject=subject,
            body=body
        )


class Category(models.Model):
    Name=models.CharField(max_length=250)

    def __str__(self):
        return self.Name

class Contribution(models.Model):
    member=models.ForeignKey(Members,on_delete=models.SET_NULL,null=True)
    groups = models.ForeignKey(Group, related_name='contribution', null=True, on_delete=models.SET_NULL)
    amount=models.FloatField(null=False,blank=False)
    categories=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=False)
    date_created=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.amount)


class Cash(models.Model):

    member=models.ForeignKey(Members,on_delete=models.SET_NULL,null=True)
    groups = models.ForeignKey(Group, related_name='cash', null=True, on_delete=models.SET_NULL)
    amount=models.FloatField(null=False,blank=False)
    categories=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=False)
    #cash_status = models.IntegerField(choices=STATUS, default=3)
    date_created=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.amount)


class Withdrawal(models.Model):
    member = models.ForeignKey(Members, on_delete=models.SET_NULL, null=True)
    groups = models.ForeignKey(Group, related_name='withdrawals', null=True, on_delete=models.SET_NULL)
    amount = models.FloatField(null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member} - {self.amount}"
 




class Investment(models.Model):
    groups = models.ManyToManyField(Group, related_name='investment', blank=False)
    Name=models.CharField(max_length=7000,null=False)
    amount=models.IntegerField(null=False)
    Investment_type=models.CharField(max_length=7000,null=False)



    def __str__(self):
        return self.Name
