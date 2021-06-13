from django.db import models

# Create your models here.
from django.db import models


class Goals(models.Model):
    semester = models.CharField(max_length=50)
    pub_date = models.DateTimeField('date published')
    life = models.CharField(max_length=200)
    interest = models.CharField(max_length=200)
    study = models.CharField(max_length=200)
    uid = models.CharField(max_length=200)
    gid = models.AutoField(max_length=48, primary_key=True)
