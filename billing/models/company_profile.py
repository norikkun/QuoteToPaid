from django.db import models
from django.utils import timezone

from .time_stamped_model import TimeStampedModel


class CompanyProfile(TimeStampedModel):
    name = models.CharField('表示名', max_length=255)
    legal_name = models.CharField('正式名称', max_length=255, blank=True)
    invoice_registration_number = models.CharField('適格請求書登録番号', max_length=32, blank=True)
    email = models.EmailField('メールアドレス', blank=True)
    phone = models.CharField('電話番号', max_length=32, blank=True)
    postal_code = models.CharField('郵便番号', max_length=16, blank=True)
    address = models.TextField('住所', blank=True)
    website = models.URLField('Webサイト', blank=True)
    notes = models.TextField('備考', blank=True)
    is_default = models.BooleanField('既定で使用する', default=False)

    class Meta:
        ordering = ['name']
        verbose_name = '自社情報'
        verbose_name_plural = '自社情報'

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            self.__class__.objects.exclude(pk=self.pk).filter(is_default=True).update(
                is_default=False,
                updated_at=timezone.now(),
            )
