from django.db import models
from django.db.models import CASCADE
from Users.models import User
#from autoslug import AutoSlugField
# Create your models here.



STATUS = (
    (0,"Pending"),
    (1,"Approved"),
    (2,"Rejected"),

 )

class Grouptype(models.Model):
    Name = models.CharField(max_length=50, unique=True)
    

    def __str__(self):
        return self.Name



class Group(models.Model):
    Name=models.CharField(max_length=200)
    Chairperson=models.ForeignKey(User,on_delete=models.SET_NULL, null=True,blank=True)
    grouptype=models.ForeignKey(Grouptype,on_delete=models.SET_NULL,null=True)
    date_created=models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering=['-date_created']

    def __str__(self):
        return self.Name


class Members(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    groups = models.ManyToManyField(Group, related_name='members')
    date_created = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        if self.user:
            return f"{self.user.username}'s Groups"
        else:
            return "Unassigned Member"



    #def __str__(self):
        #if self.user is not None:
            #group_names = ", ".join([group.name for group in self.groups.all()])
           # return f"{self.user.username}'s Groups: {group_names}"
        #else:
          #  return "Unassigned Member"




   
  

class Category(models.Model):
    Name=models.CharField(max_length=250)

    def __str__(self):
        return self.Name

class Contribution(models.Model):
    member=models.ForeignKey(Members,on_delete=models.SET_NULL,null=True)
    amount=models.FloatField(null=False,blank=False)
    categories=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=False)
    date_created=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.amount)


class Cash(models.Model):

    member=models.ForeignKey(Members,on_delete=models.SET_NULL,null=True)
    #Name =models.CharField(max_length=300)
    amount=models.FloatField(null=False,blank=False)
    categories=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=False)
    date_created=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.amount)




