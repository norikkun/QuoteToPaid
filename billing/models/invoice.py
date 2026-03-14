from decimal import Decimal

from django.db import models

from .bank_account import BankAccount
from .choices import InvoiceStatus, PaymentStatus
from .company_profile import CompanyProfile
from .project import Project
from .quote import Quote
from .shared import TAX_RATE_DEFAULT, ZERO_DECIMAL, quantize_amount
from .time_stamped_model import TimeStampedModel


class Invoice(TimeStampedModel):
    company_profile = models.ForeignKey(
        CompanyProfile,
        verbose_name='自社情報',
        related_name='invoices',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    bank_account = models.ForeignKey(
        BankAccount,
        verbose_name='振込先口座',
        related_name='invoices',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(Project, verbose_name='案件', related_name='invoices', on_delete=models.PROTECT)
    quote = models.ForeignKey(Quote, verbose_name='元見積', related_name='invoices', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField('請求番号', max_length=50, unique=True)
    title = models.CharField('件名', max_length=255)
    issue_date = models.DateField('請求日')
    due_date = models.DateField('支払期限')
    status = models.CharField('ステータス', max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    currency = models.CharField('通貨', max_length=3, default='JPY')
    tax_rate = models.DecimalField('税率', max_digits=5, decimal_places=2, default=TAX_RATE_DEFAULT)
    subtotal_amount = models.DecimalField('小計', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    tax_amount = models.DecimalField('消費税', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    total_amount = models.DecimalField('合計', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    notes = models.TextField('備考', blank=True)
    sent_at = models.DateTimeField('送付日時', null=True, blank=True)

    class Meta:
        ordering = ['-issue_date', '-id']
        verbose_name = '請求書'
        verbose_name_plural = '請求書'
        indexes = [
            models.Index(fields=['status', 'due_date']),
        ]

    def __str__(self) -> str:
        return self.invoice_number

    @property
    def client(self):
        return self.project.client

    @property
    def paid_amount(self) -> Decimal:
        paid_total = sum(
            (payment.amount for payment in self.payments.filter(status=PaymentStatus.RECEIVED)),
            ZERO_DECIMAL,
        )
        return quantize_amount(paid_total, self.currency)

    @property
    def outstanding_amount(self) -> Decimal:
        return quantize_amount(max(self.total_amount - self.paid_amount, ZERO_DECIMAL), self.currency)

    def refresh_amounts(self, save: bool = True) -> None:
        subtotal = sum((item.total_amount for item in self.items.all()), ZERO_DECIMAL)
        subtotal = quantize_amount(subtotal, self.currency)
        tax = quantize_amount(subtotal * (self.tax_rate / Decimal('100')), self.currency)
        self.subtotal_amount = subtotal
        self.tax_amount = tax
        self.total_amount = quantize_amount(subtotal + tax, self.currency)
        if save:
            self.save(update_fields=['subtotal_amount', 'tax_amount', 'total_amount', 'updated_at'])
