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
    path('employees',
         views.EmployeeViewSet.as_view(base_methods),
         name='employees'),
    path('employees/<int:pk>',
         views.EmployeeViewSet.as_view(datail_methods),
         name='employees_detail'),
    path('teams',
         views.TeamViewSet.as_view(base_methods),
         name='teams'),
    path('teams/<int:pk>',
         views.TeamViewSet.as_view(datail_methods),
         name='teams_detail'),
]
