"""Chama system URL Configuration
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Main.urls')),
    path('', include('loan.urls')),
    path('', include('Users.urls')),
    #path('', include('Preaching.urls')),
    #path('',include('Partner.urls')),
    #path('',include('Mpesa.urls')),

]

urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
