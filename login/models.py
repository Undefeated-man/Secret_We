from django.db import models

# Create your models here.
class LoginUser(models.Model):
    name = models.CharField(unique=True, max_length=128)
    password = models.CharField(max_length=256)
    email = models.CharField(primary_key=True, max_length=254)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'login_user'


# Create your models here.
class Track(models.Model):
    tid = models.AutoField(primary_key=True)
    uid = models.CharField(max_length=20)
    time = models.CharField(primary_key=True, max_length=50)
    activity = models.CharField(, max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'login_track'