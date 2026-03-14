from datetime import date, datetime
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from billing.models import (
    BankAccount,
    Client,
    CompanyProfile,
    Invoice,
    InvoiceItem,
    Payment,
    Project,
    Quote,
    QuoteItem,
    ReminderLog,
)

MAX_ITEMS_PER_DOCUMENT = 10


@pytest.fixture
def logged_in_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='owner', password='ComplexPass123')
    client.force_login(user)
    return client


@pytest.fixture
def records():
    company = CompanyProfile.objects.create(name='自社A')
    bank_account = BankAccount.objects.create(
        company_profile=company,
        nickname='メイン口座',
        bank_name='みずほ銀行',
        account_number='1234567',
        account_holder='クオートトゥペイド',
    )
    client_record = Client.objects.create(name='取引先A', payment_terms_days=30)
    project = Project.objects.create(client=client_record, name='案件A')
    quote = Quote.objects.create(
        company_profile=company,
        project=project,
        quote_number='Q-INIT-001',
        title='初回見積',
        issue_date=date(2026, 3, 14),
    )
    quote_item = QuoteItem.objects.create(
        quote=quote,
        display_order=1,
        description='設計',
        quantity=Decimal('1.00'),
        unit_price=Decimal('10000.00'),
    )
    invoice = Invoice.objects.create(
        company_profile=company,
        bank_account=bank_account,
        project=project,
        quote=quote,
        invoice_number='INV-INIT-001',
        title='初回請求',
        issue_date=date(2026, 3, 14),
        due_date=date(2026, 3, 31),
    )
    invoice_item = InvoiceItem.objects.create(
        invoice=invoice,
        quote_item=quote_item,
        display_order=1,
        description='設計',
        quantity=Decimal('1.00'),
        unit_price=Decimal('10000.00'),
    )
    payment = Payment.objects.create(
        invoice=invoice,
        received_on=date(2026, 3, 20),
        amount=Decimal('5000.00'),
    )
    reminder_log = ReminderLog.objects.create(
        invoice=invoice,
        reminded_at=timezone.make_aware(datetime(2026, 3, 21, 9, 0, 0)),
        recipient='billing@example.com',
    )
    return {
        'company': company,
        'bank_account': bank_account,
        'client': client_record,
        'project': project,
        'quote': quote,
        'quote_item': quote_item,
        'invoice': invoice,
        'invoice_item': invoice_item,
        'payment': payment,
        'reminder_log': reminder_log,
    }


