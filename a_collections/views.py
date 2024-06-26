from django.shortcuts import render
from django.contrib import messages
from django.db.models import Prefetch, Q
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

import requests 
import csv
import os
import requests
import shutil
from django.http import HttpResponse

from a_collections.utils import (artist_search, 
                                 release_search, 
                                 milliseconds_to_minutes_seconds, 
                                 release_group_search, 
                                 release_barcode_search,
                                 get_release_group_info,
                                 format_date,
                                 get_artists_from_hitdossier_online,
                                 )
from a_collections.models import Artist, Release, Cover_Art, Record_Label, Collection, Track, Release_Group
from a_collections.forms import ReleaseCreateForm, ReleaseEditForm, ArtistCreateForm, ArtistEditForm

# Create your views here.
def home_view(request, tag=None):
    # if tag:
    #     posts = Post.objects.filter(tags__slug=tag)
    #     tag = get_object_or_404(Tag, slug=tag)
    # else:     
    #     posts=  Post.objects.all()
    
    # # instantiate the Paginator oobject with 3 posts per page
    # paginator = Paginator(posts, 3)
    # # get the page to display from the request object with a defaul of 1
    # page = int(request.GET.get('page',1))
    # # give back the correct page and return a blank page when there are no more pages
    # try:
    #     posts = paginator.page(page) 
    # except:
    #     return HttpResponse('')

    # artist_search("Texas")

    # quote = 'Record collecting is the hobby of collecting sound recordings, usually of music, but sometimes poetry, reading, historical speeches, and ambient noises. Although the typical focus is on vinyl records, all formats of recorded music can be collected.'
    context = {
        'tag' : tag,
        # 'page' : page,
        # 'artists' : Artist.objects.all(),
        # 'albums' : Release.objects.all(),
        # 'quote' :  quote,
    }
    
    # if request.htmx:
    #     return render(request, 'snippets/loop_home_posts.html', context)
    
    return render(request, "pages/home.html", context)
 

def release_list_view(request, tag=None):
    
    context = {
        'results' : Release.objects.prefetch_related('cover_art'),

    }
    return render(request, "a_collections/release_list.html", context)


@login_required
def collection_list_view(request, tag=None):
    user = request.user
    results = Collection.objects.filter(user=user)

    # Prefetch related release and cover art
    results = results.select_related('release').prefetch_related(
        Prefetch('release__cover_art', queryset=Cover_Art.objects.all())
    )
    # Retrieve only the first cover art image for each release
    for result in results:
        if result.release.cover_art.exists():
            result.first_cover_art = result.release.cover_art.first()
        else:
            result.first_cover_art = None


    # Check if reset button was clicked
    reset = request.POST.get('reset') or request.GET.get('reset')
    if reset:
        results = Collection.objects.filter(user=user)
        context = {'results': results}
        if request.htmx:
            data_template = request.GET.get('data-template', 'a_collections/partials/results_table.html')
            print(data_template)
            return render(request, data_template, context)

            # return render(request, "a_collections/partials/results_table.html", context)
        else:
            return render(request, "a_collections/collection_list.html", context)


    # Check if search parameters are provided in the request
    if request.method == 'POST':
        artist = request.POST.get('artist')
        album = request.POST.get('album')

        if artist:
            results = results.filter(release__artist__name__icontains=artist)
        if album:
            results = results.filter(release__name__icontains=album)

        print(f"artist: {artist}")
        print(f"album: {album}")
        
        context = {'results': results}

    
    # Check if sort parameter is provided in the request
    sort_param = request.GET.get('sort')
    if sort_param == 'name':
        # Toggle between ascending and descending order for release name
        if request.session.get('sort_order', '') == 'asc':
            request.session['sort_order'] = 'desc'
            results = results.order_by('-release__name')
        else:
            request.session['sort_order'] = 'asc'
            results = results.order_by('release__name')
    elif sort_param == 'artist':
        if request.session.get('sort_order', '') == 'asc':
            request.session['sort_order'] = 'desc'
            results = results.order_by('-release__artist__name')
        else:
            request.session['sort_order'] = 'asc'
            results = results.order_by('release__artist__name')
    elif sort_param == 'date':
        if request.session.get('sort_order', '') == 'asc':
            request.session['sort_order'] = 'desc'
            results = results.order_by('-release__date')
        else:
            request.session['sort_order'] = 'asc'
            results = results.order_by('release__date')
    elif sort_param == 'label':
        if request.session.get('sort_order', '') == 'asc':
            request.session['sort_order'] = 'desc'
            results = results.order_by('-release__record_label__name')
        else:
            request.session['sort_order'] = 'asc'
            results = results.order_by('release__record_label__name')
    elif sort_param == 'type':
        if request.session.get('sort_order', '') == 'asc':
            request.session['sort_order'] = 'desc'
            results = results.order_by('-release__type')
        else:
            request.session['sort_order'] = 'asc'
            results = results.order_by('release__type')

    context = {'results': results}
    if request.htmx:
        data_template = request.GET.get('data-template', 'a_collections/partials/results_cover.html')
        
        print("Data template received:", data_template)  # Add debug print

        return render(request, data_template, context)
        # return render(request, "a_collections/partials/results_table.html", context)

    return render(request, "a_collections/collection_list.html", context)

