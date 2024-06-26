from django.db import models
from django.conf import settings
import uuid
# Create your models here.

"""
The Artist of a release group, e.g. U2 or Phil Collins
""" 
class Artist(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=100
    )
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10)
    ext_score = models.IntegerField(null=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


"""
The Record Label of a release
""" 
class Record_Label(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=100
    )
    name = models.CharField(max_length=255)
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)

    def __str__(self):
        return self.name


"""
Abstract type, not buyable in a shop. e.g. all versions of U2's joshua tree form a release group
"""    
class Release_Group(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=100
    )
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)
    musicbrainz_type_id = models.CharField(blank=True, null=True, max_length=255)
    musicbrainz_primrary_type_id = models.CharField(blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="artists")
    primrary_type = models.CharField(blank=True, null=True, max_length=255)
    secondary_types = models.CharField(blank=True, null=True, max_length=255)
    secondary_type_ids = models.CharField(blank=True, null=True, max_length=255)
    first_release_date = models.DateField()

    def __str__(self):
        return f"{self.name} | {self.artist.name}"

    class Meta:
        ordering = ['name' , 'artist']


"""
What you can buy in a store like a digital download, Vinyl, Casette or a CD
"""    
class Release(models.Model):
    class Type(models.IntegerChoices):
        CD = 1  
        SACD = 2 
        DVD = 3  
        BLUE_RAY = 4  
        CD_SINGLE = 5  
        OTHER = 6
    
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=100
    )
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)
    name = models.CharField(max_length=255)
    type  = models.IntegerField(choices=Type.choices, default=1)
    catalog_number = models.CharField(max_length=20, null=True, blank=True)
    
    barcode = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    date = models.CharField(max_length=20, null=True, blank=True)
    format = models.CharField(max_length=20, null=True, blank=True)
    cd_tracks = models.IntegerField()
    dvd_tracks = models.IntegerField() 
    record_label = models.ForeignKey(Record_Label, on_delete=models.SET_NULL, null=True, blank=True, related_name="record_labels")
    # release_year = models.IntegerField(null=True, blank=True)
    # artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="artists")
    release_group = models.ForeignKey(Release_Group, on_delete=models.SET_NULL, null=True, related_name="release_group")
    
    def __str__(self):
        # return f"{self.name} | {self.release_group.artist.name}"
        return f"{self.name} "

    class Meta:
        ordering = ['name',]

"""
Tracks of the release. Eeleases within a release group can have a different track list 
(e.g. vinyl vs cd or cd's with different bonus tracks) 
"""
class Track(models.Model):
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name='tracks')
    title = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    position = models.IntegerField()
    duration = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.release.name} - {self.position} - {self.title}"
    

    class Meta:
        ordering = ['release' , 'position']


class Cover_Art(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    musicbrainz_id = models.CharField(unique=True, blank=True, null=True, max_length=255)
    release = models.ForeignKey(Release, on_delete=models.CASCADE, related_name="cover_art")
    image = models.ImageField(upload_to='cover_art/', null=True, blank=True)
    image_url = models.URLField()  # url to the coverartarchive website
    image_small_url = models.URLField()  # url to the coverartarchive website
    cover_art_type = models.CharField(blank=True, null=True, max_length=255) # Front, Back, etc...

    def __str__(self):
        return f"Cover Art for {self.release.name}"


class Collection(models.Model):
    class Condition(models.IntegerChoices):
        ORIGINAL = 1
        COPY = 2
        WANT = 3
        MAYBE = 4

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, max_length=100
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name="collections",
    )
    release = models.ForeignKey(Release, on_delete=models.SET_NULL, null=True)
    condition  = models.IntegerField(choices=Condition.choices, default=1)
    date_added = models.DateField(null=True, blank=True)
    description = models.TextField()
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user} | {self.release.name}"


class Tag(models.Model):
    name = models.CharField(max_length=20)
    image = models.FileField(upload_to='icons/', null=True, blank=True) # filefield instead of imagefield since we have to deal with svg files
    slug = models.SlugField(max_length=20, unique=True)
    order = models.IntegerField(null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['order']
