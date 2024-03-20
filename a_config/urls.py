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
from a_collections.forms import ArtistAutocomplete
from a_users.views import *

from dal import autocomplete


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    path('', home_view, name='home'),

    # a_collections urls
    path('', home_view, name='home'),

    path('collection/list', collection_list_view, name='collection-list'),

    path('collection/<pk>', collection_page_view, name='collection-page'),
    # path('release/create/', release_create_view, name='release-create'),
    path('collection/delete/<pk>', collection_delete_view, name='collection-delete'),
    
    path('release/list', release_list_view, name='release-list'),
    path('release/<pk>', release_page_view, name='release-page'),
    path('release/create/', release_create_view, name='release-create'),
    path('release/delete/<pk>', release_delete_view, name='release-delete'),
    path('release/edit/<pk>', release_edit_view, name='release-edit'),

    path('artist/create/', artist_create_view, name='artist-create'),
    path('create_artist/', artist_create_view, name='create_artist'),
    path('search_artist/', search_artist, name='search_artist'),
    path('add_artist/', add_artist_view, name='add_artist'),
    path('search_release/', search_release, name='search_release'),

    path('barcode_scanner/', barcode_scanner, name='barcode_scanner'),
    path('scan_barcode/', scan_barcode, name='scan_barcode'),

    # autocomplete view TODO: Move to views
    # path('artist-autocomplete/', ArtistAutocomplete.as_view(), name='artist-autocomplete'),
    path(
        'artist-autocomplete/$',
        autocomplete.Select2QuerySetView.as_view(
            model=Artist,
            create_field='name',
            validate_create=True,
        ),
        name='artist-autocomplete',
    ),
    
    path('media/download_csv/', download_csv, name='download-csv'),
    path('category/<tag>', home_view, name='category'),

    # a_users urls
    path('profile', profile_view, name='profile'),
    path('<username>/', profile_view, name='userprofile'),
    path('profile/edit/', profile_edit_view, name='profile-edit'),
    path('profile/delete/', profile_delete_view, name='profile-delete'),
    path('profile/onboarding/', profile_edit_view, name='profile-onboarding'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)