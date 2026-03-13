import pytest
from decimal import Decimal
from datetime import date, datetime

from django.utils import timezone

from billing.models import (
    Client,
    CompanyProfile,
    Invoice,
    InvoiceItem,
    Payment,
    PaymentStatus,
    Project,
    Quote,
    QuoteItem,
    ReminderLog,
    ReminderMethod,
    ReminderStatus,
)


@pytest.mark.django_db
def test_quote_refresh_amounts_aggregates_items():
    client = Client.objects.create(name='テスト取引先')
    project = Project.objects.create(client=client, name='サイト改善')
    quote = Quote.objects.create(
        project=project,
        quote_number='Q-2026-0001',
        title='サイト改善見積',
        issue_date=date(2026, 3, 14),
    )
    QuoteItem.objects.create(quote=quote, description='設計', quantity=Decimal('2.00'), unit_price=Decimal('50000.00'))
    QuoteItem.objects.create(quote=quote, description='実装', quantity=Decimal('3.00'), unit_price=Decimal('30000.00'))

    quote.refresh_amounts()
    quote.refresh_from_db()

    assert quote.subtotal_amount == Decimal('190000.00')
    assert quote.tax_amount == Decimal('19000.00')
    assert quote.total_amount == Decimal('209000.00')


@pytest.mark.django_db
def test_invoice_outstanding_amount_uses_received_payments_only():
    client = Client.objects.create(name='テスト取引先')
    project = Project.objects.create(client=client, name='運用支援')
    invoice = Invoice.objects.create(
        project=project,
        invoice_number='INV-2026-0001',
        title='運用支援請求',
        issue_date=date(2026, 3, 14),
        due_date=date(2026, 3, 31),
    )
    InvoiceItem.objects.create(invoice=invoice, description='月次支援', quantity=Decimal('1.00'), unit_price=Decimal('120000.00'))
    invoice.refresh_amounts()

    Payment.objects.create(
        invoice=invoice,
        received_on=date(2026, 3, 20),
        amount=Decimal('20000.00'),
        status=PaymentStatus.PENDING,
    )
    Payment.objects.create(
        invoice=invoice,
        received_on=date(2026, 3, 21),
        amount=Decimal('50000.00'),
        status=PaymentStatus.RECEIVED,
    )

    assert invoice.paid_amount == Decimal('50000.00')
    assert invoice.outstanding_amount == Decimal('82000.00')


@pytest.mark.django_db
def test_reminder_log_can_be_recorded_for_invoice():
    company = CompanyProfile.objects.create(name='QuoteToPaid Studio')
    client = Client.objects.create(name='テスト取引先')
    project = Project.objects.create(client=client, name='催促運用')
    invoice = Invoice.objects.create(
        company_profile=company,
        project=project,
        invoice_number='INV-2026-0002',
        title='催促対象請求',
        issue_date=date(2026, 3, 1),
        due_date=date(2026, 3, 15),
    )

    reminder = ReminderLog.objects.create(
        invoice=invoice,
        reminded_at=timezone.make_aware(datetime(2026, 3, 16, 9, 0, 0)),
        method=ReminderMethod.EMAIL,
        recipient='billing@example.com',
        subject='お支払いのご確認',
        body='お支払い状況をご確認ください。',
        status=ReminderStatus.SENT,
    )

    assert reminder.invoice == invoice
    assert reminder.status == ReminderStatus.SENT
