"""
URL configuration for a_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.conf  import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from a_collections.views import *
from a_users.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    path('', home_view, name='home'),

    # a_users urls
    path('profile', profile_view, name='profile'),
    path('<username>/', profile_view, name='userprofile'),
    path('profile/edit/', profile_edit_view, name='profile-edit'),
    path('profile/delete/', profile_delete_view, name='profile-delete'),
    path('profile/onboarding/', profile_edit_view, name='profile-onboarding'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)