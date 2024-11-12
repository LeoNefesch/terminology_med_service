from django.contrib import admin
from .models import Element, Refbook, Version


class VersionInline(admin.TabularInline):
    model = Version
    extra = 1


class HandbookElementInline(admin.TabularInline):
    model = Element
    extra = 1


@admin.register(Refbook)
class RefbookAdmin(admin.ModelAdmin):
    fields = ['code', 'name', 'description']
    list_display = ['id', 'code', 'name', 'current_version',
                    'current_version_start_date']
    inlines = [VersionInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('versions')

    def current_version(self, obj):
        latest_version = obj.versions.order_by('-date_start').first()
        return latest_version.version if latest_version else '-'
    current_version.short_description = 'Текущая версия'

    def current_version_start_date(self, obj):
        latest_version = obj.versions.order_by('-date_start').first()
        return latest_version.date_start if latest_version else '-'
    current_version_start_date.short_description = 'Дата начала действия версии'


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    fields = ['refbook', 'version', 'date_start']
    list_display = ['refbook_code', 'refbook_name', 'version', 'date_start']
    inlines = [HandbookElementInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('refbook')

    def refbook_code(self, obj):
        return obj.refbook.code
    refbook_code.short_description = 'Код справочника'

    def refbook_name(self, obj):
        return obj.refbook.name
    refbook_name.short_description = 'Наименование справочника'


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    fields = ['version', 'code', 'value']
    list_display = ['get_refbook_code', 'get_refbook_name',
                    'get_refbook_version', 'code', 'value']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('version__refbook')

    def get_refbook_code(self, obj):
        return obj.version.refbook.code
    get_refbook_code.short_description = 'Код справочника'

    def get_refbook_name(self, obj):
        return obj.version.refbook.name
    get_refbook_name.short_description = 'Имя справочника'

    def get_refbook_version(self, obj):
        return obj.version.version
    get_refbook_version.short_description = 'Версия справочника'
