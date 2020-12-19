
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from home.views import IndexView, ShowcaseView


class TestUrls(SimpleTestCase):

    def test_index_resolves(self):
        """ Asserts that URL for view 'index' resolves """

        url = reverse('home:index')
        self.assertEquals(resolve(url).func, IndexView)


    def test_Showcase_resolves(self):
        # Asserts that URL for view 'Showcase' resolves

        url = reverse('home:Showcase')
        self.assertEquals(resolve(url).func, ShowcaseView)

