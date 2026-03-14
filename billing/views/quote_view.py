from billing.forms import MAX_ITEMS_PER_DOCUMENT, QuoteForm, QuoteItemInlineFormSet
from billing.models import Quote

from .crud_view import (
    BaseRecordCreateWithItemFormSetView,
    BaseRecordDeleteView,
    BaseRecordListView,
    BaseRecordUpdateWithItemFormSetView,
)


class QuoteListView(BaseRecordListView):
    model = Quote
    model_label = '見積書'
    model_label_plural = '見積書'
    page_badge = 'Transaction data'
    page_description = '案件ごとの見積書を、ステータス単位のページで管理します。見積明細は登録・編集画面でまとめて管理します。'
    list_url_name = 'billing:quote-list'
    status_url_name = 'billing:quote-status-list'
    create_url_name = 'billing:quote-create'
    update_url_name = 'billing:quote-update'
    delete_url_name = 'billing:quote-delete'
    status_field = 'status'
    table_fields = (
        ('quote_number', '見積番号'),
        ('project', '案件'),
        ('issue_date', '発行日'),
        ('status', 'ステータス'),
        ('total_amount', '合計'),
    )


class QuoteCreateView(BaseRecordCreateWithItemFormSetView):
    model = Quote
    form_class = QuoteForm
    model_label = '見積書'
    page_badge = 'Transaction data'
    page_description = '案件に対する見積書と見積明細を、この1画面でまとめて登録します。明細は最初に1件だけ表示されます。'
    list_url_name = 'billing:quote-list'
    status_url_name = 'billing:quote-status-list'
    status_field = 'status'
    item_formset_class = QuoteItemInlineFormSet
    item_formset_title = '見積明細'
    item_formset_description = '表示している明細だけが保存対象です。非表示にした行は保存されません。1つの見積書に対して最大10件まで登録できます。'
    item_formset_limit = MAX_ITEMS_PER_DOCUMENT


class QuoteUpdateView(BaseRecordUpdateWithItemFormSetView):
    model = Quote
    form_class = QuoteForm
    model_label = '見積書'
    page_badge = 'Transaction data'
    page_description = '既存の見積書と見積明細を、この1画面でまとめて更新します。'
    list_url_name = 'billing:quote-list'
    status_url_name = 'billing:quote-status-list'
    status_field = 'status'
    item_formset_class = QuoteItemInlineFormSet
    item_formset_title = '見積明細'
    item_formset_description = '表示している明細だけが有効です。不要な行は非表示にすると削除対象として扱います。最大10件まで管理できます。'
    item_formset_limit = MAX_ITEMS_PER_DOCUMENT


class QuoteDeleteView(BaseRecordDeleteView):
    model = Quote
    model_label = '見積書'
    page_badge = 'Transaction data'
    page_description = '既存の見積書を削除します。'
    list_url_name = 'billing:quote-list'
    status_url_name = 'billing:quote-status-list'
    status_field = 'status'
