from django.db import models

from .activateable_model import ActivateableModel
from .time_stamped_model import TimeStampedModel


class Client(ActivateableModel, TimeStampedModel):
    name = models.CharField('取引先名', max_length=255)
    legal_name = models.CharField('正式名称', max_length=255, blank=True)
    contact_person = models.CharField('担当者名', max_length=255, blank=True)
    email = models.EmailField('メールアドレス', blank=True)
    phone = models.CharField('電話番号', max_length=32, blank=True)
    postal_code = models.CharField('郵便番号', max_length=16, blank=True)
    address = models.TextField('住所', blank=True)
    invoice_registration_number = models.CharField('適格請求書登録番号', max_length=32, blank=True)
    payment_terms_days = models.PositiveSmallIntegerField('支払サイト日数', default=30)
    notes = models.TextField('備考', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = '取引先'
        verbose_name_plural = '取引先'

    def __str__(self) -> str:
        return self.name
