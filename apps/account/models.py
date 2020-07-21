from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

DUMMY_PROFILE_IMAGE = 'https://3.bp.blogspot.com/-qDc5kIFIhb8/UoJEpGN9DmI/AAAAAAABl1s/BfP6FcBY1R8/s1600/BlueHead.jpg'


class MyAccountManager(BaseUserManager):
	def create_user(self, email, username, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not username:
			raise ValueError('Users must have a username')

		user = self.model(
			email=self.normalize_email(email),
			username=username,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			username=username,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	email 					= models.EmailField(verbose_name="email", max_length=60, unique=True)
	username 				= models.CharField(max_length=30, unique=True)
	date_joined				= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
	last_login				= models.DateTimeField(verbose_name='last login', auto_now=True)
	is_admin				= models.BooleanField(default=False)
	is_active				= models.BooleanField(default=True)
	is_staff				= models.BooleanField(default=False)
	is_superuser			= models.BooleanField(default=False)
	# set many to many relationship with same table (self is shortcut for that)
	# symmetrical is bydefault true, so in case of true if we add relation from (account_id =4, followeing_id =9) then (account_id =9, followeing_id =4) is also added. same case is happened while removing data
	# so that's why we set to false here
	subscribers             = models.ManyToManyField('self', through='AccountSubscriber', symmetrical=False, related_name='related_to')
	 # or we can use `models.ImageField(upload_to='folder relative path')`
	image					= models.CharField(default=DUMMY_PROFILE_IMAGE, max_length=1000)


	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	# For checking permissions. to keep it simple all admin have ALL permissons
	def has_perm(self, perm, obj=None):
		return self.is_admin

	# Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
	def has_module_perms(self, app_label):
		return True


class AccountSubscriber(models.Model):
	# in case of self many to many relation first column become the current object field or we can say source field
	# and second property(following_account) become the target field
	# so we can say that first field here is my_account and second field will automatically become
	# the account i want to follow (target account)
	# to understand this read example code below:
	# `Account.objects.get(pk=1).subscribers.all()`  is equivalent to
	# `AccountSubscriber.objects.filter(current_account=1)`
	# 	and  `Account.objects.get(pk=1).subscribers.get(id=2)` is equivalent to
	# `AccountSubscriber.objects.filter(current_account=1, following_account=2)`

	current_account = models.ForeignKey(Account, related_name='current_account', on_delete=models.CASCADE)
	following_account = models.ForeignKey(Account, related_name='following_account', on_delete=models.CASCADE)