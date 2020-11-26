
from django.test import TestCase, Client
from django.urls import reverse

from login.views import RegisterView, LoginView, forgotPasswordView


class TestViews(TestCase):

    def setUp(self):
        self.client= Client()

        self.url_Login = reverse('login:Login')
        self.url_Register = reverse('login:Register')
        self.url_Forgot_Password = reverse('login:Forgot-Password')
        

    def test_Login_GET(self):
        response = self.client.get(self.url_Login)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/login.html')


    def test_Register_GET(self):
        response = self.client.get(self.url_Register)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/register.html')


    def test_Forgot_Password_GET(self):
        response = self.client.get(self.url_Forgot_Password)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/forgotpassword.html')


