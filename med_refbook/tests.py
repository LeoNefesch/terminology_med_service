import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date
from .models import Element, Refbook, Version


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_refbooks(db):
    """Создание данных для тестов с их удалением после выполнения тестов"""
    refbook1 = Refbook.objects.create(id=1, code="MS1", name=" ")
    refbook2 = Refbook.objects.create(id=2, code="ICD-10", name="-10")
    version_1_1 = Version.objects.create(
        refbook=refbook1, version="v1",
        date_start=date(2022, 9, 1))
    version_1_2 = Version.objects.create(
        refbook=refbook2, version="v1",
        date_start=date(2022, 10, 1))
    version_2_1 = Version.objects.create(
        refbook=refbook2, version="v2",
        date_start=date(2023, 1, 1))
    Element.objects.create(version=version_1_1, code="J00",
                           value="Test Value 1.0")
    Element.objects.create(version=version_1_2, code="J01",
                           value="Test Value 2.0")
    yield refbook1, refbook2, version_1_1, version_1_2, version_2_1

    Element.objects.all().delete()
    Version.objects.all().delete()
    Refbook.objects.all().delete()


@pytest.mark.django_db
def test_get_refbooks_with_valid_date(api_client, setup_refbooks):
    """Тест с корректной датой"""
    url = reverse('refbook-list')
    response = api_client.get(url, {'date': '2022-10-01'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'refbooks' in data
    assert len(data['refbooks']) == 2  # Ожидаем 2 справочника
    assert data['refbooks'][0]['id'] == 1
    assert data['refbooks'][1]['id'] == 2


@pytest.mark.django_db
def test_get_refbooks_with_invalid_date(api_client):
    """Тест с некорректной датой"""
    url = reverse('refbook-list')
    response = api_client.get(url, {'date': 'invalid-date'})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert 'detail' in data
    assert data['detail'] == 'Неверный формат даты. Ожидается ГГГГ-ММ-ДД.'


@pytest.mark.django_db
def test_get_refbooks_without_date(api_client, setup_refbooks):
    """Тест без указания даты"""
    url = reverse('refbook-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['refbooks']) > 0


@pytest.mark.django_db
def test_get_elements_with_version(api_client, setup_refbooks):
    """Тест на получение элемента справочника с указанием версии"""
    refbook, _, version_1_1, _, _ = setup_refbooks
    url = reverse('element-list', kwargs={'id': refbook.id})
    response = api_client.get(url, {'version': 'v1'})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['elements']) == 1
    assert response.data['elements'][0]['code'] == 'J00'


@pytest.mark.django_db
def test_get_elements_current_version(api_client, setup_refbooks):
    """Тест на получение элемента справочника без указания версии
    (возвращаем текущую версию)"""
    refbook, _, _, version_1_2, version_2_1 = setup_refbooks
    url = reverse('element-list', kwargs={'id': refbook.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['elements']) == 1
    assert response.data['elements'][0]['code'] == 'J00'


@pytest.mark.django_db
def test_refbook_not_found(api_client):
    """Тест корректности ответа при передаче несуществующего ID справочника"""
    url = reverse('element-list', kwargs={'id': 999})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Справочник не найден'


@pytest.mark.django_db
def test_version_not_found(api_client, setup_refbooks):
    """Тест корректности ответа при передаче некорректной версии справочника"""
    refbook1, _, _, _, _ = setup_refbooks
    url = reverse('element-list', kwargs={'id': refbook1.id})
    response = api_client.get(url, {'version': 'v3.0'})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Указанная версия не найдена'


@pytest.mark.django_db
def test_no_elements_for_version(api_client, setup_refbooks):
    """Тест корректности ответа при отсутствии элементов справочника"""
    refbook1, _, version_1, _, _ = setup_refbooks
    Element.objects.filter(version=version_1).delete()
    url = reverse('element-list', kwargs={'id': refbook1.id})
    response = api_client.get(url, {'version': 'v1'})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['detail'] == 'Элементы не найдены для указанной версии'


@pytest.mark.django_db
def test_check_element_exists_in_current_version(api_client, setup_refbooks):
    """Тест на существование элемента, данные корректны"""
    refbook1, _, _, _, _ = setup_refbooks
    url = reverse('check-element', kwargs={'id': refbook1.id})
    response = api_client.get(url, {
        'code': 'J00',
        'value': 'Test Value 1.0'
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'exists': True}


@pytest.mark.django_db
def test_check_element_not_exists_in_current_version(api_client,
                                                     setup_refbooks):
    """Тест на несуществующий элемент, значение элемента некорректно"""
    refbook1, _, _, _, _ = setup_refbooks
    url = reverse('check-element', kwargs={'id': refbook1.id})
    response = api_client.get(url, {
        'code': 'J01',
        'value': 'Nonexistent Value'
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'exists': False}


@pytest.mark.django_db
def test_check_element_specific_version(api_client, setup_refbooks):
    """Тест на существование элемента с указанием версии, данные корректны"""
    _, refbook2, _, version_1_2, _ = setup_refbooks
    url = reverse('check-element', kwargs={'id': refbook2.id})
    response = api_client.get(url, {
        'code': 'J01',
        'value': 'Test Value 2.0',
        'version': 'v1'
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'exists': True}


@pytest.mark.django_db
def test_check_element_refbook_not_found(api_client):
    """Тест корректности обработки невалидного id справочника"""
    url = reverse('check-element', kwargs={'id': 999})
    response = api_client.get(url, {
        'code': 'J00',
        'value': 'Test Value 1.0'
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Справочник не найден.'}


@pytest.mark.django_db
def test_check_element_missing_parameters(api_client, setup_refbooks):
    """Тест корректности обработки отсутствия параметров 'code' и 'value'"""
    refbook1, *_ = setup_refbooks
    url = reverse('check-element', kwargs={'id': refbook1.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'detail': "Параметры 'code' и 'value' обязательны."}
