from django.shortcuts import render
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

import requests 
import csv
from django.http import HttpResponse

from a_collections.models import Artist, Media
from a_collections.forms import MediaCreateForm, MediaEditForm, ArtistCreateForm, ArtistEditForm

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


    quote = 'Record collecting is the hobby of collecting sound recordings, usually of music, but sometimes poetry, reading, historical speeches, and ambient noises. Although the typical focus is on vinyl records, all formats of recorded music can be collected.'
    context = {
        'tag' : tag,
        # 'page' : page,
        'artists' : Artist.objects.all(),
        'albums' : Media.objects.all(),
        'quote' :  quote,
    }
    print (f"The quote is: {quote}")
    print (f"The context is: {context}")    
    
    # if request.htmx:
    #     return render(request, 'snippets/loop_home_posts.html', context)
    
    return render(request, "pages/home.html", context)
 


@login_required
def media_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = MediaCreateForm(request.POST)
        if form.is_valid():
            media = form.save(commit=False)

            # website = requests.get(form.data['url'])
            # sourcecode = BeautifulSoup(website.text, 'html.parser')
            # # print(sourcecode)

            # find_image = sourcecode.select('meta[content^="https://live.staticflickr.com/"]')
            # print(find_image)
            # image = find_image[0]['content']
            # post.image = image

            # find_title = sourcecode.select('h1.photo-title')
            # titile = find_title[0].text.strip()
            # post.title = titile

            # find_artist = sourcecode.select('a.owner-name') 
            # artist = find_artist[0].text.strip()    
            # post.artist = artist

            media.user = request.user

            media.save()
            # media.save_m2m() # save our tags m2m field
            return redirect('home')
        
    form = MediaCreateForm()
    return render(request, "a_collections/media_create.html", {'form' : form})


@login_required
def media_delete_view(request, pk):
    media = get_object_or_404(Media, id=pk, user=request.user)

    if request.method == 'POST':
        media.delete()
        messages.success(request, 'Media deleted successfully')  
        return redirect('home')
    
    return render(request, "a_collections/media_delete.html", {'media' : media})


@login_required
def media_edit_view(request, pk):
    media = get_object_or_404(Media, id=pk, user=request.user)
    form = MediaEditForm(instance=media)

    context = {
        'post' : media,
        'form' : form,
    }
    
    if request.method == 'POST' and request.user == media.user:
        form = MediaEditForm(request.POST, instance=media)
        if form.is_valid():
            form.save()
            messages.success(request, 'Media updated successfully')  
            return redirect('home')

    
    return render(request, "a_collections/media_edit.html", context)


def media_page_view(request, pk):
    media = get_object_or_404(Media, id=pk)

    # if request.htmx:
    #     # check if top is part of the url
    #     if 'top' in request.GET:
    #         # comments = post.comments.filter(likes__isnull=False).distinct()
            
    #         # annotate(num_likes=Count('likes')) -> counts all the likes and stores them in the variable num_likes
    #         # .filter(num_likes__gt=0) -> filters if the numk_likes is greater than 0 (gt0)
    #         print("TESTTEST")
    #         comments = media.comments.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    #     else:
    #         comments = post.comments.all()
    #     return render(request, 'snippets/loop_postpage_comments.html', {'comments': comments, 'replyform': replyform})
    
    context = {
        'media' : media,
        # 'commentform' : commentform,
        # 'replyform' : replyform,
    }
    
    return render(request, "a_collections/media_page.html", context)

@login_required
def artist_create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = ArtistCreateForm(request.POST)
        if form.is_valid():
            artist = form.save(commit=False)

            artist.user = request.user

            artist.save()
            # media.save_m2m() # save our tags m2m field
            return redirect('home')
        
    form = ArtistCreateForm()
    return render(request, "a_collections/artist_create.html", {'form' : form})


@login_required
def download_csv(request):
    # Create a HttpResponse object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write headers
    writer.writerow(['Artist name', 'Media title', 'Media type', 'Media release year', 'Media catalog nr', 'Record label'])

    media_data = Media.objects.all()
    print(media_data)
    artist_data = Artist.objects.all()
    print(artist_data)
    print("Now I am here")

    # Write data rows
    for obj1 in media_data:
        print(obj1)
        for obj2 in artist_data.filter(name=obj1.artist):
            writer.writerow([obj2.name, obj1.title, obj1.type, obj1.release_year, obj1.catalog_number, obj1.record_label])

    return response