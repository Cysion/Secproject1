
from django.test import TestCase, Client
from django.urls import reverse

from login.views import LoginView, forgotPasswordView
from login.tools import registerUser
from login.models import User
from tools.crypto import gen_rsa, secret_scrambler


class TestViews(TestCase):

    def setUp(self):
        """ View-test setup """

        # Initialize test-client instance
        self.client= Client()

        # View-URLs
        self.url_Login = reverse('login:Login')
        self.url_Register = reverse('login:Register')
        self.url_Forgot_Password = reverse('login:Forgot-Password')

        # Directly register user
        self.email = 'testmail@gmail.com'
        self.password = 'test_password'
        uid = registerUser(dict(
            email = self.email,
            password = self.password,
            gender = 'male',
            first_name = 'test_first_name',
            last_name = 'test_last_name',
            date_of_birth = '2020-03-28',
            role = 'User'
        ))


    def test_Login_GET(self):
        """ Verifes view base-case for 'Login' """

        response = self.client.get(self.url_Login)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')


    def test_Register_GET(self):
        """ Verifes view base-case for 'Register' """

        response = self.client.get(self.url_Register)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/register.html')


    def test_Forgot_Password_GET(self):
        """ Verifes view base-case for 'Forgot_Password' """

        response = self.client.get(self.url_Forgot_Password)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/forgotpassword.html')


    def test_Login_accepts_valid_user(self):
        """ Verifies user cannot be registered twice """

        response = self.client.post(self.url_Login, {
            'email': self.email,
            'password': self.password
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/userprofile/')


    def test_Login_denies_invalid_user(self):
        """ Verifies view 'Login' rejects invalid logins """

        response = self.client.post(self.url_Login, {
            'email': 'nonexistant_email@gmail.com',
            'password': 'nonexistant_password'
        })

        self.assertEquals(response.status_code, 200)


    def test_Register_valid_user(self):
        """ Verifies view 'Register' registers valid users """

        n_users = User.objects.count()

        response = self.client.post(self.url_Register, {
            'first_name': 'Göran',
            'last_name': 'Västervik',
            'date_of_birth': '2020-03-28',
            'gender': 'male',
            'gender_other': '',
            'email': 'valid_mail.99@hotmail.com',
            'password': 'god',
            'repassword': 'god',
            'agree_terms': 'accept'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/userprofile/backupkey/')
        self.assertEqual(User.objects.count(), n_users + 1)


    def test_Register_duplicate_email(self):
        """ Verifies view 'Register' denies registration of user with existant email """

        n_users = User.objects.count()

        response = self.client.post(self.url_Register, {
            'first_name': 'Karin',
            'last_name': 'Larsson',
            'date_of_birth': '2020-03-28',
            'gender': 'male',
            'gender_other': '',
            'email': self.email,
            'password': 'god',
            'repassword': 'god',
            'agree_terms': 'accept'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), n_users)


    """ Commented out due to lack of time to implement this
    def test_Register_denies_email_with_unicode(self):
        # Verifies view 'Register' denies registration with email including unicode characters

        n_users = User.objects.count()

        response = self.client.post(self.url_Register, {
            'first_name': 'Karin',
            'last_name': 'Larsson',
            'date_of_birth': '2020-03-28',
            'gender': 'male',
            'gender_other': '',
            'email': 'karin_lärson@gmail.com',
            'password': 'god',
            'repassword': 'god',
            'agree_terms': 'accept'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), n_users)
    """


    def test_Register_denies_invalid_characters(self):
        """ Verifies view 'Register' denies registration with email including invalid characters """

        n_users = User.objects.count()

        response = self.client.post(self.url_Register, {
            'first_name': 'Karin',
            'last_name': 'Larsson',
            'date_of_birth': '2020-03-28',
            'gender': 'male',
            'gender_other': '',
            'email': 'karin,larsson@gmail.com',
            'password': 'god',
            'repassword': 'god',
            'agree_terms': 'accept'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), n_users)

        response = self.client.post(self.url_Register, {
            'first_name': 'Karin',
            'last_name': 'Larsson',
            'date_of_birth': '2020-03-28',
            'gender': 'male',
            'gender_other': '',
            'email': 'karin;larsson@gmail.com',
            'password': 'god',
            'repassword': 'god',
            'agree_terms': 'accept'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), n_users)


