from billing.forms import ReminderLogForm
from billing.models import ReminderLog

from .crud_view import BaseRecordCreateView, BaseRecordDeleteView, BaseRecordListView, BaseRecordUpdateView


class ReminderLogListView(BaseRecordListView):
    model = ReminderLog
    model_label = '催促履歴'
    model_label_plural = '催促履歴'
    page_badge = 'Transaction data'
    page_description = '未入金請求に対する催促履歴を、ステータス単位のページで管理します。'
    list_url_name = 'billing:reminder-log-list'
    status_url_name = 'billing:reminder-log-status-list'
    create_url_name = 'billing:reminder-log-create'
    update_url_name = 'billing:reminder-log-update'
    delete_url_name = 'billing:reminder-log-delete'
    status_field = 'status'
    table_fields = (
        ('invoice', '請求書'),
        ('reminded_at', '催促日時'),
        ('method', '手段'),
        ('status', 'ステータス'),
        ('next_follow_up_on', '次回予定日'),
    )


class ReminderLogCreateView(BaseRecordCreateView):
    model = ReminderLog
    form_class = ReminderLogForm
    model_label = '催促履歴'
    page_badge = 'Transaction data'
    page_description = '未入金請求に対する催促履歴を登録します。'
    list_url_name = 'billing:reminder-log-list'
    status_url_name = 'billing:reminder-log-status-list'
    status_field = 'status'


class ReminderLogUpdateView(BaseRecordUpdateView):
    model = ReminderLog
    form_class = ReminderLogForm
    model_label = '催促履歴'
    page_badge = 'Transaction data'
    page_description = '既存の催促履歴を更新します。'
    list_url_name = 'billing:reminder-log-list'
    status_url_name = 'billing:reminder-log-status-list'
    status_field = 'status'


class ReminderLogDeleteView(BaseRecordDeleteView):
    model = ReminderLog
    model_label = '催促履歴'
    page_badge = 'Transaction data'
    page_description = '既存の催促履歴を削除します。'
    list_url_name = 'billing:reminder-log-list'
    status_url_name = 'billing:reminder-log-status-list'
    status_field = 'status'
