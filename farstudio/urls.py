"""
URL configuration for farstudio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from studio import views as studio_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('studio/', include("studio.urls")), # OUR CUSTOME URL app
    path('accounts/', include('allauth.urls')),

    path('accounts/profile/', studio_views.index), ## NOTE ON TEST 99%
     ### NOTE DEFAULT VIEW
    path('', studio_views.custom_logout, name='account_logout'),

    path('admin/', admin.site.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)