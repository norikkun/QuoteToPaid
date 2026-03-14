from billing.forms import ProjectForm
from billing.models import Project

from .crud_view import BaseRecordCreateView, BaseRecordDeleteView, BaseRecordListView, BaseRecordUpdateView


class ProjectListView(BaseRecordListView):
    model = Project
    model_label = '案件'
    model_label_plural = '案件'
    page_badge = 'Transaction data'
    page_description = '取引先ごとの案件を、ステータス単位のページで管理します。'
    list_url_name = 'billing:project-list'
    status_url_name = 'billing:project-status-list'
    create_url_name = 'billing:project-create'
    update_url_name = 'billing:project-update'
    delete_url_name = 'billing:project-delete'
    status_field = 'status'
    table_fields = (
        ('client', '取引先'),
        ('name', '案件名'),
        ('status', 'ステータス'),
        ('start_date', '開始日'),
        ('end_date', '終了日'),
    )


class ProjectCreateView(BaseRecordCreateView):
    model = Project
    form_class = ProjectForm
    model_label = '案件'
    page_badge = 'Transaction data'
    page_description = '見積書と請求書の親になる案件を登録します。'
    list_url_name = 'billing:project-list'
    status_url_name = 'billing:project-status-list'
    status_field = 'status'


class ProjectUpdateView(BaseRecordUpdateView):
    model = Project
    form_class = ProjectForm
    model_label = '案件'
    page_badge = 'Transaction data'
    page_description = '既存の案件情報を更新します。'
    list_url_name = 'billing:project-list'
    status_url_name = 'billing:project-status-list'
    status_field = 'status'


class ProjectDeleteView(BaseRecordDeleteView):
    model = Project
    model_label = '案件'
    page_badge = 'Transaction data'
    page_description = '見積書や請求書の親になる案件を削除します。'
    list_url_name = 'billing:project-list'
    status_url_name = 'billing:project-status-list'
    status_field = 'status'
    protected_error_message = '関連する見積書または請求書があるため削除できません。'
