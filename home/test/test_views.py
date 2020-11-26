
from django.test import TestCase, Client
from django.urls import reverse

from home.views import IndexView, ShowcaseView


class TestViews(TestCase):

    def setUp(self):
        self.client= Client()

        self.url_index = reverse('home:index')
        self.url_Showcase = reverse('home:Showcase')
        

    def test_index_GET(self):
        response = self.client.get(self.url_index)

        self.assertEquals(response.status_code, 302)


    def test_Showcase_GET(self):
        response = self.client.get(self.url_Showcase)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/showcase.html')


