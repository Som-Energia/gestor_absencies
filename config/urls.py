from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

router = routers.DefaultRouter()

urlpatterns = [
    path('absencies/', include('gestor_absencies.urls')),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('login/', obtain_jwt_token, name='login'),
]
