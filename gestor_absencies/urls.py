from django.urls import include, path
from rest_framework import routers
from . import views

base_methods = {
    'get': 'list',
    'post': 'create',
}

datail_methods = {
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
}

urlpatterns = [
    path('workers',
         views.WorkerViewSet.as_view(base_methods),
         name='workers'),
    path('workers/<int:pk>',
         views.WorkerViewSet.as_view(datail_methods),
         name='workers_detail'),
    path('teams',
         views.TeamViewSet.as_view(base_methods),
         name='teams'),
    path('teams/<int:pk>',
         views.TeamViewSet.as_view(datail_methods),
         name='teams_detail'),
]
