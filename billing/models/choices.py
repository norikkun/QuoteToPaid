from django.db import models


class BankAccountType(models.TextChoices):
    ORDINARY = 'ordinary', '普通'
    CURRENT = 'current', '当座'
    SAVINGS = 'savings', '貯蓄'
    OTHER = 'other', 'その他'


class ProjectStatus(models.TextChoices):
    LEAD = 'lead', '見込み'
    ACTIVE = 'active', '進行中'
    ON_HOLD = 'on_hold', '保留'
    COMPLETED = 'completed', '完了'
    CANCELLED = 'cancelled', '中止'


class QuoteStatus(models.TextChoices):
    DRAFT = 'draft', '下書き'
    SENT = 'sent', '送付済み'
    APPROVED = 'approved', '承認済み'
    REJECTED = 'rejected', '却下'
    EXPIRED = 'expired', '期限切れ'
    CANCELLED = 'cancelled', '取消'


class InvoiceStatus(models.TextChoices):
    DRAFT = 'draft', '下書き'
    SENT = 'sent', '送付済み'
    PARTIALLY_PAID = 'partially_paid', '一部入金'
    PAID = 'paid', '入金済み'
    OVERDUE = 'overdue', '期限超過'
    CANCELLED = 'cancelled', '取消'


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = 'bank_transfer', '銀行振込'
    CASH = 'cash', '現金'
    CARD = 'card', 'カード'
    OTHER = 'other', 'その他'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', '確認待ち'
    RECEIVED = 'received', '入金確認済み'
    FAILED = 'failed', '失敗'
    REFUNDED = 'refunded', '返金済み'


class ReminderMethod(models.TextChoices):
    EMAIL = 'email', 'メール'
    PHONE = 'phone', '電話'
    CHAT = 'chat', 'チャット'
    POSTAL = 'postal', '郵送'
    OTHER = 'other', 'その他'


class ReminderStatus(models.TextChoices):
    DRAFT = 'draft', '下書き'
    SENT = 'sent', '送信済み'
    DELIVERED = 'delivered', '到達確認'
    REPLIED = 'replied', '返信あり'
    FAILED = 'failed', '失敗'
