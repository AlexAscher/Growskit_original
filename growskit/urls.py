"""
URL configuration for growskit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
import re

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

list_django_static = []
if os.path.exists('/usr/local/lib/python3.12/dist-packages/django/contrib/admin/static/admin/'):
    list_django_static = static('static/admin/', document_root='/usr/local/lib/python3.12/dist-packages/django/contrib/admin/static/admin/')

urlpatterns = [
    re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), serve, kwargs={"document_root": 'media'}),
    path('admin/', admin.site.urls),
    *list_django_static,
    path('', include('main.urls')),
]

#if settings.DEBUG:
# break django (now we can get data from media/ path):
#urlpatterns += [re_path(r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")), serve, kwargs={"document_root": 'media'})]
# /usr/local/lib/python2.7/site-packages