@login_required
def release_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = ReleaseCreateForm(request.POST)
        if form.is_valid():
            release = form.save(commit=False)

            release.user = request.user

            release.save()
            # release.save_m2m() # save our tags m2m field
            return redirect('home')
        
    form = ReleaseCreateForm()
    return render(request, "a_collections/release_create.html", {'form' : form})


@login_required
def release_delete_view(request, pk):
    release = get_object_or_404(Release, id=pk)
    cover_art = Cover_Art.objects.filter(release=release)

    if request.method == 'POST':
        if cover_art:
            cover_art.delete()
        release.delete()
        
        messages.success(request, 'release and associated cover art deleted successfully')  
        return redirect('home')
    
    return render(request, "a_collections/release_delete.html", {'release' : release})

@login_required
def collection_delete_view(request, pk):
    collection = get_object_or_404(Collection, id=pk)

    if request.method == 'POST':
        collection.delete()
        messages.success(request, 'item removed successfully from collection')  
        return redirect('home')
    
    return render(request, "a_collections/release_delete.html", {'collection' : collection})

@login_required
def release_edit_view(request, pk):
    release = get_object_or_404(release, id=pk, user=request.user)
    form = ReleaseEditForm(instance=release)

    context = {
        'post' : release,
        'form' : form,
    }
    
    if request.method == 'POST' and request.user == release.user:
        form = ReleaseEditForm(request.POST, instance=release)
        if form.is_valid():
            form.save()
            messages.success(request, 'release updated successfully')  
            return redirect('home')

    
    return render(request, "a_collections/release_edit.html", context)


def get_cover_art_urls(release_id):
    # Construct the URL for the cover art images using the release ID
    cover_art_url = f"https://coverartarchive.org/release/{release_id}"
    # print(f"cover art url: {cover_art_url}")
    
    # Send GET request to the cover art archive
    response = requests.get(cover_art_url)

    # Check if request was successful and cover art exists
    if response.status_code == 200:
        return response.json()  # Return the JSON data
    else:
        return None


def release_page_view(request, pk):
    release = get_object_or_404(Release, id=pk)
    cover_art_images = release.cover_art.all()
    
    context = {
        'release': release,
        'cover_art_images': cover_art_images,
    }
    return render(request, "a_collections/release_detail.html", context)


@login_required
def collection_page_view(request, pk):
    collection = get_object_or_404(Collection, id=pk)
    cover_art_images = collection.release.cover_art.all()
    
    release = Release.objects.get(id=collection.release.id)
    print(f"release: {release}")

    # Get all tracks associated with the release
    tracks = release.tracks.all()

     # Convert track durations from milliseconds to minutes and seconds
    for track in tracks:
        track.duration_formatted = milliseconds_to_minutes_seconds(int(track.duration))

    print(f"tracks: {tracks}")

    context = {
    'collection': collection,
    'cover_art_images': cover_art_images,
    'tracks': tracks,
    }
    return render(request, "a_collections/collection_detail.html", context)


@login_required
def artist_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = ArtistCreateForm(request.POST)
        if form.is_valid():
            artist = form.save(commit=False)

            artist.user = request.user

            artist.save()
            return redirect('home')
        
    form = ArtistCreateForm()
    return render(request, "a_collections/artist_create.html", {'form' : form})

@login_required
def search_artist(request):
    results = []
    if request.method == 'GET' and 'artist_name' in request.GET:
        artist_name = request.GET.get('artist_name')
        results = artist_search(artist_name)

        # Modify the data to make it accessible in the template
        modified_results = [{'ext_score': result.get('ext:score'), 'id': result.get('id'), 'name': result.get('name'), 'type': result.get('type'), 'country': result.get('country'), 'gender': result.get('gender')} for result in results]

    return render(request, "a_collections/artist_create.html", {'results': modified_results})


