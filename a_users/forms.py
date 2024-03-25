from django.forms import ModelForm
from django import forms

from .models import Profile

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'realname', 'email', 'location', 'bio']
        labels = {
            'image': 'Image',
            'realname': 'Name',
            'email': 'Email',
            'location': 'Location',
            'bio': 'Bio',
        }

        widgets = {
            'image' : forms.FileInput(),
            'bio' : forms.Textarea(attrs={'rows':3}),
        }
        help_texts = {
            'image': 'Upload a profile image',
            'realname': 'Enter your real name',
            'email': 'Enter your email',
            'location': 'Enter your location',
            'bio': 'Enter a short bio',
        }
        error_messages = {
            'image': {
                'max_length': 'This image name is too long.',
            },
        }