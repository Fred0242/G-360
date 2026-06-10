from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class DashboardTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_accessible(self):
        """La page de login est accessible sans authentification"""
        response = self.client.get('/accounts/login/')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirige_si_non_connecte(self):
        """Le dashboard redirige vers login si non connecté"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_accessible_si_connecte(self):
        """Le dashboard est accessible si connecté"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class ClientsTests(TestCase):

    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        self.client_http.login(username='testuser2', password='testpass123')

    def test_liste_clients_accessible(self):
        """La page clients est accessible"""
        response = self.client_http.get('/clients/')
        self.assertEqual(response.status_code, 200)

    def test_ajouter_client(self):
        """On peut ajouter un client"""
        from clients.models import Client
        response = self.client_http.post('/clients/ajouter/', {
            'nom': 'Amadou Test',
            'telephone': '77000000',
            'adresse': 'Dakar'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(nom='Amadou Test').exists())


class StockTests(TestCase):

    def setUp(self):
        self.client_http = Client()
        self.user = User.objects.create_user(
            username='testuser3',
            password='testpass123'
        )
        self.client_http.login(username='testuser3', password='testpass123')

    def test_page_stock_accessible(self):
        """La page stock est accessible"""
        response = self.client_http.get('/stock/')
        self.assertEqual(response.status_code, 200)
