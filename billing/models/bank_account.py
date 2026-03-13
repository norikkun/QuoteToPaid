from django.db import models

from .choices import BankAccountType
from .company_profile import CompanyProfile
from .time_stamped_model import TimeStampedModel


class BankAccount(TimeStampedModel):
    company_profile = models.ForeignKey(
        CompanyProfile,
        verbose_name='自社情報',
        related_name='bank_accounts',
        on_delete=models.CASCADE,
    )
    nickname = models.CharField('口座名', max_length=100)
    bank_name = models.CharField('銀行名', max_length=255)
    branch_name = models.CharField('支店名', max_length=255, blank=True)
    account_type = models.CharField('口座種別', max_length=20, choices=BankAccountType.choices, default=BankAccountType.ORDINARY)
    account_number = models.CharField('口座番号', max_length=32)
    account_holder = models.CharField('口座名義', max_length=255)
    is_default = models.BooleanField('既定で使用する', default=False)

    class Meta:
        ordering = ['company_profile__name', 'nickname']
        verbose_name = '銀行口座'
        verbose_name_plural = '銀行口座'

    def __str__(self) -> str:
        return f'{self.company_profile.name} / {self.nickname}'
