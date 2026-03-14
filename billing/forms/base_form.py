from django import forms

INPUT_CLASSES = (
    'mt-2 block w-full rounded-2xl border border-white/10 bg-stone-900/70 px-4 py-3 '
    'text-sm text-stone-100 placeholder:text-stone-500 focus:border-emerald-300 '
    'focus:outline-none focus:ring-2 focus:ring-emerald-300/30'
)

SELECT_CLASSES = (
    'mt-2 block w-full rounded-2xl border border-white/10 bg-stone-900/70 px-4 py-3 '
    'text-sm text-stone-100 focus:border-emerald-300 focus:outline-none '
    'focus:ring-2 focus:ring-emerald-300/30'
)

TEXTAREA_CLASSES = (
    'mt-2 block w-full rounded-2xl border border-white/10 bg-stone-900/70 px-4 py-3 '
    'text-sm text-stone-100 placeholder:text-stone-500 focus:border-emerald-300 '
    'focus:outline-none focus:ring-2 focus:ring-emerald-300/30'
)

CHECKBOX_CLASSES = 'peer sr-only'

PLACEHOLDER_EXAMPLES = {
    'name': '例: 株式会社サンプル',
    'legal_name': '例: 株式会社QuoteToPaid',
    'invoice_registration_number': '例: T1234567890123',
    'email': '例: billing@example.com',
    'phone': '例: 03-1234-5678',
    'postal_code': '例: 150-0001',
    'address': '例: 東京都渋谷区渋谷1-2-3',
    'website': '例: https://quotetopaid.example.com',
    'notes': '例: 補足事項があれば入力してください',
    'nickname': '例: メイン口座',
    'bank_name': '例: みずほ銀行',
    'branch_name': '例: 渋谷支店',
    'account_number': '例: 1234567',
    'account_holder': '例: カ)クオートトゥペイド',
    'contact_person': '例: 田中 太郎',
    'payment_terms_days': '例: 30',
    'code': '例: QT-2026-001',
    'description': '例: Webサイト制作一式',
    'quote_number': '例: Q-2026-0001',
    'invoice_number': '例: INV-2026-0001',
    'title': '例: 2026年4月分 開発費',
    'tax_rate': '例: 10.00',
    'terms': '例: 月末締め翌月末払い',
    'display_order': '例: 1',
    'unit_label': '例: 時間 / 件 / 月 / 式',
    'quantity': '例: 2.00',
    'unit_price': '例: 50000.00',
    'amount': '例: 110000.00',
    'fee_amount': '例: 330.00',
    'reference_number': '例: PAY-2026-0001',
    'recipient': '例: billing@example.com',
    'subject': '例: お支払い期日のご確認',
    'body': '例: ご請求内容をご確認のうえ、ご対応をお願いいたします。',
}


class StyledFormMixin:
    date_input_format = '%Y-%m-%d'
    datetime_input_format = '%Y-%m-%dT%H:%M'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            self._apply_widget(field_name, field)

    def _apply_widget(self, field_name, field):
        if isinstance(field, forms.DateTimeField):
            field.widget = forms.DateTimeInput(
                format=self.datetime_input_format,
                attrs={
                    'class': INPUT_CLASSES,
                    'type': 'datetime-local',
                },
            )
            field.input_formats = [self.datetime_input_format]
            return

        if isinstance(field, forms.DateField):
            field.widget = forms.DateInput(
                format=self.date_input_format,
                attrs={
                    'class': INPUT_CLASSES,
                    'type': 'date',
                },
            )
            field.input_formats = [self.date_input_format]
            return

        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs['class'] = CHECKBOX_CLASSES
            return

        if isinstance(field.widget, forms.Textarea):
            field.widget.attrs['class'] = TEXTAREA_CLASSES
            field.widget.attrs.setdefault('rows', 4)
            self._apply_placeholder(field_name, field)
            return

        if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
            field.widget.attrs['class'] = SELECT_CLASSES
            return

        field.widget.attrs['class'] = INPUT_CLASSES
        self._apply_placeholder(field_name, field)

    def _apply_placeholder(self, field_name, field):
        placeholder = PLACEHOLDER_EXAMPLES.get(field_name)
        if placeholder:
            field.widget.attrs.setdefault('placeholder', placeholder)

