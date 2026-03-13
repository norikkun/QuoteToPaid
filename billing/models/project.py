from django.db import models

from .choices import ProjectStatus
from .client import Client
from .time_stamped_model import TimeStampedModel


class Project(TimeStampedModel):
    client = models.ForeignKey(Client, verbose_name='取引先', related_name='projects', on_delete=models.PROTECT)
    name = models.CharField('案件名', max_length=255)
    code = models.CharField('案件コード', max_length=50, blank=True)
    status = models.CharField('ステータス', max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.LEAD)
    description = models.TextField('案件概要', blank=True)
    start_date = models.DateField('開始日', null=True, blank=True)
    end_date = models.DateField('終了日', null=True, blank=True)
    notes = models.TextField('備考', blank=True)

    class Meta:
        ordering = ['client__name', 'name']
        verbose_name = '案件'
        verbose_name_plural = '案件'
        constraints = [
            models.UniqueConstraint(fields=['client', 'name'], name='unique_project_name_per_client'),
        ]

    def __str__(self) -> str:
        return f'{self.client.name} / {self.name}'