@login_required
def search_release(request):
    results = []
    result_list = []
    
    # format='Cassette'

    if request.method == 'GET' or request.method == 'POST':
        # artist_name = request.GET.get('artist')
        # album_name = request.GET.get('album')
        # format = request.GET.get('format')

        # print(f"artist: {artist_name} ")
        # print(f"album: {album_name} ")
        # print(f"requested format: {format}")

        artist_name = request.POST.get('artist')
        album_name = request.POST.get('album')
        format = request.POST.get('format')
        barcode = request.POST.get('barcode')

        print(f"artist: {artist_name} ")
        print(f"album: {album_name} ")
        print(f"barcode: {barcode} ")
        print(f"requested format: {format}")

        if barcode:
            print(f"We zoeken nu obv barcode")
            results = release_barcode_search(barcode=barcode)
        else:
            print(f"We zoeken nu obv artist and album")
            results = release_search(artist_name, album_name, format=format)

        # TODO release group uit release halen en opslaan
        # release_group_results = release_group_search(artist_name, album_name)
        # print(f"$$$$$$$$$$$$$$$$$$$")
        # print(f"$$$$$$$$$$$$$$$$$$$")
        # print(f"release results : {results}")
        # print(f"$$$$$$$$$$$$$$$$$$$")
        # print(f"$$$$$$$$$$$$$$$$$$$")

        # Assuming 'result' is the dictionary containing the JSON data
        for release in results['release-list']:
            release_id = release.get('id', None)
            # in_collection = Collection.objects.filter(release.musicbrainz_id = release_id)
            ext_score = release.get('ext:score', None)
            name = release.get('title', '')

            # artist_id = release['artist-credit'][0].get('id', None) if 'artist-credit' in release else None
            # TODO: artist naar Release group
            artist_id = release['artist-credit'][0]['artist']['id'] if 'artist-credit' in release and release['artist-credit'] else ''
            artist = release['artist-credit'][0]['name'] if 'artist-credit' in release else ''
            
            country_date = release.get('country', '') + ' ' + release.get('date', '') if any(key in release for key in ['country', 'date']) else ''
            label_info = release.get('label-info-list', [])
            label = label_info[0].get('label', {}).get('name', '') if label_info else ''
            label_id = label_info[0].get('label', {}).get('id', '') if label_info else ''
            catalog_number = label_info[0].get('catalog-number', '') if label_info else ''
            barcode = release.get('barcode', '')
            language = release.get('text-representation', {}).get('language', '')
            status = release.get('status', '')

            # TODO: REleae group toevoegen
            # release_type = release['release-group']['primary-type'] if 'release-group' in release else ''
            if 'release-group' in release:
                try:
                    release_type = release['release-group']['primary-type']
                    release_group_id = release['release-group']['id']
                    release_group_type = release['release-group']['primary-type']
                    release_group_title = release['release-group']['title']
                    # print(f"@@@@@@@@@@@@@")
                    # print(f"@@@@@@@@@@@@@")
                    print(f"release group info:: id {release_group_id} | type {release_group_type} | title {release_group_title}")
                    # get_release_group_info(release_group_id)
                    # print(f"@@@@@@@@@@@@@")
                    # print(f"@@@@@@@@@@@@@")

                except KeyError:
                    release_type = ''
            else:
                release_type = ''

            # Initialize variables to accumulate CD and DVD track counts
            cd_tracks = 0
            dvd_tracks = 0
            
            
            # Get cover art URLs for the release
            cover_art_data = get_cover_art_urls(release_id)
            cover_art_images = []
            if cover_art_data is not None:
                for image_data in cover_art_data['images']:
                    image_id = image_data.get('id', None)
                    image_url = image_data.get('image', None)
                    thumbnails_small = image_data.get('thumbnails', {}).get('small', None)
                    image_type = image_data.get('types', [])

                    if image_type and image_type[0] == "Front":
                        # print(f"id: {image_id} | image: {image_url} | type: {image_type[0]} | thumbnails_small: {thumbnails_small}")
                        cover_art_images.append({
                            'id': image_id,
                            'image': image_url,
                            'image_small': thumbnails_small,
                            'type': image_type[0]
                        })
                        
            else:
                cover_art_images = []

            # Iterate over each medium in the medium list
            if 'medium-list' in release:
                for medium in release['medium-list']:
                    format = medium.get('format', '')
                    track_count = medium['track-count']

                    # Accumulate track counts based on format
                    if format == 'CD':
                        cd_tracks += track_count
                    elif format == 'DVD':
                        dvd_tracks += track_count

            if cd_tracks > 0 and dvd_tracks == 0:
                format = 'CD'
            elif cd_tracks > 0 and dvd_tracks >0:
                format = 'CD + DVD'
            elif cd_tracks == 0 and dvd_tracks >0:
                format= 'DVD'

            # Print the information
            print("Release_id:", release_id)
            print("Name:", name)
            print("Artist_id:", artist_id)

            print("Artist:", artist)
            print("Format:", format)

            if cd_tracks > 0 and dvd_tracks == 0:
                print(f"Tracks: {cd_tracks}")
            elif cd_tracks > 0 and dvd_tracks >0:
                print(f"Tracks: {cd_tracks} + {dvd_tracks}")
            elif cd_tracks == 0 and dvd_tracks >0:
                print(f"Tracks: {dvd_tracks}")

            print("Country/Date:", country_date)
            print("Label:", label)
            print("Label_id:", label_id)

            print("Catalog#:", catalog_number)
            print("Barcode:", barcode)
            print("Language:", language)
            print("Release_type:", release_type)
            print("Status:", status)
                
            print("Release group id:", release_group_id) 
            print("Release group title:", release_group_title) 
            print("Release group type:", release_group_type) 
            print()

            result_info = {
                # album info
                'release_id': release_id,
                'ext_score': ext_score,
                'name': name,
                
                # artist info
                'artist_id': artist_id,
                'artist': artist,
                
                # release-group info
                'release_group_id': release_group_id,
                'release_group_title': release_group_title,

                # release info
                'format': format,
                'cd_tracks': cd_tracks,
                'dvd_tracks': dvd_tracks,
                'date': country_date,
                
                'label': label,
                'label_id': label_id,

                'catalog_number': catalog_number,
                'barcode': barcode,
                'language': language,
                'release_type': release_type,
                'status': status,

                # cover art
                'cover_art_images': cover_art_images

            }
            result_list.append(result_info)
    
    
    referring_page = request.META.get('HTTP_REFERER')
    # Split the URL by '/' characters and get the last element
    if referring_page:
        print(f"referring url: {referring_page}")
        # Split the URL by "/"
        url_parts = referring_page.split('/')
        print(f"referring url: {url_parts}")
        # Get the last element of the list
        last_part = url_parts[-2]
        print("Last part of the URL:", last_part)
        print(f"##################")

        if last_part == 'list':
            return render(request, "a_collections/partials/musicbrainz_results_table.html", {'results': result_list})
        else:
            return render(request, "a_collections/release_create.html", {'results': result_list})
    else:
        print("Referring page not found")

    return render(request, "a_collections/release_create.html", {'results': result_list})


