from django.contrib import admin

# Register your models here.
from .models import Media, Artist, Collection, Record_Label

admin.site.register(Media)
admin.site.register(Artist)
admin.site.register(Collection)
admin.site.register(Record_Label)