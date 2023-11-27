from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.



class User(AbstractUser):
	username=models.CharField(unique=True,max_length=100)
	email=models.EmailField(unique=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	phone=models.CharField(max_length=30,null=True,blank=True)
	profile_pic=models.ImageField(default="no_avatar.jpg",null=True,blank=False,upload_to='Users_profile_picture/')
	is_email_verified = models.BooleanField(default=False)



	USERNAME_FIELD='email'

	REQUIRED_FIELDS=['username']

	def __str__(self):
		return self.first_name + "" + self.last_name
 	