from django.contrib import admin

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


class BankAccountInline(admin.TabularInline):
    model = BankAccount
    extra = 0


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'invoice_registration_number', 'is_default', 'updated_at')
    search_fields = ('name', 'legal_name', 'invoice_registration_number')
    list_filter = ('is_default',)
    inlines = [BankAccountInline]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'payment_terms_days', 'is_active')
    search_fields = ('name', 'legal_name', 'contact_person', 'email')
    list_filter = ('is_active',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'status', 'start_date', 'end_date')
    search_fields = ('name', 'code', 'client__name')
    list_filter = ('status',)


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'title', 'project', 'status', 'issue_date', 'total_amount')
    search_fields = ('quote_number', 'title', 'project__name', 'project__client__name')
    list_filter = ('status', 'issue_date')
    inlines = [QuoteItemInline]


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class ReminderLogInline(admin.TabularInline):
    model = ReminderLog
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'title', 'project', 'status', 'issue_date', 'due_date', 'total_amount')
    search_fields = ('invoice_number', 'title', 'project__name', 'project__client__name')
    list_filter = ('status', 'issue_date', 'due_date')
    inlines = [InvoiceItemInline, PaymentInline, ReminderLogInline]