def build_formset_payload(prefix, items, initial_forms=0):
    payload = {
        f'{prefix}-TOTAL_FORMS': str(len(items)),
        f'{prefix}-INITIAL_FORMS': str(initial_forms),
        f'{prefix}-MIN_NUM_FORMS': '0',
        f'{prefix}-MAX_NUM_FORMS': str(MAX_ITEMS_PER_DOCUMENT),
    }
    for index, item in enumerate(items):
        for key, value in item.items():
            payload[f'{prefix}-{index}-{key}'] = value
    return payload


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url_name',
    [
        'billing:company-profile-list',
        'billing:bank-account-list',
        'billing:client-list',
        'billing:project-list',
        'billing:quote-list',
        'billing:invoice-list',
        'billing:payment-list',
        'billing:reminder-log-list',
    ],
)
def test_record_list_views_render_for_logged_in_user(logged_in_client, records, url_name):
    response = logged_in_client.get(reverse(url_name))

    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    'case_name',
    [
        'company_profile',
        'bank_account',
        'client',
        'project',
        'quote',
        'invoice',
        'payment',
        'reminder_log',
    ],
)
def test_record_create_views_persist_objects(logged_in_client, records, case_name):
    if case_name == 'company_profile':
        url = reverse('billing:company-profile-create')
        post_data = {
            'name': '自社B',
            'legal_name': '株式会社B',
            'invoice_registration_number': 'T1234567890123',
            'email': 'corp@example.com',
            'phone': '03-1111-2222',
            'postal_code': '100-0001',
            'address': '東京都千代田区',
            'website': 'https://example.com',
            'notes': 'テスト登録',
            'is_default': 'on',
        }
        model = CompanyProfile
        expected = lambda obj: obj.name == '自社B'
    elif case_name == 'bank_account':
        url = reverse('billing:bank-account-create')
        post_data = {
            'company_profile': str(records['company'].pk),
            'nickname': 'サブ口座',
            'bank_name': '三井住友銀行',
            'branch_name': '新宿支店',
            'account_type': 'ordinary',
            'account_number': '7654321',
            'account_holder': 'クオートトゥペイド サブ',
            'is_default': 'on',
        }
        model = BankAccount
        expected = lambda obj: obj.nickname == 'サブ口座'
    elif case_name == 'client':
        url = reverse('billing:client-create')
        post_data = {
            'name': '取引先B',
            'legal_name': '株式会社取引先B',
            'contact_person': '田中太郎',
            'email': 'client@example.com',
            'phone': '090-1111-2222',
            'postal_code': '150-0001',
            'address': '東京都渋谷区',
            'invoice_registration_number': 'T9999999999999',
            'payment_terms_days': '45',
            'notes': '新規取引先',
            'is_active': 'on',
        }
        model = Client
        expected = lambda obj: obj.name == '取引先B'
    elif case_name == 'project':
        url = reverse('billing:project-create')
        post_data = {
            'client': str(records['client'].pk),
            'name': '案件B',
            'code': 'PRJ-B',
            'status': 'active',
            'description': '追加案件',
            'start_date': '2026-04-01',
            'end_date': '2026-05-31',
            'notes': '補足あり',
        }
        model = Project
        expected = lambda obj: obj.name == '案件B'
    elif case_name == 'quote':
        url = reverse('billing:quote-create')
        post_data = {
            'company_profile': str(records['company'].pk),
            'project': str(records['project'].pk),
            'quote_number': 'Q-NEW-001',
            'title': '追加見積',
            'issue_date': '2026-04-01',
            'valid_until': '2026-04-30',
            'status': 'draft',
            'currency': 'JPY',
            'tax_rate': '10.00',
            'terms': '月末締め',
            'notes': '見積備考',
            'sent_at': '',
            'approved_at': '',
        }
        post_data.update(
            build_formset_payload(
                'items',
                [
                    {
                        'display_order': '1',
                        'description': '設計',
                        'unit_label': '式',
                        'quantity': '1.00',
                        'unit_price': '10000.00',
                        'notes': '1行目',
                    },
                    {
                        'display_order': '2',
                        'description': '実装',
                        'unit_label': '式',
                        'quantity': '2.00',
                        'unit_price': '15000.00',
                        'notes': '2行目',
                    },
                ],
            )
        )
        model = Quote
        expected = lambda obj: obj.quote_number == 'Q-NEW-001' and obj.items.count() == 2 and obj.total_amount == Decimal('44000.00')
    elif case_name == 'invoice':
        url = reverse('billing:invoice-create')
        post_data = {
            'company_profile': str(records['company'].pk),
            'bank_account': str(records['bank_account'].pk),
            'project': str(records['project'].pk),
            'quote': str(records['quote'].pk),
            'invoice_number': 'INV-NEW-001',
            'title': '追加請求',
            'issue_date': '2026-04-01',
            'due_date': '2026-04-30',
            'status': 'draft',
            'currency': 'JPY',
            'tax_rate': '10.00',
            'notes': '請求備考',
            'sent_at': '',
        }
        post_data.update(
            build_formset_payload(
                'items',
                [
                    {
                        'quote_item': str(records['quote_item'].pk),
                        'display_order': '1',
                        'description': '設計',
                        'unit_label': '式',
                        'quantity': '1.00',
                        'unit_price': '8000.00',
                        'notes': '1行目',
                    },
                    {
                        'quote_item': '',
                        'display_order': '2',
                        'description': '運用',
                        'unit_label': '月',
                        'quantity': '1.00',
                        'unit_price': '12000.00',
                        'notes': '2行目',
                    },
                ],
            )
        )
        model = Invoice
        expected = lambda obj: obj.invoice_number == 'INV-NEW-001' and obj.items.count() == 2 and obj.total_amount == Decimal('22000.00')
    elif case_name == 'payment':
        url = reverse('billing:payment-create')
        post_data = {
            'invoice': str(records['invoice'].pk),
            'received_on': '2026-04-05',
            'amount': '12000.00',
            'fee_amount': '330.00',
            'method': 'bank_transfer',
            'status': 'received',
            'reference_number': 'PAY-001',
            'notes': '追加入金',
        }
        model = Payment
        expected = lambda obj: obj.reference_number == 'PAY-001'
    else:
        url = reverse('billing:reminder-log-create')
        post_data = {
            'invoice': str(records['invoice'].pk),
            'reminded_at': '2026-04-06T10:30',
            'method': 'email',
            'recipient': 'finance@example.com',
            'subject': 'お支払い確認',
            'body': 'ご確認ください。',
            'status': 'sent',
            'next_follow_up_on': '2026-04-10',
            'notes': '1回目催促',
        }
        model = ReminderLog
        expected = lambda obj: obj.subject == 'お支払い確認'

    response = logged_in_client.post(url, post_data)

    assert response.status_code == 302
    created = model.objects.order_by('-id').first()
    assert expected(created)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'case_name',
    [
        'company_profile',
        'bank_account',
        'client',
        'project',
        'quote',
        'invoice',
        'payment',
        'reminder_log',
    ],
)
def test_record_update_views_persist_changes(logged_in_client, records, case_name):
    if case_name == 'company_profile':
        instance = records['company']
        url = reverse('billing:company-profile-update', args=[instance.pk])
        post_data = {
            'name': '自社A更新',
            'legal_name': '株式会社A更新',
            'invoice_registration_number': '',
            'email': '',
            'phone': '',
            'postal_code': '',
            'address': '',
            'website': '',
            'notes': '更新済み',
            'is_default': 'on',
        }
        expected = lambda obj: obj.name == '自社A更新'
    elif case_name == 'bank_account':
        instance = records['bank_account']
        url = reverse('billing:bank-account-update', args=[instance.pk])
        post_data = {
            'company_profile': str(records['company'].pk),
            'nickname': 'メイン口座更新',
            'bank_name': 'みずほ銀行',
            'branch_name': '東京支店',
            'account_type': 'current',
            'account_number': '1234567',
            'account_holder': 'クオートトゥペイド',
            'is_default': 'on',
        }
        expected = lambda obj: obj.nickname == 'メイン口座更新'
    elif case_name == 'client':
        instance = records['client']
        url = reverse('billing:client-update', args=[instance.pk])
        post_data = {
            'name': '取引先A更新',
            'legal_name': '',
            'contact_person': '佐藤花子',
            'email': '',
            'phone': '',
            'postal_code': '',
            'address': '',
            'invoice_registration_number': '',
            'payment_terms_days': '60',
            'notes': '更新済み',
            'is_active': 'on',
        }
        expected = lambda obj: obj.name == '取引先A更新'
    elif case_name == 'project':
        instance = records['project']
        url = reverse('billing:project-update', args=[instance.pk])
        post_data = {
            'client': str(records['client'].pk),
            'name': '案件A更新',
            'code': 'PRJ-A-UPDATED',
            'status': 'completed',
            'description': '完了案件',
            'start_date': '2026-03-01',
            'end_date': '2026-03-31',
            'notes': '完了済み',
        }
        expected = lambda obj: obj.name == '案件A更新'
    elif case_name == 'quote':
        instance = records['quote']
        url = reverse('billing:quote-update', args=[instance.pk])
        post_data = {
            'company_profile': str(records['company'].pk),
            'project': str(records['project'].pk),
            'quote_number': 'Q-INIT-001-UPDATED',
            'title': '初回見積更新',
            'issue_date': '2026-03-15',
            'valid_until': '2026-03-31',
            'status': 'sent',
            'currency': 'JPY',
            'tax_rate': '10.00',
            'terms': '即日着手',
            'notes': '更新済み',
            'sent_at': '2026-03-15T10:00',
            'approved_at': '',
        }
        post_data.update(
            build_formset_payload(
                'items',
                [
                    {
                        'id': str(records['quote_item'].pk),
                        'display_order': '1',
                        'description': '設計更新',
                        'unit_label': '式',
                        'quantity': '3.00',
                        'unit_price': '7000.00',
                        'notes': '更新済み',
                    },
                    {
                        'display_order': '2',
                        'description': '実装追加',
                        'unit_label': '式',
                        'quantity': '1.00',
                        'unit_price': '5000.00',
                        'notes': '追加行',
                    },
                ],
                initial_forms=1,
            )
        )
        expected = lambda obj: obj.quote_number == 'Q-INIT-001-UPDATED' and obj.items.count() == 2 and obj.total_amount == Decimal('28600.00')
    elif case_name == 'invoice':
        instance = records['invoice']
        url = reverse('billing:invoice-update', args=[instance.pk])
        post_data = {
            'company_profile': str(records['company'].pk),
            'bank_account': str(records['bank_account'].pk),
            'project': str(records['project'].pk),
            'quote': str(records['quote'].pk),
            'invoice_number': 'INV-INIT-001-UPDATED',
            'title': '初回請求更新',
            'issue_date': '2026-03-16',
            'due_date': '2026-04-15',
            'status': 'sent',
            'currency': 'JPY',
            'tax_rate': '10.00',
            'notes': '更新済み',
            'sent_at': '2026-03-16T11:00',
        }
        post_data.update(
            build_formset_payload(
                'items',
                [
                    {
                        'id': str(records['invoice_item'].pk),
                        'quote_item': str(records['quote_item'].pk),
                        'display_order': '1',
                        'description': '設計更新',
                        'unit_label': '式',
                        'quantity': '2.00',
                        'unit_price': '9000.00',
                        'notes': '更新済み',
                    },
                    {
                        'quote_item': '',
                        'display_order': '2',
                        'description': '運用追加',
                        'unit_label': '月',
                        'quantity': '1.00',
                        'unit_price': '4000.00',
                        'notes': '追加行',
                    },
                ],
                initial_forms=1,
            )
        )
        expected = lambda obj: obj.invoice_number == 'INV-INIT-001-UPDATED' and obj.items.count() == 2 and obj.total_amount == Decimal('24200.00')
    elif case_name == 'payment':
        instance = records['payment']
        url = reverse('billing:payment-update', args=[instance.pk])
        post_data = {
            'invoice': str(records['invoice'].pk),
            'received_on': '2026-03-22',
            'amount': '15000.00',
            'fee_amount': '440.00',
            'method': 'cash',
            'status': 'pending',
            'reference_number': 'PAY-UPDATED',
            'notes': '更新済み',
        }
        expected = lambda obj: obj.reference_number == 'PAY-UPDATED'
    else:
        instance = records['reminder_log']
        url = reverse('billing:reminder-log-update', args=[instance.pk])
        post_data = {
            'invoice': str(records['invoice'].pk),
            'reminded_at': '2026-03-22T14:15',
            'method': 'phone',
            'recipient': 'finance@example.com',
            'subject': '電話催促',
            'body': 'お電話でご連絡しました。',
            'status': 'replied',
            'next_follow_up_on': '2026-03-25',
            'notes': '更新済み',
        }
        expected = lambda obj: obj.subject == '電話催促'

    response = logged_in_client.post(url, post_data)

    assert response.status_code == 302
    instance.refresh_from_db()
    assert expected(instance)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'case_name',
    [
        'company_profile',
        'bank_account',
        'client',
        'project',
        'quote',
        'invoice',
        'payment',
        'reminder_log',
    ],
)
def test_record_delete_views_remove_objects(logged_in_client, case_name):
    if case_name == 'company_profile':
        obj = CompanyProfile.objects.create(name='削除用自社')
        url = reverse('billing:company-profile-delete', args=[obj.pk])
        model = CompanyProfile
    elif case_name == 'bank_account':
        company = CompanyProfile.objects.create(name='削除用自社')
        obj = BankAccount.objects.create(
            company_profile=company,
            nickname='削除用口座',
            bank_name='削除銀行',
            account_number='1111111',
            account_holder='サクジョ',
        )
        url = reverse('billing:bank-account-delete', args=[obj.pk])
        model = BankAccount
    elif case_name == 'client':
        obj = Client.objects.create(name='削除用取引先')
        url = reverse('billing:client-delete', args=[obj.pk])
        model = Client
    elif case_name == 'project':
        client_record = Client.objects.create(name='削除用取引先')
        obj = Project.objects.create(client=client_record, name='削除用案件')
        url = reverse('billing:project-delete', args=[obj.pk])
        model = Project
    elif case_name == 'quote':
        client_record = Client.objects.create(name='削除用取引先')
        project = Project.objects.create(client=client_record, name='削除用案件')
        obj = Quote.objects.create(project=project, quote_number='Q-DELETE-001', title='削除用見積', issue_date=date(2026, 3, 14))
        url = reverse('billing:quote-delete', args=[obj.pk])
        model = Quote
    elif case_name == 'invoice':
        client_record = Client.objects.create(name='削除用取引先')
        project = Project.objects.create(client=client_record, name='削除用案件')
        obj = Invoice.objects.create(project=project, invoice_number='INV-DELETE-001', title='削除用請求', issue_date=date(2026, 3, 14), due_date=date(2026, 3, 31))
        url = reverse('billing:invoice-delete', args=[obj.pk])
        model = Invoice
    elif case_name == 'payment':
        client_record = Client.objects.create(name='削除用取引先')
        project = Project.objects.create(client=client_record, name='削除用案件')
        invoice = Invoice.objects.create(project=project, invoice_number='INV-DELETE-003', title='削除用請求', issue_date=date(2026, 3, 14), due_date=date(2026, 3, 31))
        obj = Payment.objects.create(invoice=invoice, received_on=date(2026, 3, 20), amount=Decimal('1000.00'))
        url = reverse('billing:payment-delete', args=[obj.pk])
        model = Payment
    else:
        client_record = Client.objects.create(name='削除用取引先')
        project = Project.objects.create(client=client_record, name='削除用案件')
        invoice = Invoice.objects.create(project=project, invoice_number='INV-DELETE-004', title='削除用請求', issue_date=date(2026, 3, 14), due_date=date(2026, 3, 31))
        obj = ReminderLog.objects.create(invoice=invoice, reminded_at=timezone.make_aware(datetime(2026, 3, 21, 9, 0, 0)))
        url = reverse('billing:reminder-log-delete', args=[obj.pk])
        model = ReminderLog

    object_id = obj.pk
    response = logged_in_client.post(url)

    assert response.status_code == 302
    assert not model.objects.filter(pk=object_id).exists()


