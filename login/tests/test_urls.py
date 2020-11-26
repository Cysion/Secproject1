
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from login.views import LoginView, RegisterView, forgotPasswordView


class TestUrls(SimpleTestCase):

    def test_Login_resolves(self):
        """ Asserts that URL for view 'Login' resolves """

        url = reverse('login:Login')
        self.assertEquals(resolve(url).func, LoginView)


    def test_Register_resolves(self):
        """ Asserts that URL for view 'Register' resolves """

        url = reverse('login:Register')
        self.assertEquals(resolve(url).func, RegisterView)


    def test_ForgotPassword_resolves(self):
        """ Asserts that URL for view 'Forgot-Password' resolves """

        url = reverse('login:Forgot-Password')
        self.assertEquals(resolve(url).func, forgotPasswordView)


