from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='ComplexPass123')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('billing:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=/', response.url)

    def test_dashboard_page_renders_for_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('billing:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QuoteToPaid')
        self.assertContains(response, 'ログイン中: owner')
        self.assertContains(response, '取引先登録から入金までの最短フロー')
        self.assertContains(response, '次にやること')
        self.assertTemplateUsed(response, 'billing/dashboard.html')
