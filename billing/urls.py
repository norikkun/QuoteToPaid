from django.urls import path

from .views.auth_view import UserLoginView, UserLogoutView, UserSetupView
from .views.invoice_view import InvoiceCreateView, InvoiceDeleteView, InvoiceListView, InvoiceUpdateView
from .views.master_data_view import (
    BankAccountCreateView,
    BankAccountDeleteView,
    BankAccountListView,
    BankAccountUpdateView,
    ClientCreateView,
    ClientDeleteView,
    ClientListView,
    ClientUpdateView,
    CompanyProfileCreateView,
    CompanyProfileDeleteView,
    CompanyProfileListView,
    CompanyProfileUpdateView,
)
from .views.pages_view import DashboardTemplateView
from .views.payment_view import PaymentCreateView, PaymentDeleteView, PaymentListView, PaymentUpdateView
from .views.project_view import ProjectCreateView, ProjectDeleteView, ProjectListView, ProjectUpdateView
from .views.quote_view import QuoteCreateView, QuoteDeleteView, QuoteListView, QuoteUpdateView
from .views.reminder_log_view import (
    ReminderLogCreateView,
    ReminderLogDeleteView,
    ReminderLogListView,
    ReminderLogUpdateView,
)
from .views.user_view import UserDeleteView, UserDetailView, UserUpdateView

app_name = 'billing'

urlpatterns = [
    path('', DashboardTemplateView.as_view(), name='dashboard'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('user/setup/', UserSetupView.as_view(), name='user-setup'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('user/edit/', UserUpdateView.as_view(), name='user-update'),
    path('user/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('company-profiles/', CompanyProfileListView.as_view(), name='company-profile-list'),
    path('company-profiles/create/', CompanyProfileCreateView.as_view(), name='company-profile-create'),
    path('company-profiles/<int:pk>/edit/', CompanyProfileUpdateView.as_view(), name='company-profile-update'),
    path('company-profiles/<int:pk>/delete/', CompanyProfileDeleteView.as_view(), name='company-profile-delete'),
    path('bank-accounts/', BankAccountListView.as_view(), name='bank-account-list'),
    path('bank-accounts/create/', BankAccountCreateView.as_view(), name='bank-account-create'),
    path('bank-accounts/<int:pk>/edit/', BankAccountUpdateView.as_view(), name='bank-account-update'),
    path('bank-accounts/<int:pk>/delete/', BankAccountDeleteView.as_view(), name='bank-account-delete'),
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/edit/', ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),
    path('projects/', ProjectListView.as_view(), name='project-list'),
    path('projects/status/<str:status>/', ProjectListView.as_view(), name='project-status-list'),
    path('projects/create/', ProjectCreateView.as_view(), name='project-create'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project-update'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project-delete'),
    path('quotes/', QuoteListView.as_view(), name='quote-list'),
    path('quotes/status/<str:status>/', QuoteListView.as_view(), name='quote-status-list'),
    path('quotes/create/', QuoteCreateView.as_view(), name='quote-create'),
    path('quotes/<int:pk>/edit/', QuoteUpdateView.as_view(), name='quote-update'),
    path('quotes/<int:pk>/delete/', QuoteDeleteView.as_view(), name='quote-delete'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/status/<str:status>/', InvoiceListView.as_view(), name='invoice-status-list'),
    path('invoices/create/', InvoiceCreateView.as_view(), name='invoice-create'),
    path('invoices/<int:pk>/edit/', InvoiceUpdateView.as_view(), name='invoice-update'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice-delete'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/status/<str:status>/', PaymentListView.as_view(), name='payment-status-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/edit/', PaymentUpdateView.as_view(), name='payment-update'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment-delete'),
    path('reminder-logs/', ReminderLogListView.as_view(), name='reminder-log-list'),
    path('reminder-logs/status/<str:status>/', ReminderLogListView.as_view(), name='reminder-log-status-list'),
    path('reminder-logs/create/', ReminderLogCreateView.as_view(), name='reminder-log-create'),
    path('reminder-logs/<int:pk>/edit/', ReminderLogUpdateView.as_view(), name='reminder-log-update'),
    path('reminder-logs/<int:pk>/delete/', ReminderLogDeleteView.as_view(), name='reminder-log-delete'),
]
