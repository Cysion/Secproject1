from django.db import models

# Create your models here.

class ResearchData(models.Model):
    """
    Data researchers should have.
    AnonymityCode = is a code which is generated from data from a users and
    cannot be reversed.
    """

    ResearchDataId = models.AutoField(primary_key=True)
    ActionId = models.CharField(max_length=3)
    AnonId = models.BinaryField(max_length=128)
    Time = models.DateTimeField(auto_now=True)
    Value = models.CharField(max_length=255)
    Role = models.CharField(max_length=16)
