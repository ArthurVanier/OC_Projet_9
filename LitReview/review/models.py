from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# Create your models here.

class Ticket(models.Model):
    TYPE = 'ticket'
    HAS_REVIEW = False
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    time_created = models.DateTimeField(default=datetime.datetime.now())

    def get_type(self):
        return 'ticket'

class UserFollows(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user')
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL , on_delete=models.CASCADE, related_name='followed_by')
    class Meta:
        unique_together = ('user','followed_user')

class Review(models.Model):
    TYPE = 'review'
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    headline = models.CharField(max_length=128)
    body = models.TextField(max_length=8192,blank=True)
    time_created = models.DateTimeField(default=datetime.datetime.now())