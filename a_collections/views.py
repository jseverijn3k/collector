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

from a_collections.utils import artist_search, release_search, milliseconds_to_minutes_seconds
from a_collections.models import Artist, Release, Cover_Art, Record_Label, Collection, Track
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

    if request.method == 'GET':
        artist_name = request.GET.get('artist_name')
        album_name = request.GET.get('album_name')

        results = release_search(artist_name, album_name)

        # Assuming 'result' is the dictionary containing the JSON data
        for release in results['release-list']:
            release_id = release.get('id', None)
            # in_collection = Collection.objects.filter(release.musicbrainz_id = release_id)
            ext_score = release.get('ext:score', None)
            name = release.get('title', '')

            # artist_id = release['artist-credit'][0].get('id', None) if 'artist-credit' in release else None
            artist_id = release['artist-credit'][0]['artist']['id'] if 'artist-credit' in release and release['artist-credit'] else ''
            artist = release['artist-credit'][0]['name'] if 'artist-credit' in release else ''
            country_date = release.get('country', '') + ' ' + release.get('date', '') if any(key in release for key in ['country', 'date']) else ''
            label_info = release.get('label-info-list', [])
            label = label_info[0].get('label', {}).get('name', '') if label_info else ''
            label_id = label_info[0].get('label', {}).get('id', '') if label_info else ''
            catalog_number = label_info[0].get('catalog-number', '') if label_info else ''
            barcode = release.get('barcode', '')
            language = release.get('text-representation', {}).get('language', '')
            release_type = release['release-group']['primary-type'] if 'release-group' in release else ''
            status = release.get('status', '')

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
            # print("Release_id:", release_id)
            # print("Name:", name)
            # print("Artist_id:", artist_id)

            # print("Artist:", artist)
            # print("Format:", format)

            # if cd_tracks > 0 and dvd_tracks == 0:
            #     print(f"Tracks: {cd_tracks}")
            # elif cd_tracks > 0 and dvd_tracks >0:
            #     print(f"Tracks: {cd_tracks} + {dvd_tracks}")
            # elif cd_tracks == 0 and dvd_tracks >0:
            #     print(f"Tracks: {dvd_tracks}")

            # print("Country/Date:", country_date)
            # print("Label:", label)
            # print("Label_id:", label_id)

            # print("Catalog#:", catalog_number)
            # print("Barcode:", barcode)
            # print("Language:", language)
            # print("Release_type:", release_type)
            # print("Status:", status)
            # print()

            result_info = {
                # album info
                'release_id': release_id,
                'ext_score': ext_score,
                'name': name,
                
                # artist info
                'artist_id': artist_id,
                'artist': artist,
                
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

        print(f"id: {artist_id} | name: {artist_name} | ext_score: {ext_score}")
        
        user = request.user
        artist = Artist.objects.filter(musicbrainz_id=artist_id).first()
        release = Release.objects.filter(musicbrainz_id=release_id).first()
        collection = Collection.objects.filter(release=release, user=user).first()
        
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
                artist=artist,
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
                    cover_art = Cover_Art.objects.filter( musicbrainz_id = musicbrainz_id).first()
                    # print(f"covert art: {cover_art}")

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
