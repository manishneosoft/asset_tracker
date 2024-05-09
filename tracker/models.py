from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import uuid
from django.contrib.auth.models import Permission


class Role(models.Model):
    name = models.CharField(max_length=100, 
                            choices=[('system_admin', 'system_admin'), ('seeder', 'seeder')])
    create_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None):
        if not email:
            raise ValueError("Users must have an email address")
        
        user = self.model(
            email=self.normalize_email(email),
            role=role,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, role=None):
        user = self.create_user(
            email=email,
            password=password,
            role=role,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.CharField(max_length=100, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE) 
    create_on = models.DateTimeField(auto_now_add=True,)
    updated_on = models.DateTimeField(auto_now=True,)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email



class SeederPermission(Permission):
    name = 'Can access seeder pages'
    codename = 'seeder_access'

class SysadminPermission(Permission):
    name = 'Can access sysadmin pages'
    codename = 'sysadmin_access'

class AssetType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Asset(models.Model):
    name = models.CharField(max_length=255)
    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE, related_name='assets')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class AssetImage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='assets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for asset: {self.asset.name}"

# Note: You will need to run migrations to create these tables in your database.
# Use the following commands:
# python manage.py makemigrations tracker
# python manage.py migrate

    # @property
    # def is_staff(self):
    #     return self.is_admin

    # def has_perm(self, perm, obj=None):
    #     return self.is_admin

    # def has_module_perms(self, app_label):
    #     return self.is_admin