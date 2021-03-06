"""drm_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from dispute_resolution.viewsets import UserViewSet, NotifyEventViewSet, \
    UserInfoViewSet, ContractStageViewSet, ContractCaseViewSet

schema_view = get_swagger_view(title='Dispute Resolution API')

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)
router.register(r'contracts', ContractCaseViewSet)
router.register(r'stages', ContractStageViewSet)
router.register(r'userinfo', UserInfoViewSet)
router.register(r'events', NotifyEventViewSet, base_name='Events')
urlpatterns = router.urls

urlpatterns += [
    url(r'^admin/', admin.site.urls),
    url(r'^$', schema_view),
]
