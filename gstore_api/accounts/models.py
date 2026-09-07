from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, User
from django.utils.translation import gettext_lazy as _
import pyotp
from django.conf import settings

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff = True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(email, first_name, last_name, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    username = models.CharField(unique=True, blank=True, null=True, max_length=24)
    otp_secret = models.CharField(max_length=50, blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    
    objects = CustomUserManager()
    
    def generate_otp(self):
        if not self.otp_secret:
            self.otp_secret = pyotp.random_base32()
            self.save(update_fields=["otp_secret"])
        return pyotp.TOTP(self.otp_secret, digits=6, interval=600).now() 
    
    def verify_otp(self, otp):
        return pyotp.TOTP(self.otp_secret, digits=6, interval=600).verify(otp)    
    
    def email_user(self, subject, message, from_email=settings.DEFAULT_FROM_EMAIL, **kwargs):
        
        """Send an email to this user"""
        from django.core.mail import send_mail
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
    