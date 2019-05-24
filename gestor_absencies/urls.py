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

detail_methods_without_update = {
    'get': 'retrieve',
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
    path('members',
         views.MemberViewSet.as_view(base_methods),
         name='members'),
    path('members/<int:pk>',
         views.MemberViewSet.as_view(datail_methods),
         name='members_detail'),
    path('vacationpolicy',
         views.VacationPolicyViewSet.as_view(base_methods),
         name='vacationpolicy'),
    path('vacationpolicy/<int:pk>',
         views.VacationPolicyViewSet.as_view(datail_methods),
         name='vacationpolicy_detail'),
    path('absencetype',
         views.SomEnergiaAbsenceTypeViewSet.as_view(base_methods),
         name='absencetype'),
    path('absencetype/<int:pk>',
         views.SomEnergiaAbsenceTypeViewSet.as_view(datail_methods),
         name='absencetype'),
    path('absences',
         views.SomEnergiaOccurrenceViewSet.as_view(base_methods),
         name='absences'),
    path('absences/<int:pk>',
         views.SomEnergiaOccurrenceViewSet.as_view(detail_methods_without_update),
         name='absences'),
]
