from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class CommunityPost(models.Model):

    bullet_point = models.CharField(max_length = 50)
    post_title   = models.TextField(max_length = 200)
    
    author       = models.ForeignKey(User, on_delete = models.CASCADE)