from billing.forms import PaymentForm
from billing.models import Payment

from .crud_view import BaseRecordCreateView, BaseRecordDeleteView, BaseRecordListView, BaseRecordUpdateView


class PaymentListView(BaseRecordListView):
    model = Payment
    model_label = '入金'
    model_label_plural = '入金'
    page_badge = 'Transaction data'
    page_description = '請求書に対する入金記録を、ステータス単位のページで管理します。'
    list_url_name = 'billing:payment-list'
    status_url_name = 'billing:payment-status-list'
    create_url_name = 'billing:payment-create'
    update_url_name = 'billing:payment-update'
    delete_url_name = 'billing:payment-delete'
    status_field = 'status'
    table_fields = (
        ('invoice', '請求書'),
        ('received_on', '入金日'),
        ('amount', '入金額'),
        ('status', 'ステータス'),
        ('method', '入金方法'),
    )


class PaymentCreateView(BaseRecordCreateView):
    model = Payment
    form_class = PaymentForm
    model_label = '入金'
    page_badge = 'Transaction data'
    page_description = '請求書に対する入金情報を登録します。'
    list_url_name = 'billing:payment-list'
    status_url_name = 'billing:payment-status-list'
    status_field = 'status'


class PaymentUpdateView(BaseRecordUpdateView):
    model = Payment
    form_class = PaymentForm
    model_label = '入金'
    page_badge = 'Transaction data'
    page_description = '既存の入金記録を更新します。'
    list_url_name = 'billing:payment-list'
    status_url_name = 'billing:payment-status-list'
    status_field = 'status'


class PaymentDeleteView(BaseRecordDeleteView):
    model = Payment
    model_label = '入金'
    page_badge = 'Transaction data'
    page_description = '既存の入金記録を削除します。'
    list_url_name = 'billing:payment-list'
    status_url_name = 'billing:payment-status-list'
    status_field = 'status'
