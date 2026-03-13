from django.db import models

from .choices import ReminderMethod, ReminderStatus
from .invoice import Invoice
from .time_stamped_model import TimeStampedModel


class ReminderLog(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, verbose_name='請求書', related_name='reminder_logs', on_delete=models.CASCADE)
    reminded_at = models.DateTimeField('催促日時')
    method = models.CharField('手段', max_length=20, choices=ReminderMethod.choices, default=ReminderMethod.EMAIL)
    recipient = models.CharField('送付先', max_length=255, blank=True)
    subject = models.CharField('件名', max_length=255, blank=True)
    body = models.TextField('本文', blank=True)
    status = models.CharField('ステータス', max_length=20, choices=ReminderStatus.choices, default=ReminderStatus.DRAFT)
    next_follow_up_on = models.DateField('次回予定日', null=True, blank=True)
    notes = models.TextField('備考', blank=True)

    class Meta:
        ordering = ['-reminded_at', '-id']
        verbose_name = '催促履歴'
        verbose_name_plural = '催促履歴'

    def __str__(self) -> str:
        return f'{self.invoice.invoice_number} / {self.reminded_at:%Y-%m-%d %H:%M}'