def barcode_scanner(request):
    print("geef barcode weer")
    return render(request, "a_collections/barcode_scanner.html")


def scan_barcode(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        print(f"barcode:: {barcode}")
        # Perform the MusicBrainz API request here using the barcode
        # Example:
        response = requests.get(f'https://musicbrainz.org/ws/2/release?query=barcode:{barcode}&fmt=json')
        data = response.json()
        print(f"data:: {data    }")
        return JsonResponse(data)
    return JsonResponse({'error': 'Method not allowed'}, status=405)



def release_detail(request, release_id):
    release = Release.objects.get(id=release_id)
    artist = Artist.objects.get(id = artist.id)
    cover_art = Cover_Art.objects.filter(release=release)
    context = {
        'release': release,
        'artist' : artist,
        'cover_art': cover_art,
    }
    return render(request, 'a_collections/release_detail.html', context)


import json

@login_required
def add_artist_view(request):
    cover_art_images = []
    
    # What do we need to add
    if request.method == 'POST':
        release_id = request.POST.get('release_id')
        release_name = request.POST.get('release_name')
        artist_id = request.POST.get('artist_id')
        artist_name = request.POST.get('artist_name')
        format = request.POST.get('format')
        ext_score = request.POST.get('ext_score')
        barcode = request.POST.get('barcode')
        date = request.POST.get('date')
        language = request.POST.get('language')
        status = request.POST.get('status')
        catalog_number = request.POST.get('catalog_number')
        cd_tracks = request.POST.get('cd_tracks')
        dvd_tracks = request.POST.get('dvd_tracks')
        cover_art_images_str = request.POST.get('cover_art_images')
        label_name = request.POST.get('label')
        label_id = request.POST.get('label_id')
        release_group_id = request.POST.get('release_group_id')
        release_group_title =request.POST.get('release_group_title')

        print(f"id: {artist_id} | name: {artist_name} | ext_score: {ext_score} | release_group_title {release_group_title}")
        
        user = request.user
        artist = Artist.objects.filter(musicbrainz_id=artist_id).first()
        release = Release.objects.filter(musicbrainz_id=release_id).first()
        collection = Collection.objects.filter(release=release, user=user).first()
        release_group = Release_Group.objects.filter(musicbrainz_id=release_group_id).first()
        

        if collection:
            print(f"release already in collection {release} of user ")
        
        label = Record_Label.objects.filter(musicbrainz_id=label_id).first()
        
        if not artist:
            artist = Artist.objects.create(
                musicbrainz_id=artist_id,
                name=artist_name,
                ext_score=ext_score
            )
            messages.success(request, f'Artist {artist} added successfully')  

        else:
            messages.success(request, f'Artist {artist_name} already in the database')  

        if release_group:
            print(f"release group already exists")
        else:
            release_group_info = get_release_group_info(release_group_id)
            print("###################")
            print("###################")
            print(f"release_group_info {type(release_group_info)}")
            print(f"release_group_info {release_group_info}")
            print("###################")
            print("###################")
            data = release_group_info
            #TODO: juiste info invullen uit release_group_info
            # dus niet via d efront end maar vanuit een aparte call!!

            release_group = Release_Group.objects.create(
                musicbrainz_id = release_group_id,
                # musicbrainz_type_id= data.get('type-id'),
                musicbrainz_primrary_type_id = data.get("primary-type-id"),
                name = release_group_title,
                artist = artist,
                first_release_date = format_date(data.get('first-release-date')),
                primrary_type = data.get('primary-type'),
                secondary_types = data.get("secondary-types", []),
                secondary_type_ids = data.get('secondary-type-ids'),
            )
            print(f"Release group object: {release_group}")
            messages.success(request, f'Release group {release_group.name} added succesfully')  

        if not label:
            label = Record_Label.objects.create(
                musicbrainz_id=label_id,
                name=label_name,
            )
            messages.success(request, f'Record Label {label_name} added successfully')  
            print(f'Record Label {label_name} added successfully')
        else:
            messages.success(request, f'Record Label {label_name} already in the database')
            print(f'Record Label {label_name} already in the database')

        if not release and release_id is not None:
            release = Release.objects.create(
                musicbrainz_id=release_id,
                name=release_name,
                release_group = release_group,
                barcode = barcode,
                catalog_number = catalog_number,
                status = status,
                language = language,
                cd_tracks = cd_tracks,
                dvd_tracks = dvd_tracks,
                format = format,
                date = date,
                record_label = label
            )
            messages.success(request, f'Release {release} added successfully')  
        
        # add release to collection
        if not collection:
            collection = Collection.objects.create(
                release = release,
                user = user,

            )

        if cover_art_images_str:
            try:
                # Preprocess the string to replace single quotes with double quotes
                cover_art_images_str = cover_art_images_str.replace("'", '"')
                cover_art_images = json.loads(cover_art_images_str)
                
                for data in cover_art_images:
                    musicbrainz_id = data.get('id'),
                    print(f"covert musicbrainz_id: {musicbrainz_id}")
                    print(f"covert musicbrainz_id: {type(musicbrainz_id)}")
                    print(f"covert musicbrainz_id: {musicbrainz_id[0]}")

                    cover_art = Cover_Art.objects.filter( musicbrainz_id = musicbrainz_id[0]).first()
                    print(f"covert art: {cover_art}")

                    if not cover_art:

                        # Download cover art image
                        cover_art_url = data.get('image'),
                        print("###################")
                        print("###################")
                        print("###################")
                        print(f"cover art image url for large image: {cover_art_url}")
                        first_url_string = str(cover_art_url[0])
                        print(f"cover art image url for large image: {first_url_string}")
                        print(f"cover art image url type large image: {type(first_url_string)}")
                        
                        # Download the image from the URL
                        response = requests.get(first_url_string)
                        print(f"response: {response}")

                        if response.status_code == 200:
                            # Define the filename for the downloaded image
                            filename = f"cover_art_{release_id}.jpg"
                            print(f"filename: {filename}")

                            # Define the file path in the media folder
                            folder_path = os.path.join(settings.MEDIA_ROOT, "cover_art")
                            
                            # Create the folder if it doesn't exist
                            os.makedirs(folder_path, exist_ok=True)
                            
                            file_path = os.path.join(folder_path, filename)
                            print(f"file path: {file_path}")
                            
                            # Save the image to the media folder
                            with open(file_path, 'wb') as f:
                                f.write(response.content)                        

                        # store new cover art object
                        cover_art = Cover_Art.objects.create(
                            musicbrainz_id = data.get('id'),
                            image=os.path.join(settings.MEDIA_URL, "cover_art", filename),
                            image_url = data.get('image'),
                            image_small_url = data.get('image_small'),
                            cover_art_type = data.get('type'),
                            release = release,
                        )

                       
                        # if image_url:
                        #     image_response = requests.get(image_url, stream=True)
                        #     if image_response.status_code == 200:
                        #         # Save image to media folder
                        #         file_name = f"cover_art_{release_id}.jpg"
                        #         file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                        #         with open(file_path, 'wb') as f:
                        #             image_response.raw.decode_content = True
                        #             shutil.copyfileobj(image_response.raw, f)


                        # print(f"cover art: {cover_art}")
                        messages.success(request, f'Cover art for {release} added successfully')
            except json.JSONDecodeError as e:
                print("Error decoding cover_art_images JSON:", e)

        else: 
            if release:
                messages.success(request, f'Release {release} already in the database')  

        # add tracks
        # Construct the URL for the MusicBrainz API endpoint for releases
        url = f"https://musicbrainz.org/ws/2/release/{release_id}?inc=recordings&fmt=json"
        print(f"url: {url}")
        print(f"release id: {release_id}")
        # Make a GET request to the MusicBrainz API
        response = requests.get(url)
        print(f"response: {response}")
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract the list of recordings (tracks) from the response
            tracks = data.get('media', [{}])[0].get('tracks', [])
            print(f"tracks on this release: ")
            print(f"{tracks}")
          
            for track in tracks:
                musicbrainz_id = track.get('id', None)
                length = track.get('length', None)
                number = track.get('number', None)
                position = track.get('position', None)
                title = track.get('title', None)
                print(f"track title: {title}")
                print(f"musicbrainz id: {musicbrainz_id}")
                print(f"length/duration of song: {length}")
                print(f"number on release: {number}")
                print(f"position on release: {position}")
                
                track_found = Track.objects.filter(musicbrainz_id = musicbrainz_id).first()
                print(f"track found in database: {track}")

                if not track_found:
                    #TODO: check of track er als is:

                    track = Track.objects.create(
                        musicbrainz_id = musicbrainz_id,
                        release = release,
                        title = title,
                        position = position,
                        duration = length,
                        number = number,
                    )
        else:
            # If the request fails, print an error message
            print(f"Failed to fetch tracks from release {release_id}. Status code: {response.status_code}")
        

        return redirect('collection-list')  
    return redirect('collection-list')

# def add_artist_view(request):
#     cover_art_images = []
#     if request.method == 'POST':
#         release_id = request.POST.get('release_id')
#         release_name = request.POST.get('release_name')
#         artist_id = request.POST.get('artist_id')
#         artist_name = request.POST.get('artist_name')
#         # type = request.POST.get('type')
#         format = request.POST.get('format')
#         ext_score = request.POST.get('ext_score')
#         barcode = request.POST.get('barcode')
#         date = request.POST.get('date')
#         language = request.POST.get('language')
#         status = request.POST.get('status')
#         catalog_number = request.POST.get('catalog_number')
#         cd_tracks = request.POST.get('cd_tracks')
#         dvd_tracks = request.POST.get('dvd_tracks')
#         cover_art_images = request.POST.get('cover_art_images')

#         print(f"id: {artist_id} | name: {artist_name} | ext_score: {ext_score}")
        

#         # Check if the artist_id already exists in the database
#         artist = Artist.objects.filter(musicbrainz_id=artist_id).first()
#         print(f"Artist: {artist}")
#         existing_album = Release.objects.filter(musicbrainz_id=release_id).first()

#         # If the artist does not exist, create a new record
#         if not artist:
#             artist = Artist.objects.create(
#                 musicbrainz_id=artist_id,
#                 name=artist_name,
#                 # type="",
#                 ext_score=ext_score
#             )
#             # Now the artist record is added to the database
#             messages.success(request, f'Artist {artist} added successfully')  

#         else:
#             # The artist already exists in the database
#             # You can choose to perform any other action here, if needed
#             messages.success(request, f'Artist {artist_name} already in the database')  

#         if not existing_album and release_id is not None:
#             release = Release.objects.create(
#                 musicbrainz_id=release_id,
#                 name=release_name,
#                 artist=artist,
#                 barcode = barcode,
#                 catalog_number = catalog_number,
#                 status = status,
#                 language = language,
#                 cd_tracks = cd_tracks,
#                 dvd_tracks = dvd_tracks,
#                 format = format,
#                 date = date,
#             )
#             # Now the artist record is added to the database
#             messages.success(request, f'release {release} added successfully')  

#             if cover_art_images:
#                 print(f"cover_art_images: {cover_art_images}")
#                 print("Type of cover_art_images:", type(cover_art_images))

#                 for data in cover_art_images:
#                     print("###########")
#                     print("###########")
#                     print(f"cover art data: {data} <-- what data...")
#                     print("###########")
#                     print("###########")
#                     cover_art = Cover_Art.objects.create(
#                         musicbrainz_id = data.get('id'),
#                         image_url = data.get('image'),
#                         image_small_url = data.get('image_small'),
#                         cover_art_type = data.get('type'),
#                         # musicbrainz_id = data['id'],
#                         # image_url = data['image'],
#                         # image_small_url = data['image_small'],
#                         # cover_art_type = data['type'],
#                         release = release,
#                     )
#                     print(f"cover art: {cover_art}")
#                 messages.success(request, f'cover art for {release} added successfully')

#         else: 
#             # The artist already exists in the database
#             # You can choose to perform any other action here, if needed
#             if existing_album:
#                 messages.success(request, f'release {existing_album} already in the database')  


#         return redirect('home')  # Redirect to home page or any other page after adding artist
#     return redirect('home')  # Redirect to home page if not a POST request


@login_required
def download_csv(request):
    # Create a HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write headers
    writer.writerow(['Artist name', 'release title', 'release type', 'release release year', 'release catalog nr', 'Record label'])

    release_data = Release.objects.all()
    print(release_data)
    artist_data = Artist.objects.all()
    print(artist_data)
    print("Now I am here")

    # Write data rows
    for obj1 in release_data:
        print(obj1)
        for obj2 in artist_data.filter(name=obj1.artist):
            writer.writerow([obj2.name, obj1.name, obj1.type, obj1.release_year, obj1.catalog_number, obj1.record_label])

    return response


def recognize_song(request):
    print(f"request: {request}")
    if request.method == 'POST':

        # Assume you have obtained the audio sample from the user's microphone
        audio_sample = request.FILES.get('audio_data')  # Get the uploaded audio file

        # Construct the request payload with the audio sample
        payload = {
            'audio': audio_sample,
            # Add other necessary parameters, such as API key, etc.
        }

        # Make a POST request to Shazam's API endpoint for recognition
        response = requests.post('https://api.shazam.com/songs/recognize', data=payload)
        print(f"response: {response}")
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON to extract song metadata
            song_data = response.json()
            song_title = song_data['title']
            artist_name = song_data['artist']

            print(f"song_data: {song_data}")
            # Extract other relevant song metadata

            # Return the recognized song information as a response
            context = {
                'title': song_title,
                'artist': artist_name,
                # Include other song metadata as needed
            }
        else:
            # Handle the case where recognition failed
            print(f"(error: 'Recognition failed', status=500")
    
    context = {}
    return render(request, 'a_collections/shazam.html', context)


""" Function to get al albums from a given artist 
    input: musicbrainz artist_id
    output: list of albums from the artis

"""
def artist_discography(request):
    offset = 0
    limit = 10  # You can adjust this value based on your needs

    if request.method == 'POST':
        artist_name = request.POST.get('artist')
        print(f"artist that we are looking for: {artist_name}")
        
        artist = Artist.objects.filter(name__icontains=artist_name).first()

        if artist:
            # Make a request to the MusicBrainz API to get information about the artist
            # response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}?inc=release-groups&fmt=json')
            # TODO: limit and offset dont work
            # response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}?inc=release-groups&type=album|single&fmt=json&limit={limit}&offset={offset}')
            response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}?inc=release-groups&type=album|single&fmt=json&limit=100')
            # response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}?inc=release-groups&type=album|single&fmt=json')

            # response = requests.get(f'http://musicbrainz.org/ws/2/release-group/?query=artist:"{artist_name}"&fmt=json&limit={limit}&offset={offset}')

            # response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}?inc=release-groups&type=album|single&fmt=json')

            # response = requests.get(f'https://musicbrainz.org/ws/2/release?artist={artist.musicbrainz_id}&fmt=json&inc=release-groups&limit=100&offset=300')
            print(f"offset = {offset} and limit = {limit}")
            print("###############")
            print("###############")

            # response = requests.get(f'https://musicbrainz.org/ws/2/artist/{artist.musicbrainz_id}')
            print(f"data: {response}")
            if response.status_code == 200:
                data = response.json()
                print("###### DATA ###########")
                print(f"{data}")
                print("#######################")
                
                # Print artist information
                print("Artist Name:", data.get("name"))
                try:
                    print("Begin Area:", data.get("begin-area", {}).get("name"))
                except:
                    print("Begin Area:", data.get("begin-area"))
                print("Country:", data.get("country"))
                print("Life Span:", data.get("life-span"))
                print()

                # Print Wikipedia link if available
                artist_wikipedia(artist_name)
                # artist_wikipedia(data.get("name"))

                # Print tags if available
                print(f"musicbrainz id: {data.get("id")}")
                artist_tags(data.get("id"))

                # ORIGINAL CODE:
                # artist_name = data['name']
                artist_name = artist_name
                albums = []
                # Extract relevant information about the artist's albums
                idx = 1
                for release_group in data['release-groups']:
                    primary_type = release_group.get('primary-type')
                    if primary_type:
                    # if release_group['primary-type']:  # Filter only albums
                        album = {
                            'year_released': release_group.get('first-release-date', '').split('-')[0],
                            'name': release_group['title'],
                            'musicbrainz_id': release_group['id'],
                            'release_id' : release_group['id'],
                            'primary_type' : release_group['primary-type'],
                            # 'primary_type' : release_group.get('primary-type'),  # Get the primary-type or None if not found
                            'secondary_types' : release_group.get('secondary-types', []),
                            'secondary_type_ids' : release_group.get('secondary-type-ids', []),
                        }
                        print(f"{idx} | item : {album}")
                        idx +=1
                        albums.append(album)
                
                # print(albums)
                # Pass artist name and albums to the template
                
                # Sort albums in a way they can be used in teh template
                album_list = []
                single_list = []
                ep_list = []

                for album in albums:
                    # print(f"album {album} | {album['primary_type']} | {album.get('primary_type')}")
                    if album['primary_type'] == 'Album':
                        album_list.append(album)
                        # print(f"album in here: {album}")
                    elif album['primary_type'] == 'Single' :
                        single_list.append(album)
                        print(f" single: {album}")
                    elif album['primary_type'] == 'Ep' :
                        print(f" ep: {album}")
                        ep_list.append(album)

                context = {
                    'artist_name': artist_name,
                    'albums': albums,
                    'album_list' : album_list,
                    'single_list' : single_list,
                    'ep_list' :  ep_list,
                }

                return render(request, 'a_collections/artist_overview.html', context)
            else:
                # Handle error response from the API
                print("message: Failed to fetch artist information")
                messages.success(request, f'Failed to fetch artist information for {artist_name}')  

        else:
                print("message: no artist found with this name in the database")
                messages.success(request, f'No artist withthe name {artist_name} found in the database')  
    return render(request, "a_collections/artist_overview.html")


