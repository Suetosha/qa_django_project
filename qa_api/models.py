from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
import logging

logger = logging.getLogger(__name__)

# Модель вопроса
class Question(models.Model):
    text = models.TextField(
        verbose_name="Текст вопроса",
        validators=[MinLengthValidator(5, "Вопрос должен содержать минимум 5 символов")],
        help_text="Введите текст вопроса (минимум 5 символов)"
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        default=timezone.now,
        help_text="Автоматически устанавливается при создании"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"Вопрос #{self.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Создан новый вопрос id={self.id}")

    def delete(self, *args, **kwargs):
        answers_count = self.answers.count()
        super().delete(*args, **kwargs)
        logger.info(f"Вопрос id={self.id} и {answers_count} ответов удалены")


# Модель ответа на вопрос
class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Вопрос",
        help_text="Вопрос, к которому относится этот ответ"
    )
    user_id = models.UUIDField(
        max_length=255,
        verbose_name="Id пользователя",
        help_text="Уникальный идентификатор пользователя"
    )
    text = models.TextField(
        verbose_name="Текст ответа",
        validators=[MinLengthValidator(3, "Ответ должен содержать минимум 3 символа")],
        help_text="Введите текст ответа (минимум 3 символа)"
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        default=timezone.now,
        help_text="Автоматически устанавливается при создании"
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['question', 'created_at']),
            models.Index(fields=['user_id']),
        ]

    def __str__(self) -> str:
        return f"Ответ #{self.id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"Создан новый ответ id={self.id} на вопрос id={self.question_id}")

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        logger.info(f"Ответ id={self.id} удален")
