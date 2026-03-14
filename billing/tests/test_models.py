import pytest
from datetime import date, datetime
from decimal import Decimal

from django.utils import timezone

from billing.models import (
    BankAccount,
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
    invoice.refresh_from_db()

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


@pytest.mark.django_db
def test_quote_total_refreshes_on_quote_item_update_and_delete():
    client = Client.objects.create(name='更新確認取引先')
    project = Project.objects.create(client=client, name='更新確認案件')
    quote = Quote.objects.create(
        project=project,
        quote_number='Q-2026-0099',
        title='更新確認見積',
        issue_date=date(2026, 3, 14),
    )
    item = QuoteItem.objects.create(
        quote=quote,
        description='開発',
        quantity=Decimal('1.00'),
        unit_price=Decimal('10000.00'),
    )

    quote.refresh_from_db()
    assert quote.total_amount == Decimal('11000.00')

    item.quantity = Decimal('2.00')
    item.unit_price = Decimal('12000.00')
    item.save()
    quote.refresh_from_db()
    assert quote.total_amount == Decimal('26400.00')

    item.delete()
    quote.refresh_from_db()
    assert quote.total_amount == Decimal('0.00')


@pytest.mark.django_db
def test_invoice_total_refreshes_on_invoice_item_update_and_delete():
    client = Client.objects.create(name='更新確認取引先')
    project = Project.objects.create(client=client, name='更新確認案件')
    invoice = Invoice.objects.create(
        project=project,
        invoice_number='INV-2026-0099',
        title='更新確認請求',
        issue_date=date(2026, 3, 14),
        due_date=date(2026, 3, 31),
    )
    item = InvoiceItem.objects.create(
        invoice=invoice,
        description='開発',
        quantity=Decimal('1.00'),
        unit_price=Decimal('20000.00'),
    )

    invoice.refresh_from_db()
    assert invoice.total_amount == Decimal('22000.00')

    item.quantity = Decimal('2.00')
    item.unit_price = Decimal('15000.00')
    item.save()
    invoice.refresh_from_db()
    assert invoice.total_amount == Decimal('33000.00')

    item.delete()
    invoice.refresh_from_db()
    assert invoice.total_amount == Decimal('0.00')


@pytest.mark.django_db
def test_company_profile_default_turns_off_other_defaults():
    first = CompanyProfile.objects.create(name='自社A', is_default=True)
    second = CompanyProfile.objects.create(name='自社B', is_default=True)

    first.refresh_from_db()
    second.refresh_from_db()

    assert first.is_default is False
    assert second.is_default is True


@pytest.mark.django_db
def test_bank_account_default_turns_off_other_defaults_within_same_company():
    company = CompanyProfile.objects.create(name='自社A')
    other_company = CompanyProfile.objects.create(name='自社B')
    first = BankAccount.objects.create(
        company_profile=company,
        nickname='口座A',
        bank_name='みずほ銀行',
        account_number='1111111',
        account_holder='カ)A',
        is_default=True,
    )
    second = BankAccount.objects.create(
        company_profile=company,
        nickname='口座B',
        bank_name='三井住友銀行',
        account_number='2222222',
        account_holder='カ)B',
        is_default=True,
    )
    other_company_account = BankAccount.objects.create(
        company_profile=other_company,
        nickname='口座C',
        bank_name='りそな銀行',
        account_number='3333333',
        account_holder='カ)C',
        is_default=True,
    )

    first.refresh_from_db()
    second.refresh_from_db()
    other_company_account.refresh_from_db()

    assert first.is_default is False
    assert second.is_default is True
    assert other_company_account.is_default is True

@pytest.mark.django_db
def test_jpy_amounts_are_rounded_to_whole_yen():
    client = Client.objects.create(name='丸め確認取引先')
    project = Project.objects.create(client=client, name='丸め確認案件')
    quote = Quote.objects.create(
        project=project,
        quote_number='Q-2026-0100',
        title='丸め確認見積',
        issue_date=date(2026, 3, 14),
    )
    item = QuoteItem.objects.create(
        quote=quote,
        description='端数確認',
        quantity=Decimal('1.00'),
        unit_price=Decimal('1000.50'),
    )

    item.refresh_from_db()
    quote.refresh_from_db()

    assert item.total_amount == Decimal('1001.00')
    assert quote.subtotal_amount == Decimal('1001.00')
    assert quote.tax_amount == Decimal('100.00')
    assert quote.total_amount == Decimal('1101.00')