@pytest.mark.django_db
def test_protected_delete_redirects_with_message(logged_in_client, records):
    response = logged_in_client.post(reverse('billing:client-delete', args=[records['client'].pk]), follow=True)

    assert response.status_code == 200
    assert Client.objects.filter(pk=records['client'].pk).exists()
    messages = list(response.context['messages'])
    assert any('関連する案件があるため削除できません' in str(message) for message in messages)


@pytest.mark.django_db
def test_quote_create_view_rejects_more_than_ten_items(logged_in_client, records):
    post_data = {
        'company_profile': str(records['company'].pk),
        'project': str(records['project'].pk),
        'quote_number': 'Q-LIMIT-001',
        'title': '明細上限確認',
        'issue_date': '2026-04-01',
        'valid_until': '2026-04-30',
        'status': 'draft',
        'currency': 'JPY',
        'tax_rate': '10.00',
        'terms': '',
        'notes': '',
        'sent_at': '',
        'approved_at': '',
    }
    items = []
    for index in range(MAX_ITEMS_PER_DOCUMENT + 1):
        items.append(
            {
                'display_order': str(index + 1),
                'description': f'明細{index + 1}',
                'unit_label': '式',
                'quantity': '1.00',
                'unit_price': '1000.00',
                'notes': '',
            }
        )
    post_data.update(build_formset_payload('items', items))

    response = logged_in_client.post(reverse('billing:quote-create'), post_data)

    assert response.status_code == 200
    assert Quote.objects.filter(quote_number='Q-LIMIT-001').count() == 0
    assert response.context['item_formset'].non_form_errors()


