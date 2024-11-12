from django.urls import path
from .views import CheckElement, ElementList, RefbookList

urlpatterns = [
    path('refbooks/', RefbookList.as_view(), name='refbook-list'),
    path('refbooks/<int:id>/elements', ElementList.as_view(),
         name='element-list'),
    path('refbooks/<int:id>/check_element', CheckElement.as_view(),
         name='check-element'),
]
