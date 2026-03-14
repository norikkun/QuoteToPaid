from decimal import Decimal

from django.db import models

from .choices import QuoteStatus
from .company_profile import CompanyProfile
from .project import Project
from .shared import TAX_RATE_DEFAULT, ZERO_DECIMAL, quantize_amount
from .time_stamped_model import TimeStampedModel


class Quote(TimeStampedModel):
    company_profile = models.ForeignKey(
        CompanyProfile,
        verbose_name='自社情報',
        related_name='quotes',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    project = models.ForeignKey(Project, verbose_name='案件', related_name='quotes', on_delete=models.PROTECT)
    quote_number = models.CharField('見積番号', max_length=50, unique=True)
    title = models.CharField('件名', max_length=255)
    issue_date = models.DateField('発行日')
    valid_until = models.DateField('有効期限', null=True, blank=True)
    status = models.CharField('ステータス', max_length=20, choices=QuoteStatus.choices, default=QuoteStatus.DRAFT)
    currency = models.CharField('通貨', max_length=3, default='JPY')
    tax_rate = models.DecimalField('税率', max_digits=5, decimal_places=2, default=TAX_RATE_DEFAULT)
    subtotal_amount = models.DecimalField('小計', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    tax_amount = models.DecimalField('消費税', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    total_amount = models.DecimalField('合計', max_digits=12, decimal_places=2, default=ZERO_DECIMAL)
    terms = models.TextField('取引条件', blank=True)
    notes = models.TextField('備考', blank=True)
    sent_at = models.DateTimeField('送付日時', null=True, blank=True)
    approved_at = models.DateTimeField('承認日時', null=True, blank=True)

    class Meta:
        ordering = ['-issue_date', '-id']
        verbose_name = '見積書'
        verbose_name_plural = '見積書'

    def __str__(self) -> str:
        return self.quote_number

    @property
    def client(self):
        return self.project.client

    def refresh_amounts(self, save: bool = True) -> None:
        subtotal = sum((item.total_amount for item in self.items.all()), ZERO_DECIMAL)
        subtotal = quantize_amount(subtotal, self.currency)
        tax = quantize_amount(subtotal * (self.tax_rate / Decimal('100')), self.currency)
        self.subtotal_amount = subtotal
        self.tax_amount = tax
        self.total_amount = quantize_amount(subtotal + tax, self.currency)
        if save:
            self.save(update_fields=['subtotal_amount', 'tax_amount', 'total_amount', 'updated_at'])
