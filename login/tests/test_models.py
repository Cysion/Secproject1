
from django.db import IntegrityError
from django.test import TestCase

from login.models import User, Action, ResearchData
from tools.crypto import gen_rsa, secret_scrambler


class TestModels(TestCase):

    def setUp(self):
        """ Initializing testing environment, creating objects """

        # Initialize fields
        self.gender = u'male'
        self.first_name = u'michael'
        self.last_name = u'scött'
        self.date_of_birth = u'2020-03-28'
        self.email = u'testmail@gmail.com'
        self.role = u'User',
        self.password = u'uper-secret-password'

        self.priv_key = ''
        self.pub_key = ''
        self.sym_key = ''
        self.anon_id = ''

        # 1. Create user with Id
        self.user = User.objects.create(Email = self.email)
        self.user.save()

        # 2. Set RSA keys (dependent on Uid)
        key = gen_rsa(secret_scrambler(self.password, self.user.getUid()))
        self.user.setPubKey(key.publickey().export_key())
        self.pub_key = self.user.getPubkey()
        self.priv_key = key.export_key().decode("utf-8")

        # 3. Generate AnonId (dependent on date of birth)
        self.user.setDateOfBirth(self.date_of_birth)
        self.user.setAnonId(self.priv_key)
        self.anon_id = self.user.getAnonId(self.priv_key)

        """ Uncomment when symmetric crypt-functions has been fixed
        # 4. Generate AES key (dependent on RSA keys)
        self.user.setSymkey()
        #self.sym_key = self.user.getSymKey(self.priv_key.decode("utf-8"))
        self.user.save()
        """

        # 5. Set remaining fields
        self.user.setGender(self.gender)
        self.user.setFirstName(self.first_name)
        self.user.setLastName(self.last_name)
        self.user.setEmail(self.email)
        self.user.setRole(self.role)

        self.assertEqual(User.objects.count(), 1)


    def test_User_fields_is_encrypted(self):
        """ Tests if User fields gets encrypted """

        self.assertEqual(self.user.Email, self.email)
        self.assertEqual(self.user.Role, self.role)
        self.assertEqual(self.user.Pubkey, self.pub_key)

        self.assertNotEqual(self.user.Gender, self.gender)
        self.assertNotEqual(self.user.FirstName, self.first_name)
        self.assertNotEqual(self.user.LastName, self.last_name)
        self.assertNotEqual(self.user.DateOfBirth, self.date_of_birth)
        #self.assertNotEqual(self.user.SymKey, self.sym_key)
        self.assertNotEqual(self.user.AnonId, self.anon_id)


    def test_User_field_is_decrypted(self):
        """ Tests if User fields gets decrypted via User get-functions """

        # Test plain fields
        self.assertEqual(self.user.getUid(), self.user.UserId)
        self.assertEqual(self.user.getEmail(), self.email)
        self.assertEqual(self.user.getRole(), self.role)
        self.assertEqual(self.user.getPubkey(), self.pub_key)

        # Test encrypted fields
        self.assertEqual(self.user.getGender(self.priv_key), self.gender)
        self.assertEqual(self.user.getFirstName(self.priv_key), self.first_name.capitalize())
        self.assertEqual(self.user.getLastName(self.priv_key), self.last_name.capitalize())
        self.assertEqual(self.user.getDateOfBirth(self.priv_key), self.date_of_birth)
        #self.assertEqual(self.user.getSymKey(self.priv_key), self.sym_key)
        self.assertEqual(self.user.getAnonId(self.priv_key), self.anon_id)


    def test_User_allowing_duplicates(self):
        """ Tests if duplicate users can be added """

        try:
            dupelicate_user = User.objects.create(Email = self.email)
        except IntegrityError:
            pass
        else:
            raise IntegrityError("Database allows creation of users with duplicate email")


    def test_Action_ResearchData(self):
        """ Tests basic functionality of object Action and ResearchData """

        # Creating Action-object
        description = "Hello world!"
        action = Action.objects.create(
            Description = description
        )
        self.assertEqual(Action.objects.count(), 1)
        self.assertEqual(action.Description, description)

        # Creating object ResearchData
        research_data = ResearchData.objects.create(
            ActionId = action,
            AnonId = self.user.getAnonId(self.priv_key),
            Time = '2018-02-01'
        )
        self.assertEqual(ResearchData.objects.count(), 1)
        self.assertEqual(research_data.ActionId, action)
        self.assertEqual(research_data.AnonId, self.anon_id)


