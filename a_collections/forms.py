from django.forms import ModelForm
from django import forms 

from .models import Media, Artist

class MediaCreateForm(ModelForm):
    class Meta:
        model = Media
        fields = "__all__"
        # fields = ['url', 'body', 'tags']
        # labels = {
        #     'body' : 'Caption',
        #     'tags' : 'Category',
        # }
        # widgets = {
        #     'body' : forms.Textarea(attrs={'rows' : 3, 'placeholder' : 'Add a caption ...', 'class': 'font1 text-4xl'}),
        #     'url' : forms.TextInput(attrs={'placeholder' : 'Add a url ...', 'class': 'font1 text-4xl'}),
        #     'tags' : forms.CheckboxSelectMultiple(),
        # }
       
class MediaEditForm(ModelForm):
    class Meta:
        model = Media
        fields = "__all__"
        # fields = ['body', 'tags']
        # labels = {
        #     'body' : '',
        #     'tags' : 'Category',
        # }
        # widgets = {
        #     'body' : forms.Textarea(attrs={'rows' : 3, 'class': 'font1 text-4xl'}),
        #     'tags' : forms.CheckboxSelectMultiple(),
        # }

class ArtistCreateForm(ModelForm):
    class Meta:
        model = Artist
        fields = "__all__"
        # fields = ['url', 'body', 'tags']
        # labels = {
        #     'body' : 'Caption',
        #     'tags' : 'Category',
        # }
        # widgets = {
        #     'body' : forms.Textarea(attrs={'rows' : 3, 'placeholder' : 'Add a caption ...', 'class': 'font1 text-4xl'}),
        #     'url' : forms.TextInput(attrs={'placeholder' : 'Add a url ...', 'class': 'font1 text-4xl'}),
        #     'tags' : forms.CheckboxSelectMultiple(),
        # }
       
class ArtistEditForm(ModelForm):
    class Meta:
        model = Artist
        fields = "__all__"
        # fields = ['body', 'tags']
        # labels = {
        #     'body' : '',
        #     'tags' : 'Category',
        # }
        # widgets = {
        #     'body' : forms.Textarea(attrs={'rows' : 3, 'class': 'font1 text-4xl'}),
        #     'tags' : forms.CheckboxSelectMultiple(),
        # }
