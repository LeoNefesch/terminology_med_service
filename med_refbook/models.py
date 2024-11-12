from django.db import models
from django.utils.translation import gettext_lazy as _


class Refbook(models.Model):
    """Справочник"""
    id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор справочника'
    )
    code = models.CharField(
        max_length=100,
        blank=False,
        unique=True,
        verbose_name='Код',
        help_text='Код справочника'
    )
    name = models.CharField(
        max_length=300,
        blank=False,
        verbose_name='Наименование',
        help_text='Наименование справочника'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
        help_text='Описание справочника'
    )

    def __str__(self):
        return f'{self.name} ({self.code})'

    class Meta:
        verbose_name = _('Справочник')
        verbose_name_plural = _('Справочники')


class Version(models.Model):
    """Версия справочника"""
    id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор версии',
        help_text='Идентификатор версии справочника'
    )
    refbook = models.ForeignKey(
        Refbook,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='Справочник',
        help_text='Идентификатор справочника'
    )
    version = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Версия',
        help_text='Версия справочника'
    )
    date_start = models.DateField(
        verbose_name='Дата начала версии',
        help_text='Дата начала действия версии'
    )

    def __str__(self):
        return f'{self.refbook.name} - Версия {self.version}'

    class Meta:
        verbose_name = _('Версия справочника')
        verbose_name_plural = _('Версии справочника')
        unique_together = (
            ('refbook', 'version'),
            ('refbook', 'date_start')
        )


class Element(models.Model):
    """Элемент справочника"""
    id = models.AutoField(
        primary_key=True,
        verbose_name='Идентификатор элемента справочника',
        help_text='Идентификатор элемента справочника'
    )
    version = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='elements',
        verbose_name='Версия справочника',
        help_text='Идентификатор версии справочника'
    )
    code = models.CharField(
        max_length=100,
        blank=False,
        verbose_name='Код',
        help_text='Код элемента'
    )
    value = models.CharField(
        max_length=300,
        blank=False,
        verbose_name='Значение',
        help_text='Значение элемента'
    )

    def __str__(self):
        return f'{self.code}: {self.value}'

    class Meta:
        verbose_name = _('Элемент справочника')
        verbose_name_plural = _('Элементы справочника')
        unique_together = ('version', 'code')
