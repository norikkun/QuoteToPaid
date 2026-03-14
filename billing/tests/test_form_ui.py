from datetime import date

import pytest
from django.urls import reverse

from billing.forms import BankAccountForm, ClientForm, CompanyProfileForm
from billing.forms.record_form import QuoteInlineItemForm
from billing.models import BankAccount, Client, CompanyProfile, Project, Quote


@pytest.fixture
def logged_in_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='owner', password='ComplexPass123')
    client.force_login(user)
    return client


@pytest.fixture
def document_records():
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
    return {
        'company': company,
        'bank_account': bank_account,
        'client': client_record,
        'project': project,
        'quote': quote,
    }


def build_formset_payload(prefix, items, initial_forms=0):
    payload = {
        f'{prefix}-TOTAL_FORMS': str(len(items)),
        f'{prefix}-INITIAL_FORMS': str(initial_forms),
        f'{prefix}-MIN_NUM_FORMS': '0',
        f'{prefix}-MAX_NUM_FORMS': '10',
    }
    for index, item in enumerate(items):
        for key, value in item.items():
            payload[f'{prefix}-{index}-{key}'] = value
    return payload


@pytest.mark.django_db
def test_master_data_forms_use_toggle_labels_and_placeholders():
    company_form = CompanyProfileForm()
    bank_account_form = BankAccountForm()
    client_form = ClientForm()
    quote_item_form = QuoteInlineItemForm(prefix='items-0')

    assert company_form.fields['is_default'].label == '標準の発行元として使う'
    assert bank_account_form.fields['is_default'].label == '標準の振込先口座として使う'
    assert client_form.fields['is_active'].label == '見積・請求で利用する'

    assert company_form.fields['name'].widget.attrs['placeholder'] == '例: 株式会社サンプル'
    assert bank_account_form.fields['account_number'].widget.attrs['placeholder'] == '例: 1234567'
    assert client_form.fields['payment_terms_days'].widget.attrs['placeholder'] == '例: 30'
    assert '請求日から何日後' in client_form.fields['payment_terms_days'].help_text
    assert '明細番号と同じ値が自動で入ります' in quote_item_form.fields['display_order'].help_text
    assert quote_item_form.fields['display_order'].widget.attrs['readonly'] is True
    assert '時間 / 件 / 本 / 月 / 式' in quote_item_form.fields['unit_label'].help_text
    assert quote_item_form.fields['unit_label'].widget.attrs['placeholder'] == '例: 時間 / 件 / 月 / 式'


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['billing:quote-create', 'billing:invoice-create'])
def test_document_create_views_initially_show_one_detail_form(logged_in_client, url_name):
    response = logged_in_client.get(reverse(url_name))

    assert response.status_code == 200
    item_formset = response.context['item_formset']
    visible_forms = [form for form in item_formset.forms if getattr(form, 'is_displayed', False)]
    assert len(visible_forms) == 1
    assert '明細を追加' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_quote_create_view_keeps_only_visible_detail_rows_after_parent_form_error(logged_in_client, document_records):
    post_data = {
        'company_profile': str(document_records['company'].pk),
        'project': str(document_records['project'].pk),
        'quote_number': 'Q-REQ-002',
        'title': '',
        'issue_date': '2026-04-01',
        'valid_until': '2026-04-30',
        'status': 'draft',
        'currency': 'JPY',
        'tax_rate': '10.00',
        'terms': '',
        'notes': '',
        'sent_at': '',
        'approved_at': '',
        'items-TOTAL_FORMS': '10',
        'items-INITIAL_FORMS': '0',
        'items-MIN_NUM_FORMS': '0',
        'items-MAX_NUM_FORMS': '10',
    }

    for index in range(10):
        post_data[f'items-{index}-VISIBLE'] = '1' if index == 0 else '0'
        post_data[f'items-{index}-display_order'] = str(index + 1)
        post_data[f'items-{index}-description'] = '設計' if index == 0 else ''
        post_data[f'items-{index}-unit_label'] = '式' if index == 0 else ''
        post_data[f'items-{index}-quantity'] = '1.00' if index == 0 else ''
        post_data[f'items-{index}-unit_price'] = '10000.00' if index == 0 else ''
        post_data[f'items-{index}-notes'] = ''

    response = logged_in_client.post(reverse('billing:quote-create'), post_data)

    assert response.status_code == 200
    visible_forms = [form for form in response.context['item_formset'].forms if getattr(form, 'is_displayed', False)]
    assert len(visible_forms) == 1


@pytest.mark.django_db
def test_company_profile_create_view_renders_switch_ui(logged_in_client):
    response = logged_in_client.get(reverse('billing:company-profile-create'))
    content = response.content.decode('utf-8')

    assert response.status_code == 200
    assert '標準の発行元として使う' in content
    assert 'peer sr-only' in content


@pytest.mark.django_db
def test_quote_create_view_requires_at_least_one_visible_detail(logged_in_client, document_records):
    post_data = {
        'company_profile': str(document_records['company'].pk),
        'project': str(document_records['project'].pk),
        'quote_number': 'Q-REQ-001',
        'title': '明細必須確認',
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
    post_data.update(build_formset_payload('items', []))

    response = logged_in_client.post(reverse('billing:quote-create'), post_data)

    assert response.status_code == 200
    assert response.context['item_formset'].non_form_errors()
    assert '少なくとも1件の明細' in response.content.decode('utf-8')


