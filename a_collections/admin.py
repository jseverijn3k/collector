from django.contrib import admin

# Register your models here.
from .models import Release, Artist, Collection, Record_Label, Cover_Art

admin.site.register(Release)
admin.site.register(Cover_Art)
admin.site.register(Artist)
admin.site.register(Collection)
admin.site.register(Record_Label)