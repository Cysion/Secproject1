from django.test import TestCase
from login.models import User, RelationFrom, RelationTo, Action, ResearchData


class TestModels(TestCase):

    def test_User(self):
        """ Tests valid creations of model 'User' and derivate relations """

        # Testing model: User
        self.valid_User = User.objects.create(
            Gender = bytes('male', 'utf-8'),
            FirstName = bytes('michael', 'utf-8'),
            LastName = bytes('scött', 'utf-8'),
            DateOfBirth = bytes('2020-03-28', 'utf-8'),
            Email = 'testmail@gmail.com',
            Pubkey = 'super-strong-test-key',
            Role = 'User',
            Symkey = 'test-key'
        )
        self.assertEquals(User.objects.count(), 1)
        self.assertEquals(User.objects.filter(UserId=1).first().FirstName, bytes('michael', 'utf-8'))

        # Testing model: RelationFrom
        self.valid_RelationFrom = RelationFrom.objects.create(
            RelationFromId = 42,
            AnonymityIdFrom = 42,
            UserIdTo = self.valid_User,
            Permission = 'car',
            Key = 'this is a superstrong key'
        )
        self.assertEquals(RelationFrom.objects.count(), 1)

        # Testing model: RelationTo
        self.valid_RelationTo = RelationTo.objects.create(
            RelationToId = 42,
            UserIdFrom = self.valid_User,
            AnonymityIdTo = 42,
            Permission = 'car',
            Key = 'this is a superstrong key'
        )
        self.assertEquals(RelationTo.objects.count(), 1)

    def test_Action(self):
        """ Tests valid creations of model 'Action' and ResearchData """

        # Testing model: Action
        self.valid_Action = Action.objects.create(
                ActionId = 42,
                Description = 'Description of action'
        )
        self.assertEquals(Action.objects.count(), 1)

        # Testing model: ResearchData
        self.valid_ResearchData = ResearchData.objects.create(
            ResearchDataId = 42,
            ActionId = self.valid_Action,
            AnonymityCode = 'Anonymity string code here'
        )
        self.assertEquals(ResearchData.objects.count(), 1)


