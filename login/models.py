from django.db import models

# Create your models here.

class User(models.Model):
    '''
    This is the User model which will have information about the user.
    '''
    UserId = models.IntegerField(primary_key=True)
    Gender_Choices = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    Gender = models.CharField(
        max_length=6,
        choices=Gender_Choices
    )
    FirstName = models.CharField(max_length=64, blank=False)
    LastName = models.CharField(max_length=64, blank=False)
    DateOfBirth = models.DateField(blank=False)
    Email = models.CharField(
        max_length=64,
        blank=False,
    )
    Secret = models.CharField(
        max_length=64,
        blank=False,
    )

class UserLogin(models.Model):
    """
    Stores users hashed password.
    """

    UserId = models.OneToOneField(User, on_delete=models.CASCADE)
    Passhash = models.CharField(max_length=64, blank=False)

class Type(models.Model):
    """
    What type of relationship it is. Example Researcher, friend and family.
    """

    TypeId = models.IntegerField(primary_key=True)
    Description = models.CharField(max_length=16, blank=False)

class Relationsships(models.Model):
    """Relationship connection between two users."""

    RelationsshipsId = models.IntegerField(primary_key=True)
    UserA = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='UserA'
    )
    UserB = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='UserB'
    )
    TypeId = models.ForeignKey(Type, on_delete=models.CASCADE)

class Action(models.Model):
    """
    Is connected to ResearchData.
    The description will contain a descritive message about what a user has
    done.
    """

    ActionId = models.IntegerField(primary_key=True)
    Description = models.CharField(max_length=255)

class ResearchData(models.Model):
    """
    Data researchers should have.
    AnonymityCode = is a code which is generated from data from a users and
    cannot be reversed.
    """

    ResearchDataId = models.IntegerField(primary_key=True)
    ActionId = models.ForeignKey(Action, on_delete=models.CASCADE)
    AnonymityCode = models.CharField(max_length=64)
    Time = models.DateTimeField(auto_now=True)