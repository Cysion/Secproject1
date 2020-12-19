
from django.test import TestCase, Client
from django.urls import reverse

from home.views import IndexView, ShowcaseView


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        

    def test_index_GET(self):
        """ Tests index GET-code """

        url_index = reverse('home:index')
        response = self.client.get(url_index)

        self.assertEquals(response.status_code, 200)


    """ Commented out since we are currently working on it
    def test_Showcase_GET(self):
        # Tests Showcase GET-code

        url_Showcase = reverse('home:Showcase')
        response = self.client.get(url_Showcase)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/showcase.html')
    """

