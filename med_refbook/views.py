# from datetime import datetime

from django.db.models import Prefetch, Q
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Element, Refbook, Version
from .serializers import ElementSerializer, RefbookSerializer


@extend_schema(
    summary='Получение списка справочников',
    parameters=[
        OpenApiParameter(name='date',
                         description='Дата в формате ГГГГ-ММ-ДД для фильтрации '
                                     'актуальных справочников.',
                         required=False, type=str)
    ],
    responses={200: RefbookSerializer(many=True)},
)
class RefbookList(APIView):
    """Получение списка справочников (+ актуальных на указанную дату). \n
    Пример запроса:
    ` http://127.0.0.1:8000/refbooks/?date=2022-10-01 ` \n
    Пример ответа:
    ```
    {
        "refbooks": [
            {
                "id": 1,
                "code": "S001",
                "name": "Мед.справ."
            }
        ]
    }
    ```"""
    def get(self, request, *args, **kwargs):
        query_date = request.query_params.get('date')
        filter_date = parse_date(query_date) if query_date else now().date()
        if not filter_date:
            raise ValidationError({
                'detail': 'Неверный формат даты. Ожидается ГГГГ-ММ-ДД.'})
        filtered_versions = Version.objects.filter(date_start__lte=filter_date)
        refbooks = Refbook.objects.prefetch_related(
            Prefetch('versions', queryset=filtered_versions)
        ).distinct()
        serializer = RefbookSerializer(refbooks, many=True)
        return Response({'refbooks': serializer.data})


@extend_schema(
    summary='Получение элементов заданного справочника',
    parameters=[
        OpenApiParameter(name='id', location=OpenApiParameter.PATH,
                         description='Идентификатор справочника',
                         required=True, type=int),
        OpenApiParameter(name='version',
                         description='Версия справочника',
                         required=False, type=str)
    ],
    responses={200: ElementSerializer(many=True)},
)
class ElementList(APIView):
    """Получение элементов заданного справочника. \n
    Пример запроса:
    `http://127.0.0.1:8000/refbooks/1/elements?version=v2.0` \n
    Пример ответа:
    ```
    {
        "elements": [
            {
                "code": "123",
                "value": "Грипп"
            },
            {
                "code": "321",
                "value": "Плоскостопие"
            }
        ]
    }
    ```
    """
    def get(self, request, id, *args, **kwargs):
        version_param = request.query_params.get('version')
        if not Refbook.objects.filter(pk=id).exists():
            raise NotFound({'detail': 'Справочник не найден'})
        if version_param:
            version = Version.objects.filter(refbook_id=id,
                                             version=version_param).first()
            if not version:
                raise NotFound({'detail': 'Указанная версия не найдена'})
        else:
            version = Version.objects.filter(
                refbook_id=id, date_start__lte=now().date()).order_by(
                '-date_start').first()
            if not version:
                raise NotFound({'detail': 'Текущая версия не найдена'})
        elements = Element.objects.filter(version=version)
        if not elements:
            raise NotFound({
                'detail': 'Элементы не найдены для указанной версии'})
        serializer = ElementSerializer(elements, many=True)
        return Response({'elements': serializer.data})


@extend_schema(
    summary="Проверка наличия элемента в справочнике",
    parameters=[
        OpenApiParameter(name='id', location=OpenApiParameter.PATH,
                         description='Идентификатор справочника',
                         required=True, type=int),
        OpenApiParameter(name='code',
                         description='Код элемента',
                         required=True, type=str),
        OpenApiParameter(name='value',
                         description='Значение элемента',
                         required=True, type=str),
        OpenApiParameter(name='version',
                         description='Версия справочника',
                         required=False, type=str),
    ],
    responses={200: OpenApiParameter(name='exists', type=bool)},
)
class CheckElement(APIView):
    """ Проверка наличия элемента с данным кодом и значением в указанной версии
    справочника. \n
    Пример запроса:
    `http://127.0.0.1:8000/refbooks/1/check_element?code=234&value=Насморк&
    version=v1.0` \n
    Пример ответа:
    ```
    {
        "exists": true
    }
    ```"""
    def get(self, request, id, *args, **kwargs):
        code = request.query_params.get('code')
        value = request.query_params.get('value')
        version_name = request.query_params.get('version')
        if not code or not value:
            return Response(
                {"detail": "Параметры 'code' и 'value' обязательны."},
                status=400)
        refbook = Refbook.objects.filter(pk=id).first()
        if not refbook:
            raise NotFound({"detail": "Справочник не найден."})
        version_filter = Q(refbook=refbook,
                           version=version_name) if version_name else Q(
            refbook=refbook, date_start__lte=now().date())
        latest_version = Version.objects.filter(version_filter).order_by(
            '-date_start').first()
        if not latest_version:
            raise NotFound(
                {"detail": "Не найдено валидной версии справочника."})
        element_exists = Element.objects.filter(version=latest_version,
                                                code=code, value=value).exists()
        return Response({"exists": element_exists})
