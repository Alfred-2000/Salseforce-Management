from django.db import models
from datetime import datetime

class DateTimeWithTZField(models.DateTimeField):
    def db_type(self, connection):
        return 'timestamptz'
    
class Users(models.Model):
    user_id = models.UUIDField(primary_key=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.CharField(max_length=256, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)
    is_admin = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)
    updated_at = DateTimeWithTZField(null=True, blank=True)

    def __str__(self):
        return self.username
    
class Notes(models.Model):
    notes_id = models.UUIDField(primary_key=True)
    title = models.TextField(null=True, blank=True, unique=True)
    body = models.TextField(null=True, blank=True)
    user_id = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, blank=True, null=True)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)
    updated_at = DateTimeWithTZField(null=True, blank=True)

    def __str__(self):
        return self.notes_id

class UserToken(models.Model):
    token_id = models.UUIDField(primary_key=True)
    user_id = models.ForeignKey('accounts.Users', on_delete=models.CASCADE, blank=True, null=True)
    created_at = DateTimeWithTZField(default=datetime.now(), null=True, blank=True)