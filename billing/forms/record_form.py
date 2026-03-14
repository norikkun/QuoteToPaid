from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

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

from .base_form import StyledFormMixin

MAX_ITEMS_PER_DOCUMENT = 10
DISPLAY_ORDER_HELP_TEXT = '明細番号と同じ値が自動で入ります。帳票の上から 1, 2, 3... の順に並びます。'
UNIT_LABEL_HELP_TEXT = '数量の単位を入力します。例: 時間 / 件 / 本 / 月 / 式。作業一式なら「式」、時間課金なら「時間」です。'


class ToggleCopyMixin:
    toggle_labels = {}
    toggle_help_texts = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, label in self.toggle_labels.items():
            if field_name in self.fields:
                self.fields[field_name].label = label
        for field_name, help_text in self.toggle_help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text



class AutoNumberedItemFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'display_order' in self.fields:
            self.fields['display_order'].widget.attrs['readonly'] = True

class CompanyProfileForm(ToggleCopyMixin, StyledFormMixin, forms.ModelForm):
    toggle_labels = {
        'is_default': '標準の発行元として使う',
    }
    toggle_help_texts = {
        'is_default': 'オンにすると、見積書や請求書で最初に選ばれる自社情報になります。',
    }

    class Meta:
        model = CompanyProfile
        fields = (
            'name',
            'legal_name',
            'invoice_registration_number',
            'email',
            'phone',
            'postal_code',
            'address',
            'website',
            'notes',
            'is_default',
        )


class BankAccountForm(ToggleCopyMixin, StyledFormMixin, forms.ModelForm):
    toggle_labels = {
        'is_default': '標準の振込先口座として使う',
    }
    toggle_help_texts = {
        'is_default': 'オンにすると、同じ自社情報に紐づく他の口座は自動でオフになり、この口座が請求書で最初に選ばれます。',
    }

    class Meta:
        model = BankAccount
        fields = (
            'company_profile',
            'nickname',
            'bank_name',
            'branch_name',
            'account_type',
            'account_number',
            'account_holder',
            'is_default',
        )


class ClientForm(ToggleCopyMixin, StyledFormMixin, forms.ModelForm):
    toggle_labels = {
        'is_active': '見積・請求で利用する',
    }
    toggle_help_texts = {
        'is_active': 'オンにすると、新しい案件や帳票の作成時に取引先候補として利用できます。',
    }

    class Meta:
        model = Client
        fields = (
            'name',
            'legal_name',
            'contact_person',
            'email',
            'phone',
            'postal_code',
            'address',
            'invoice_registration_number',
            'payment_terms_days',
            'notes',
            'is_active',
        )
        help_texts = {
            'payment_terms_days': '請求日から何日後を支払期限の目安にするかを入力します。例: 30 なら「請求日の30日後」です。',
        }


class ProjectForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'client',
            'name',
            'code',
            'status',
            'description',
            'start_date',
            'end_date',
            'notes',
        )


class QuoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Quote
        fields = (
            'company_profile',
            'project',
            'quote_number',
            'title',
            'issue_date',
            'valid_until',
            'status',
            'currency',
            'tax_rate',
            'terms',
            'notes',
            'sent_at',
            'approved_at',
        )


class QuoteItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = (
            'quote',
            'display_order',
            'description',
            'unit_label',
            'quantity',
            'unit_price',
            'notes',
        )
        help_texts = {
            'display_order': DISPLAY_ORDER_HELP_TEXT,
            'unit_label': UNIT_LABEL_HELP_TEXT,
            'unit_price': '金額は「数量 x 単価」から自動計算されます。',
        }

    def clean_quote(self):
        quote = self.cleaned_data['quote']
        if quote and not self.instance.pk and quote.items.count() >= MAX_ITEMS_PER_DOCUMENT:
            raise forms.ValidationError('見積書ごとの明細は10件まで登録できます。')
        return quote


class QuoteInlineItemForm(AutoNumberedItemFormMixin, StyledFormMixin, forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = (
            'display_order',
            'description',
            'unit_label',
            'quantity',
            'unit_price',
            'notes',
        )
        help_texts = {
            'display_order': DISPLAY_ORDER_HELP_TEXT,
            'unit_label': UNIT_LABEL_HELP_TEXT,
            'unit_price': '数量と単価から、この行の金額をリアルタイムで表示します。',
        }


class InvoiceForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            'company_profile',
            'bank_account',
            'project',
            'quote',
            'invoice_number',
            'title',
            'issue_date',
            'due_date',
            'status',
            'currency',
            'tax_rate',
            'notes',
            'sent_at',
        )


class InvoiceItemForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = (
            'invoice',
            'quote_item',
            'display_order',
            'description',
            'unit_label',
            'quantity',
            'unit_price',
            'notes',
        )
        help_texts = {
            'display_order': DISPLAY_ORDER_HELP_TEXT,
            'unit_label': UNIT_LABEL_HELP_TEXT,
            'unit_price': '金額は「数量 x 単価」から自動計算されます。',
        }

    def clean_invoice(self):
        invoice = self.cleaned_data['invoice']
        if invoice and not self.instance.pk and invoice.items.count() >= MAX_ITEMS_PER_DOCUMENT:
            raise forms.ValidationError('請求書ごとの明細は10件まで登録できます。')
        return invoice


class InvoiceInlineItemForm(AutoNumberedItemFormMixin, StyledFormMixin, forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = (
            'quote_item',
            'display_order',
            'description',
            'unit_label',
            'quantity',
            'unit_price',
            'notes',
        )
        help_texts = {
            'display_order': DISPLAY_ORDER_HELP_TEXT,
            'unit_label': UNIT_LABEL_HELP_TEXT,
            'unit_price': '数量と単価から、この行の金額をリアルタイムで表示します。',
        }


class PaymentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = (
            'invoice',
            'received_on',
            'amount',
            'fee_amount',
            'method',
            'status',
            'reference_number',
            'notes',
        )


class ReminderLogForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = ReminderLog
        fields = (
            'invoice',
            'reminded_at',
            'method',
            'recipient',
            'subject',
            'body',
            'status',
            'next_follow_up_on',
            'notes',
        )


class BaseLimitedItemInlineFormSet(BaseInlineFormSet):
    max_items = MAX_ITEMS_PER_DOCUMENT

    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'display_order' in form.fields and not form.instance.pk:
            form.fields['display_order'].initial = (index or 0) + 1

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        active_forms = []
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            if form.instance.pk:
                active_forms.append(form)
                continue

            has_input = any(
                form.cleaned_data.get(field_name) not in (None, '', [])
                for field_name in form.fields
                if field_name != 'DELETE'
            )
            if has_input:
                active_forms.append(form)

        if not active_forms:
            raise forms.ValidationError('少なくとも1件の明細を表示したまま保存してください。')
        if len(active_forms) > self.max_items:
            raise forms.ValidationError(f'明細は1帳票あたり最大{self.max_items}件まで登録できます。')


QuoteItemInlineFormSet = inlineformset_factory(
    Quote,
    QuoteItem,
    form=QuoteInlineItemForm,
    formset=BaseLimitedItemInlineFormSet,
    extra=MAX_ITEMS_PER_DOCUMENT,
    can_delete=True,
    max_num=MAX_ITEMS_PER_DOCUMENT,
    validate_max=True,
)


InvoiceItemInlineFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceInlineItemForm,
    formset=BaseLimitedItemInlineFormSet,
    extra=MAX_ITEMS_PER_DOCUMENT,
    can_delete=True,
    max_num=MAX_ITEMS_PER_DOCUMENT,
    validate_max=True,
)

