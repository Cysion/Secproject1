
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from login.views import login_view, register_view, forgot_password_view


class TestUrls(SimpleTestCase):

    def test_Login_resolves(self):
        """ Asserts that URL for view 'Login' resolves """

        url = reverse('login:Login')
        self.assertEquals(resolve(url).func, login_view)


    def test_Register_resolves(self):
        """ Asserts that URL for view 'Register' resolves """

        url = reverse('login:Register')
        self.assertEquals(resolve(url).func, register_view)


    def test_ForgotPassword_resolves(self):
        """ Asserts that URL for view 'Forgot-Password' resolves """

        url = reverse('login:Forgot-Password')
        self.assertEquals(resolve(url).func, forgot_password_view)


