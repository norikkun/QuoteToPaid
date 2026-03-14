from billing.forms import BankAccountForm, ClientForm, CompanyProfileForm
from billing.models import BankAccount, Client, CompanyProfile

from .crud_view import BaseRecordCreateView, BaseRecordDeleteView, BaseRecordListView, BaseRecordUpdateView


class CompanyProfileListView(BaseRecordListView):
    model = CompanyProfile
    model_label = '自社情報'
    model_label_plural = '自社情報'
    page_badge = 'Master data'
    page_description = '見積書と請求書の発行元として使う自社情報を管理します。'
    list_url_name = 'billing:company-profile-list'
    create_url_name = 'billing:company-profile-create'
    update_url_name = 'billing:company-profile-update'
    delete_url_name = 'billing:company-profile-delete'
    table_fields = (
        ('name', '表示名'),
        ('legal_name', '正式名称'),
        ('invoice_registration_number', '登録番号'),
        ('is_default', '既定'),
    )


class CompanyProfileCreateView(BaseRecordCreateView):
    model = CompanyProfile
    form_class = CompanyProfileForm
    model_label = '自社情報'
    page_badge = 'Master data'
    page_description = '見積書と請求書の発行元として使う自社情報を登録します。'
    list_url_name = 'billing:company-profile-list'


class CompanyProfileUpdateView(BaseRecordUpdateView):
    model = CompanyProfile
    form_class = CompanyProfileForm
    model_label = '自社情報'
    page_badge = 'Master data'
    page_description = '既存の自社情報を更新します。'
    list_url_name = 'billing:company-profile-list'


class CompanyProfileDeleteView(BaseRecordDeleteView):
    model = CompanyProfile
    model_label = '自社情報'
    page_badge = 'Master data'
    page_description = '見積書や請求書の発行元として使う自社情報を削除します。'
    list_url_name = 'billing:company-profile-list'
    protected_error_message = '関連する見積書または請求書があるため削除できません。'


class BankAccountListView(BaseRecordListView):
    model = BankAccount
    model_label = '銀行口座'
    model_label_plural = '銀行口座'
    page_badge = 'Master data'
    page_description = '請求書に記載する振込先口座を管理します。'
    list_url_name = 'billing:bank-account-list'
    create_url_name = 'billing:bank-account-create'
    update_url_name = 'billing:bank-account-update'
    delete_url_name = 'billing:bank-account-delete'
    table_fields = (
        ('company_profile', '自社情報'),
        ('nickname', '口座名'),
        ('bank_name', '銀行名'),
        ('account_number', '口座番号'),
        ('is_default', '既定'),
    )


class BankAccountCreateView(BaseRecordCreateView):
    model = BankAccount
    form_class = BankAccountForm
    model_label = '銀行口座'
    page_badge = 'Master data'
    page_description = '請求書に記載する振込先口座を登録します。'
    list_url_name = 'billing:bank-account-list'


class BankAccountUpdateView(BaseRecordUpdateView):
    model = BankAccount
    form_class = BankAccountForm
    model_label = '銀行口座'
    page_badge = 'Master data'
    page_description = '既存の銀行口座を更新します。'
    list_url_name = 'billing:bank-account-list'


class BankAccountDeleteView(BaseRecordDeleteView):
    model = BankAccount
    model_label = '銀行口座'
    page_badge = 'Master data'
    page_description = '振込先として使う銀行口座を削除します。'
    list_url_name = 'billing:bank-account-list'


class ClientListView(BaseRecordListView):
    model = Client
    model_label = '取引先'
    model_label_plural = '取引先'
    page_badge = 'Master data'
    page_description = '案件、見積書、請求書の起点になる取引先を管理します。'
    list_url_name = 'billing:client-list'
    create_url_name = 'billing:client-create'
    update_url_name = 'billing:client-update'
    delete_url_name = 'billing:client-delete'
    table_fields = (
        ('name', '取引先名'),
        ('contact_person', '担当者'),
        ('email', 'メール'),
        ('payment_terms_days', '支払サイト'),
        ('is_active', '有効'),
    )


class ClientCreateView(BaseRecordCreateView):
    model = Client
    form_class = ClientForm
    model_label = '取引先'
    page_badge = 'Master data'
    page_description = '案件の発生元となる取引先を登録します。'
    list_url_name = 'billing:client-list'


class ClientUpdateView(BaseRecordUpdateView):
    model = Client
    form_class = ClientForm
    model_label = '取引先'
    page_badge = 'Master data'
    page_description = '既存の取引先情報を更新します。'
    list_url_name = 'billing:client-list'


class ClientDeleteView(BaseRecordDeleteView):
    model = Client
    model_label = '取引先'
    page_badge = 'Master data'
    page_description = '案件の起点となる取引先を削除します。'
    list_url_name = 'billing:client-list'
    protected_error_message = '関連する案件があるため削除できません。'
