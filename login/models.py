from django.db import models

# Create your models here.

class User(models.Model):
    '''
    This is the User model which will have information about the user.
    '''
    UserId = models.AutoField(primary_key=True)
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
        unique=True
    )
    Pubkey = models.CharField(
        max_length=64,
        blank=False,
    )

    Role_Choices = [
        ('User', 'User'),
        ('Caretaker', 'Caretaker'),
        ('Admin', 'Admin')
    ]

    Role = models.CharField(
        max_length=9,
        choices=Role_Choices
    ) # This might not be needed
    Symkey = models.CharField(max_length=256) # This might not be needed

class RelationFrom(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).

    UserIdTo: Friend, Family or therapist user id.
    AnonymityIdFrom: The current user. To see which this user have
    relationsships to.
    Permission: a bit string where 0 says no permission and 1 says
    got permission for each permission entry.
    Key: The public key of the UserIdTo.
    """
    RelationFromId = models.IntegerField(primary_key=True)
    AnonymityIdFrom = models.IntegerField(blank=False)
    UserIdTo = models.ForeignKey(User, on_delete=models.CASCADE)
    Permission = models.CharField(max_length=4)
    Key = models.CharField(max_length=64)

class RelationTo(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).

    UserIdTo: Friend, Family or therapist user id.
    AnonymityIdFrom: The current user. To see which this user have
    relationsships to.
    Permission: a bit string where 0 says no permission and 1 says
    got permission for each permission entry.
    Key: The public key of the AnonymityIdTo.
    """
    RelationToId = models.IntegerField(primary_key=True)
    UserIdFrom = models.ForeignKey(User, on_delete=models.CASCADE)
    AnonymityIdTo = models.IntegerField(blank=False)
    Permission = models.CharField(max_length=4)
    Key = models.CharField(max_length=64)


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
