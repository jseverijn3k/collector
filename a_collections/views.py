from django.shortcuts import render
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

import requests 
import csv
from django.http import HttpResponse

from a_collections.utils import artist_search, release_search
from a_collections.models import Artist, Release, Cover_Art
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

    artist_search("Texas")

    quote = 'Record collecting is the hobby of collecting sound recordings, usually of music, but sometimes poetry, reading, historical speeches, and ambient noises. Although the typical focus is on vinyl records, all formats of recorded music can be collected.'
    context = {
        'tag' : tag,
        # 'page' : page,
        'artists' : Artist.objects.all(),
        'albums' : Release.objects.all(),
        'quote' :  quote,
    }
    
    # if request.htmx:
    #     return render(request, 'snippets/loop_home_posts.html', context)
    
    return render(request, "pages/home.html", context)
 


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
    release = get_object_or_404(release, id=pk, user=request.user)

    if request.method == 'POST':
        release.delete()
        messages.success(request, 'release deleted successfully')  
        return redirect('home')
    
    return render(request, "a_collections/release_delete.html", {'release' : release})


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
    print(f"cover art url: {cover_art_url}")
    # Send GET request to the cover art archive
    response = requests.get(cover_art_url)

    # Check if request was successful and cover art exists
    if response.status_code == 200:
        return response.json()  # Return the JSON data
    else:
        return None


    
def release_page_view(request, pk):
    release = get_object_or_404(release, id=pk)

    # if request.htmx:
    #     # check if top is part of the url
    #     if 'top' in request.GET:
    #         # comments = post.comments.filter(likes__isnull=False).distinct()
            
    #         # annotate(num_likes=Count('likes')) -> counts all the likes and stores them in the variable num_likes
    #         # .filter(num_likes__gt=0) -> filters if the numk_likes is greater than 0 (gt0)
    #         print("TESTTEST")
    #         comments = release.comments.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    #     else:
    #         comments = post.comments.all()
    #     return render(request, 'snippets/loop_postpage_comments.html', {'comments': comments, 'replyform': replyform})
    
    context = {
        'release' : release,
        # 'commentform' : commentform,
        # 'replyform' : replyform,
    }
    
    return render(request, "a_collections/release_page.html", context)

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
            ext_score = release.get('ext:score', None)
            name = release.get('title', '')

            # artist_id = release['artist-credit'][0].get('id', None) if 'artist-credit' in release else None
            artist_id = release['artist-credit'][0]['artist']['id'] if 'artist-credit' in release and release['artist-credit'] else ''
            artist = release['artist-credit'][0]['name'] if 'artist-credit' in release else ''
            country_date = release.get('country', '') + ' ' + release.get('date', '') if any(key in release for key in ['country', 'date']) else ''
            label_info = release.get('label-info-list', [])
            label = label_info[0].get('label', {}).get('name', '') if label_info else ''
            catalog_number = label_info[0].get('catalog-number', '') if label_info else ''
            barcode = release.get('barcode', '')
            language = release.get('text-representation', {}).get('language', '')
            type = release['release-group']['primary-type'] if 'release-group' in release else ''
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
                        print(f"id: {image_id} | image: {image_url} | type: {image_type} | thumbnails_small: {thumbnails_small}")
                        cover_art_images.append({'id': image_id, 'image': image_url, 'image_small': thumbnails_small, 'type': image_type})
                        print(cover_art_images)
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
            print("Catalog#:", catalog_number)
            print("Barcode:", barcode)
            print("Language:", language)
            print("Type:", type)
            print("Status:", status)
            print()

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
                'Catalog_number': catalog_number,
                'barcode': barcode,
                'language': language,
                'type': type,
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


@login_required
def add_artist_view(request):
    if request.method == 'POST':
        release_id = request.POST.get('release_id')
        release_name = request.POST.get('release_name')
        artist_id = request.POST.get('artist_id')
        artist_name = request.POST.get('artist_name')
        type = request.POST.get('type')
        ext_score = request.POST.get('ext_score')

        print(f"id: {artist_id} | name: {artist_name} | type: {type} ext_score: {ext_score}")

        # Check if the artist_id already exists in the database
        artist = Artist.objects.filter(musicbrainz_id=artist_id).first()
        print(f"Artist: {artist}")
        existing_album = Release.objects.filter(musicbrainz_id=release_id).first()

        # If the artist does not exist, create a new record
        if not artist:
            artist = Artist.objects.create(
                musicbrainz_id=artist_id,
                name=artist_name,
                type="",
                ext_score=ext_score
            )
            # Now the artist record is added to the database
            messages.success(request, f'Artist {artist} added successfully')  

        else:
            # The artist already exists in the database
            # You can choose to perform any other action here, if needed
            messages.success(request, f'Artist {artist_name} already in the database')  

        if not existing_album and release_id is not None:
            release = Release.objects.create(
                musicbrainz_id=release_id,
                name=release_name,
                artist=artist,
                
            )
            # Now the artist record is added to the database
            messages.success(request, f'release {release} added successfully')  

        else: 
            # The artist already exists in the database
            # You can choose to perform any other action here, if needed
            if existing_album:
                messages.success(request, f'release {existing_album} already in the database')  


        return redirect('home')  # Redirect to home page or any other page after adding artist
    return redirect('home')  # Redirect to home page if not a POST request


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