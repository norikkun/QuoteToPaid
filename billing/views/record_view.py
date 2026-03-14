from .invoice_view import InvoiceCreateView, InvoiceDeleteView, InvoiceListView, InvoiceUpdateView
from .master_data_view import (
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
from .payment_view import PaymentCreateView, PaymentDeleteView, PaymentListView, PaymentUpdateView
from .project_view import ProjectCreateView, ProjectDeleteView, ProjectListView, ProjectUpdateView
from .quote_view import QuoteCreateView, QuoteDeleteView, QuoteListView, QuoteUpdateView
from .reminder_log_view import (
    ReminderLogCreateView,
    ReminderLogDeleteView,
    ReminderLogListView,
    ReminderLogUpdateView,
)

__all__ = [
    'BankAccountCreateView',
    'BankAccountDeleteView',
    'BankAccountListView',
    'BankAccountUpdateView',
    'ClientCreateView',
    'ClientDeleteView',
    'ClientListView',
    'ClientUpdateView',
    'CompanyProfileCreateView',
    'CompanyProfileDeleteView',
    'CompanyProfileListView',
    'CompanyProfileUpdateView',
    'InvoiceCreateView',
    'InvoiceDeleteView',
    'InvoiceListView',
    'InvoiceUpdateView',
    'PaymentCreateView',
    'PaymentDeleteView',
    'PaymentListView',
    'PaymentUpdateView',
    'ProjectCreateView',
    'ProjectDeleteView',
    'ProjectListView',
    'ProjectUpdateView',
    'QuoteCreateView',
    'QuoteDeleteView',
    'QuoteListView',
    'QuoteUpdateView',
    'ReminderLogCreateView',
    'ReminderLogDeleteView',
    'ReminderLogListView',
    'ReminderLogUpdateView',
]
