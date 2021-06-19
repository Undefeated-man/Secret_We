from django.db import models

# Create your models here.
from django.db import models


class Together(models.Model):
    tid = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    describe = models.CharField(max_length=500)
    done = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'goals_together'


class Goals(models.Model):
    gid = models.AutoField(primary_key=True)
    semester = models.CharField(max_length=50)
    pub_date = models.DateField(auto_now_add=True)
    life = models.CharField(max_length=100)
    interest = models.CharField(max_length=100)
    study = models.CharField(max_length=100)
    uid = models.CharField(max_length=100)
    done = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'goals_goals'

