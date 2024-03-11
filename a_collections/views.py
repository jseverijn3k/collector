from django.shortcuts import render

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
        # 'posts' : posts,
        # 'tag' : tag,
        # 'page' : page,
        'quote' :  quote
    }
    print (f"The quote is: {quote}")
    print (f"The context is: {context}")    
    
    # if request.htmx:
    #     return render(request, 'snippets/loop_home_posts.html', context)
    
    return render(request, "pages/home.html", context)
 
