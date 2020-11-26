
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):

    def setUp(self):
        self.client= Client()

        self.url_contacts   = reverse('prepare:contacts')
        self.url_add_memory = reverse('prepare:add-memory')
        self.url_memory     = reverse('prepare:memory')
        self.url_menu_page  = reverse('prepare:menu-page')
        self.url_menu       = reverse('prepare:menu')


    def test_contacts_GET(self):
        response = self.client.get(self.url_contacts)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepare/contacts.html')


    def test_add_memory_GET(self):
        response = self.client.get(self.url_add_memory)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepare/add_memory.html')


    def test_memory_GET(self):
        response = self.client.get(self.url_memory)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepare/memory.html')


    def test_menu_page_GET(self):
        response = self.client.get(self.url_menu_page)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepare/menu.html')


    def test_menu_GET(self):
        response = self.client.get(self.url_menu)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'prepare/menu.html')


