
from django.test import SimpleTestCase
from django.urls import reverse, resolve


class TestUrls(SimpleTestCase):

    def test_contacts_resolves(self):
        """ Asserts that URL for view 'contacts' resolves """

        url = reverse('prepare:contacts')
        self.assertEquals(resolve(url).func, views.ContactView)


    def test_add_memory_resolves(self):
        """ Asserts that URL for view 'add-memory' resolves """

        url = reverse('prepare:add-memory')
        self.assertEquals(resolve(url).func, views.addMemoryView)


    def test_memory_resolves(self):
        """ Asserts that URL for view 'memory' resolves """

        url = reverse('prepare:memory')
        self.assertEquals(resolve(url).func, views.MemoryView)


    def test_menu_page_resolves(self):
        """ Asserts that URL for view 'menu-page' resolves """

        url = reverse('prepare:menu-page')
        self.assertEquals(resolve(url).func, views.MenuView)


    def test_menu_resolves(self):
        """ Asserts that URL for view 'menu' resolves """

        url = reverse('prepare:menu')
        self.assertEquals(resolve(url).func, views.MenuView)


