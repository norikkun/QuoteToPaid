from django.urls import reverse_lazy
from django.views.generic import TemplateView

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

from .base_view import AppLoginRequiredMixin


class DashboardTemplateView(AppLoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('billing:login')
    template_name = 'billing/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        company_count = CompanyProfile.objects.count()
        bank_account_count = BankAccount.objects.count()
        client_count = Client.objects.count()
        project_count = Project.objects.count()
        quote_count = Quote.objects.count()
        quote_item_count = QuoteItem.objects.count()
        invoice_count = Invoice.objects.count()
        invoice_item_count = InvoiceItem.objects.count()
        payment_count = Payment.objects.count()
        reminder_log_count = ReminderLog.objects.count()

        workflow_steps = [
            {
                'step': '01',
                'title': '取引先を登録',
                'description': '最初に請求先となる取引先を1件登録します。',
                'summary': f'取引先 {client_count}件',
                'status': '完了' if client_count else '未着手',
                'status_tone': 'emerald' if client_count else 'amber',
                'primary_label': '取引先一覧へ',
                'primary_url': reverse_lazy('billing:client-list'),
                'secondary_label': '登録画面へ',
                'secondary_url': reverse_lazy('billing:client-create'),
            },
            {
                'step': '02',
                'title': '案件を作成',
                'description': '登録した取引先に対して、対象案件を作成します。',
                'summary': f'案件 {project_count}件',
                'status': '完了' if project_count else '未着手',
                'status_tone': 'emerald' if project_count else 'amber',
                'primary_label': '案件一覧へ',
                'primary_url': reverse_lazy('billing:project-list'),
                'secondary_label': '登録画面へ',
                'secondary_url': reverse_lazy('billing:project-create'),
            },
            {
                'step': '03',
                'title': '見積を作成',
                'description': '案件に対する見積書と見積明細を1回のフォーム入力でまとめて作成します。',
                'summary': f'見積書 {quote_count}件 / 明細 {quote_item_count}件',
                'status': '完了' if quote_count and quote_item_count else '進行中' if quote_count or quote_item_count else '未着手',
                'status_tone': 'emerald' if quote_count and quote_item_count else 'sky' if quote_count or quote_item_count else 'amber',
                'primary_label': '見積書一覧へ',
                'primary_url': reverse_lazy('billing:quote-list'),
                'secondary_label': '見積書を登録',
                'secondary_url': reverse_lazy('billing:quote-create'),
            },
            {
                'step': '04',
                'title': '請求を起票',
                'description': '見積内容をもとに請求書と請求明細を1回のフォーム入力でまとめて作成します。',
                'summary': f'請求書 {invoice_count}件 / 明細 {invoice_item_count}件',
                'status': '完了' if invoice_count and invoice_item_count else '進行中' if invoice_count or invoice_item_count else '未着手',
                'status_tone': 'emerald' if invoice_count and invoice_item_count else 'sky' if invoice_count or invoice_item_count else 'amber',
                'primary_label': '請求書一覧へ',
                'primary_url': reverse_lazy('billing:invoice-list'),
                'secondary_label': '請求書を登録',
                'secondary_url': reverse_lazy('billing:invoice-create'),
            },
            {
                'step': '05',
                'title': '入金を記録',
                'description': '実際の入金を記録して、請求の回収状況を追跡します。',
                'summary': f'入金 {payment_count}件',
                'status': '完了' if payment_count else '未着手',
                'status_tone': 'emerald' if payment_count else 'amber',
                'primary_label': '入金一覧へ',
                'primary_url': reverse_lazy('billing:payment-list'),
                'secondary_label': '登録画面へ',
                'secondary_url': reverse_lazy('billing:payment-create'),
            },
        ]

        if not client_count:
            next_action = '最初の1件として取引先を登録すると、このあと案件、見積、請求へ進めます。'
        elif not project_count:
            next_action = '次は案件を1件作成してください。取引先に紐づく案件が見積と請求の起点になります。'
        elif not (quote_count and quote_item_count):
            next_action = '次は見積書を登録してください。この画面で見積明細までまとめて入力できます。'
        elif not (invoice_count and invoice_item_count):
            next_action = '次は請求書を登録してください。この画面で請求明細までまとめて入力できます。'
        elif not payment_count:
            next_action = '次は入金を記録してください。未入金の場合は催促履歴も併用できます。'
        else:
            next_action = '一連の流れは作成済みです。未入金対応が必要な場合は催促履歴を活用してください。'

        context.update(
            {
                'page_title': 'QuoteToPaid',
                'project_name': 'QuoteToPaid',
                'next_action': next_action,
                'workflow_steps': workflow_steps,
                'dashboard_sections': [
                    {
                        'title': '自社情報と銀行口座',
                        'description': '発行元情報と請求書に載せる振込先口座をまとめて管理します。',
                        'accent': 'emerald',
                        'items': [
                            {
                                'label': '自社情報',
                                'count': company_count,
                                'url': reverse_lazy('billing:company-profile-list'),
                            },
                            {
                                'label': '銀行口座',
                                'count': bank_account_count,
                                'url': reverse_lazy('billing:bank-account-list'),
                            },
                        ],
                    },
                    {
                        'title': '取引先',
                        'description': '案件と見積・請求の起点になる取引先情報を管理します。',
                        'accent': 'sky',
                        'items': [
                            {
                                'label': '取引先',
                                'count': client_count,
                                'url': reverse_lazy('billing:client-list'),
                            },
                        ],
                    },
                    {
                        'title': '案件',
                        'description': '取引先ごとの案件を管理し、見積と請求の親データにします。',
                        'accent': 'amber',
                        'items': [
                            {
                                'label': '案件',
                                'count': project_count,
                                'url': reverse_lazy('billing:project-list'),
                            },
                        ],
                    },
                    {
                        'title': '見積書と見積明細',
                        'description': '見積書の登録・編集画面で、見積明細までまとめて管理します。',
                        'accent': 'emerald',
                        'items': [
                            {
                                'label': '見積書',
                                'count': quote_count,
                                'url': reverse_lazy('billing:quote-list'),
                                'meta': f'見積明細 {quote_item_count}件',
                                'note': '明細は見積書フォーム内で管理します。',
                            },
                        ],
                    },
                    {
                        'title': '請求書と請求明細',
                        'description': '請求書の登録・編集画面で、請求明細までまとめて管理します。',
                        'accent': 'sky',
                        'items': [
                            {
                                'label': '請求書',
                                'count': invoice_count,
                                'url': reverse_lazy('billing:invoice-list'),
                                'meta': f'請求明細 {invoice_item_count}件',
                                'note': '明細は請求書フォーム内で管理します。',
                            },
                        ],
                    },
                    {
                        'title': '入金と催促履歴',
                        'description': '入金確認と未入金フォローを同じまとまりで管理します。',
                        'accent': 'rose',
                        'items': [
                            {
                                'label': '入金',
                                'count': payment_count,
                                'url': reverse_lazy('billing:payment-list'),
                            },
                            {
                                'label': '催促履歴',
                                'count': reminder_log_count,
                                'url': reverse_lazy('billing:reminder-log-list'),
                            },
                        ],
                    },
                ],
            }
        )
        return context
