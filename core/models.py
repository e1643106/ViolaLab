from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

#zser models 
# für core
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'username'
    objects = CustomUserManager()

    class Meta:
        managed = False
        db_table = 'users'