@pytest.mark.django_db
def test_invoice_create_view_rejects_more_than_ten_items(logged_in_client, records):
    post_data = {
        'company_profile': str(records['company'].pk),
        'bank_account': str(records['bank_account'].pk),
        'project': str(records['project'].pk),
        'quote': str(records['quote'].pk),
        'invoice_number': 'INV-LIMIT-001',
        'title': '明細上限確認',
        'issue_date': '2026-04-01',
        'due_date': '2026-04-30',
        'status': 'draft',
        'currency': 'JPY',
        'tax_rate': '10.00',
        'notes': '',
        'sent_at': '',
    }
    items = []
    for index in range(MAX_ITEMS_PER_DOCUMENT + 1):
        items.append(
            {
                'quote_item': '',
                'display_order': str(index + 1),
                'description': f'明細{index + 1}',
                'unit_label': '式',
                'quantity': '1.00',
                'unit_price': '1000.00',
                'notes': '',
            }
        )
    post_data.update(build_formset_payload('items', items))

    response = logged_in_client.post(reverse('billing:invoice-create'), post_data)

    assert response.status_code == 200
    assert Invoice.objects.filter(invoice_number='INV-LIMIT-001').count() == 0
    assert response.context['item_formset'].non_form_errors()


@pytest.mark.django_db
def test_quote_update_view_rejects_eleventh_item(logged_in_client, records):
    for index in range(2, MAX_ITEMS_PER_DOCUMENT + 1):
        QuoteItem.objects.create(
            quote=records['quote'],
            display_order=index,
            description=f'既存明細{index}',
            quantity=Decimal('1.00'),
            unit_price=Decimal('1000.00'),
        )

    items = []
    for item in records['quote'].items.order_by('display_order'):
        items.append(
            {
                'id': str(item.pk),
                'display_order': str(item.display_order),
                'description': item.description,
                'unit_label': item.unit_label,
                'quantity': str(item.quantity),
                'unit_price': str(item.unit_price),
                'notes': item.notes,
            }
        )
    items.append(
        {
            'display_order': '11',
            'description': '11件目',
            'unit_label': '式',
            'quantity': '1.00',
            'unit_price': '1000.00',
            'notes': '',
        }
    )

    response = logged_in_client.post(
        reverse('billing:quote-update', args=[records['quote'].pk]),
        {
            'company_profile': str(records['company'].pk),
            'project': str(records['project'].pk),
            'quote_number': records['quote'].quote_number,
            'title': records['quote'].title,
            'issue_date': records['quote'].issue_date.isoformat(),
            'valid_until': '',
            'status': records['quote'].status,
            'currency': records['quote'].currency,
            'tax_rate': str(records['quote'].tax_rate),
            'terms': records['quote'].terms,
            'notes': records['quote'].notes,
            'sent_at': '',
            'approved_at': '',
            **build_formset_payload('items', items, initial_forms=MAX_ITEMS_PER_DOCUMENT),
        },
    )

    assert response.status_code == 200
    assert records['quote'].items.count() == MAX_ITEMS_PER_DOCUMENT
    assert response.context['item_formset'].non_form_errors()
