from django.template import Library
from django.db.models import Count

# from ..models import Tag, Post, Comment

register = Library()

@register.inclusion_tag('includes/sidebar.html')
def sidebar_view(tag=None, user=None):
    """
    Inclusion tag for rendering the sidebar with a list of all Tag categories.

    This template tag retrieves all Tag objects from the database and includes them in the
    'includes/sidebar.html' template. The list of categories is made available in the
    context dictionary under the key 'categories'.

    Usage in a template:
    {% load sidebar %}  <!-- Load the template tags -->
    {% sidebar_view %}  <!-- Include the rendered sidebar in the template -->
    """

    # categories = Tag.objects.all()
    # top_posts = Post.objects.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    # top_comments = Comment.objects.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by('-num_likes')
    context = { 
        # 'categories' : categories,
        # 'tag' : tag,
        # 'top_posts' : top_posts,
        'user' : user,
        # 'top_comments' : top_comments,
        }
    
    return context