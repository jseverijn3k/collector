from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse


from .forms import ProfileForm
from .models import Profile

# from a_posts.forms import ReplyCreateForm
# from a_posts.models import Post, Comment, LikedPost



def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            raise Http404()
        
    # posts = profile.user.posts.all()
    
    # if request.htmx:
    #     if 'top-posts' in request.GET:
    #         posts = profile.user.posts.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    #     elif 'top-comments' in request.GET:
    #         comments = profile.user.comments.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    #         # replyform = ReplyCreateForm()
    #         return render(request, 'snippets/loop_profile_comments.html', { 'comments': comments, 'replyform': replyform })
    #     elif 'liked-posts' in request.GET:
    #         posts = profile.user.likedposts.order_by('-likedpost__created') 
    #     return render(request, 'snippets/loop_profile_posts.html', { 'posts': posts })
    
    context = {
        'profile': profile,
        # 'posts': posts,
    }
    
    return render(request, 'a_users/profile.html', context)


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':    
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')

    # if the user is onboarding, we show a different template    
    if request.path == reverse('profile-onboarding'):
        template = 'a_users/profile_onboarding.html'
    else:
        template = 'a_users/profile_edit.html'
    
    return render(request, template,{'form' : form})


@login_required
def profile_delete_view(request):
    user = request.user

    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')

    return render(request, 'a_users/profile_delete.html',{})
