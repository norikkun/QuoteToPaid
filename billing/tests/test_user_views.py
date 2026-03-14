from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class UserAccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='owner',
            first_name='太郎',
            last_name='田中',
            email='owner@example.com',
            password='ComplexPass123',
        )
        self.client.force_login(self.user)

    def test_user_detail_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse('billing:user-detail'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/?next=/user/', response.url)

    def test_user_detail_renders_current_user(self):
        response = self.client.get(reverse('billing:user-detail'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'アカウント設定')
        self.assertContains(response, 'owner@example.com')
        self.assertTemplateUsed(response, 'billing/users/user_detail.html')

    def test_user_update_updates_current_user(self):
        response = self.client.post(
            reverse('billing:user-update'),
            {
                'username': 'owner-updated',
                'first_name': '花子',
                'last_name': '田中',
                'email': 'updated@example.com',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('billing:user-detail'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'owner-updated')
        self.assertEqual(self.user.first_name, '花子')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertContains(response, 'ユーザー情報を更新しました。')

    def test_user_delete_removes_current_user_and_redirects_to_login(self):
        response = self.client.post(reverse('billing:user-delete'), follow=True)

        self.assertRedirects(response, reverse('billing:login'))
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, 'ユーザーを削除しました。')