def artist_wikipedia(artist_name):
    # als er een ' in de artist name zit, deze omzetten naar een %27
    if "'" in artist_name:
        # Vervang het enkele citaat-teken door "%27"
        new_artist_name = artist_name.replace("'", "%27")
        print(f"New artist name: {artist_name}")
    else:
        new_artist_name = artist_name

    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={artist_name}&prop=extracts&format=json&exintro=1"

    response = requests.get(url)
    data = response.json()
    # print(f"wikipedia response: {response}")
    # print(f"wikipedia data: {data}")

    # Extract Wikipedia URL
    pages = data.get("query", {}).get("pages", {})
    # print(f"wikipedia pages: {pages}")

    if pages:
        page_id = list(pages.keys())[0]
        wikipedia_url = pages[page_id].get("fullurl", "")
        print("Wikipedia URL:", wikipedia_url)

        # Haal de pagina-ID op van de artiest
        page_ids = data['query']['pages'].keys()
        print(f"page_ids: {page_ids}")
        page_id = next(iter(page_ids))
        print(f"page_id: {page_id}")

        if page_id != '-1':
            # Haal de eerste paragraaf op uit de extracten als beschikbaar, anders leeg laten
            first_paragraph = data['query']['pages'][page_id].get('extract', '')
            # print(f"Wikipedia first paragraph: {first_paragraph}")
    else:
        print("Wikipedia URL not found.")
    return first_paragraph


def artist_tags(artist_id):
    url = f"https://musicbrainz.org/ws/2/artist/{artist_id}/tags?fmt=json"

    response = requests.get(url)
    data = response.json()

    # Print genre tags if available
    tags = data.get("tags", [])
    if tags:
        print("Genre Tags:")
        for tag in tags:
            print(tag.get("name"))
    else:
        print("No genre tags found.")




from django.shortcuts import render
from .utils import get_artists_from_hitdossier_online  # Import your scraping function

def hitdossier_create(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            artists = get_artists_from_hitdossier_online(url)
            return render(request, 'a_collections/hitdossier_create.html', {'artists': artists})
    return render(request, 'a_collections/hitdossier_create.html')


