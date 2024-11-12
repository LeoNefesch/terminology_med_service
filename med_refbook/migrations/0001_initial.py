# Generated by Django 4.2.7 on 2024-11-11 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Refbook',
            fields=[
                ('id', models.AutoField(help_text='Идентификатор справочника', primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('code', models.CharField(help_text='Код справочника', max_length=100, unique=True, verbose_name='Код')),
                ('name', models.CharField(help_text='Наименование справочника', max_length=300, verbose_name='Наименование')),
                ('description', models.TextField(blank=True, help_text='Описание справочника', verbose_name='Описание')),
            ],
            options={
                'verbose_name': 'Справочник',
                'verbose_name_plural': 'Справочники',
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(help_text='Идентификатор версии справочника', primary_key=True, serialize=False, verbose_name='Идентификатор версии')),
                ('version', models.CharField(help_text='Версия справочника', max_length=50, verbose_name='Версия')),
                ('date_start', models.DateField(help_text='Дата начала действия версии', verbose_name='Дата начала версии')),
                ('refbook', models.ForeignKey(help_text='Идентификатор справочника', on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='med_refbook.refbook', verbose_name='Справочник')),
            ],
            options={
                'verbose_name': 'Версия справочника',
                'verbose_name_plural': 'Версии справочника',
                'unique_together': {('refbook', 'date_start'), ('refbook', 'version')},
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(help_text='Идентификатор элемента справочника', primary_key=True, serialize=False, verbose_name='Идентификатор элемента справочника')),
                ('code', models.CharField(help_text='Код элемента', max_length=100, verbose_name='Код')),
                ('value', models.CharField(help_text='Значение элемента', max_length=300, verbose_name='Значение')),
                ('version', models.ForeignKey(help_text='Идентификатор версии справочника', on_delete=django.db.models.deletion.CASCADE, related_name='elements', to='med_refbook.version', verbose_name='Версия справочника')),
            ],
            options={
                'verbose_name': 'Элемент справочника',
                'verbose_name_plural': 'Элементы справочника',
                'unique_together': {('version', 'code')},
            },
        ),
    ]