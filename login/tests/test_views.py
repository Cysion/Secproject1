
from django.test import TestCase, Client
from django.urls import reverse

from login.views import RegisterView, LoginView, forgotPasswordView, registerUser
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


    def test_accepts_valid_login(self):
        """ Verifies user cannot be registered twice """

        response = self.client.post(self.url_Login, {
            'email': self.email,
            'password': self.password
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/userprofile/')


    def test_denies_invalid_login(self):
        """ Verifies view 'Login' rejects invalid logins """

        response = self.client.post(self.url_Login, {
            'email': 'nonexistant_email@gmail.com',
            'password': 'nonexistant_password'
        })

        self.assertEquals(response.status_code, 200)



