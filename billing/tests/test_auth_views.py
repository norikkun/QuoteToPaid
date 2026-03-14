from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationFlowTests(TestCase):
    def test_login_page_renders_when_no_user_exists(self):
        response = self.client.get(reverse('billing:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規登録へ')
        self.assertContains(response, reverse('billing:user-setup'))

    def test_setup_page_renders_when_no_user_exists(self):
        response = self.client.get(reverse('billing:user-setup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー登録')
        self.assertTemplateUsed(response, 'billing/users/user_form.html')

    def test_setup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('billing:user-setup'),
            {
                'username': 'owner',
                'first_name': '太郎',
                'last_name': '田中',
                'email': 'owner@example.com',
                'password1': 'ComplexPass123',
                'password2': 'ComplexPass123',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('billing:dashboard'))
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'ユーザーを登録し、ログインしました。')
        self.assertTrue(response.context['user'].is_authenticated)

    def test_setup_page_renders_even_when_user_already_exists(self):
        User.objects.create_user(username='owner', password='ComplexPass123')

        response = self.client.get(reverse('billing:user-setup'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー登録')

    def test_setup_allows_multiple_users_to_register(self):
        User.objects.create_user(username='owner', password='ComplexPass123')

        response = self.client.post(
            reverse('billing:user-setup'),
            {
                'username': 'second',
                'first_name': '次',
                'last_name': 'ユーザー',
                'email': 'second@example.com',
                'password1': 'ComplexPass123',
                'password2': 'ComplexPass123',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('billing:dashboard'))
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='second').exists())

    def test_login_page_contains_setup_link(self):
        User.objects.create_user(username='owner', password='ComplexPass123')

        response = self.client.get(reverse('billing:login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('billing:user-setup'))
        self.assertContains(response, '新規登録へ')

    def test_login_authenticates_registered_user(self):
        User.objects.create_user(username='owner', password='ComplexPass123')

        response = self.client.post(
            reverse('billing:login'),
            {
                'username': 'owner',
                'password': 'ComplexPass123',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('billing:dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout_clears_session(self):
        user = User.objects.create_user(username='owner', password='ComplexPass123')
        self.client.force_login(user)

        response = self.client.post(reverse('billing:logout'), follow=True)

        self.assertRedirects(response, reverse('billing:login'))
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertContains(response, 'ログアウトしました。')
