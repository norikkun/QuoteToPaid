from billing.forms import MAX_ITEMS_PER_DOCUMENT, InvoiceForm, InvoiceItemInlineFormSet
from billing.models import Invoice

from .crud_view import (
    BaseRecordCreateWithItemFormSetView,
    BaseRecordDeleteView,
    BaseRecordListView,
    BaseRecordUpdateWithItemFormSetView,
)


class InvoiceListView(BaseRecordListView):
    model = Invoice
    model_label = '請求書'
    model_label_plural = '請求書'
    page_badge = 'Transaction data'
    page_description = '請求書の発行状況と支払期限を、ステータス単位のページで管理します。請求明細は登録・編集画面でまとめて管理します。'
    list_url_name = 'billing:invoice-list'
    status_url_name = 'billing:invoice-status-list'
    create_url_name = 'billing:invoice-create'
    update_url_name = 'billing:invoice-update'
    delete_url_name = 'billing:invoice-delete'
    status_field = 'status'
    table_fields = (
        ('invoice_number', '請求番号'),
        ('project', '案件'),
        ('due_date', '支払期限'),
        ('status', 'ステータス'),
        ('total_amount', '合計'),
    )


class InvoiceCreateView(BaseRecordCreateWithItemFormSetView):
    model = Invoice
    form_class = InvoiceForm
    model_label = '請求書'
    page_badge = 'Transaction data'
    page_description = '案件または見積書を元に、請求書と請求明細をこの1画面でまとめて登録します。明細は最初に1件だけ表示されます。'
    list_url_name = 'billing:invoice-list'
    status_url_name = 'billing:invoice-status-list'
    status_field = 'status'
    item_formset_class = InvoiceItemInlineFormSet
    item_formset_title = '請求明細'
    item_formset_description = '表示している明細だけが保存対象です。非表示にした行は保存されません。1つの請求書に対して最大10件まで登録できます。'
    item_formset_limit = MAX_ITEMS_PER_DOCUMENT


class InvoiceUpdateView(BaseRecordUpdateWithItemFormSetView):
    model = Invoice
    form_class = InvoiceForm
    model_label = '請求書'
    page_badge = 'Transaction data'
    page_description = '既存の請求書と請求明細を、この1画面でまとめて更新します。'
    list_url_name = 'billing:invoice-list'
    status_url_name = 'billing:invoice-status-list'
    status_field = 'status'
    item_formset_class = InvoiceItemInlineFormSet
    item_formset_title = '請求明細'
    item_formset_description = '表示している明細だけが有効です。不要な行は非表示にすると削除対象として扱います。最大10件まで管理できます。'
    item_formset_limit = MAX_ITEMS_PER_DOCUMENT


class InvoiceDeleteView(BaseRecordDeleteView):
    model = Invoice
    model_label = '請求書'
    page_badge = 'Transaction data'
    page_description = '入金や催促の親になる請求書を削除します。'
    list_url_name = 'billing:invoice-list'
    status_url_name = 'billing:invoice-status-list'
    status_field = 'status'