@pytest.mark.django_db
def test_invoice_update_view_rejects_eleventh_item(logged_in_client, records):
    for index in range(2, MAX_ITEMS_PER_DOCUMENT + 1):
        InvoiceItem.objects.create(
            invoice=records['invoice'],
            display_order=index,
            description=f'既存明細{index}',
            quantity=Decimal('1.00'),
            unit_price=Decimal('1000.00'),
        )

    items = []
    for item in records['invoice'].items.order_by('display_order'):
        items.append(
            {
                'id': str(item.pk),
                'quote_item': str(item.quote_item_id or ''),
                'display_order': str(item.display_order),
                'description': item.description,
                'unit_label': item.unit_label,
                'quantity': str(item.quantity),
                'unit_price': str(item.unit_price),
                'notes': item.notes,
            }
        )
    items.append(
        {
            'quote_item': '',
            'display_order': '11',
            'description': '11件目',
            'unit_label': '式',
            'quantity': '1.00',
            'unit_price': '1000.00',
            'notes': '',
        }
    )

    response = logged_in_client.post(
        reverse('billing:invoice-update', args=[records['invoice'].pk]),
        {
            'company_profile': str(records['company'].pk),
            'bank_account': str(records['bank_account'].pk),
            'project': str(records['project'].pk),
            'quote': str(records['quote'].pk),
            'invoice_number': records['invoice'].invoice_number,
            'title': records['invoice'].title,
            'issue_date': records['invoice'].issue_date.isoformat(),
            'due_date': records['invoice'].due_date.isoformat(),
            'status': records['invoice'].status,
            'currency': records['invoice'].currency,
            'tax_rate': str(records['invoice'].tax_rate),
            'notes': records['invoice'].notes,
            'sent_at': '',
            **build_formset_payload('items', items, initial_forms=MAX_ITEMS_PER_DOCUMENT),
        },
    )

    assert response.status_code == 200
    assert records['invoice'].items.count() == MAX_ITEMS_PER_DOCUMENT
    assert response.context['item_formset'].non_form_errors()


@pytest.mark.django_db
def test_quote_status_page_filters_rows_by_selected_status(logged_in_client, records):
    Quote.objects.create(
        company_profile=records['company'],
        project=records['project'],
        quote_number='Q-INIT-002',
        title='送付済み見積',
        issue_date=date(2026, 3, 15),
        status='sent',
    )

    response = logged_in_client.get(reverse('billing:quote-status-list', args=['sent']))

    assert response.status_code == 200
    assert response.context['current_status_label'] == '送付済み'
    assert len(response.context['table_rows']) == 1
    assert response.context['table_rows'][0]['object'].quote_number == 'Q-INIT-002'
    active_links = [link for link in response.context['status_navigation'] if link['is_active']]
    assert len(active_links) == 1
    assert active_links[0]['label'] == '送付済み'

