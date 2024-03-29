from django.forms import ModelForm
from django import forms 


from .models import Release, Artist

from dal import autocomplete

class ArtistAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Artist.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
    

class ReleaseCreateForm(ModelForm):
    
    class Meta:
        model = Release
        fields = ('__all__')
        widgets = {
            'artist': autocomplete.ModelSelect2(url='artist-autocomplete')
        }
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
       
class ReleaseEditForm(ModelForm):
    class Meta:
        model = Release
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
