from django.test import TestCase
from django.urls import reverse


class DashboardViewTests(TestCase):
    def test_dashboard_page_renders(self):
        response = self.client.get(reverse('billing:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QuoteToPaid')
        self.assertTemplateUsed(response, 'billing/dashboard.html')

    def test_healthcheck_returns_ok_payload(self):
        response = self.client.get(reverse('billing:healthcheck'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                'project': 'QuoteToPaid',
                'message': 'Environment is ready.',
                'status': 'ok',
            },
        )

    def test_pdf_preview_returns_pdf(self):
        response = self.client.get(reverse('billing:pdf-preview'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline; filename="quote-to-paid-invoice-preview.pdf"', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))
