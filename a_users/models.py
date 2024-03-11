from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CharField,
    DateField,
    DateTimeField,
    ImageField,
    PositiveSmallIntegerField,
    EmailField,
    TextField,
)
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static




# class User(AbstractUser):
#     """
#     Default custom user model for Yovta v2.
#     If adding fields that need to be filled at user signup,
#     check forms.SignupForm and forms.SocialSignupForms accordingly.
#     """

#     GENDER_MALE = 1
#     GENDER_FEMALE = 2
#     GENDER_OTHER = 3
#     GENDER_DONT_WANT_TO_TELL = 4
#     GENDER_CHOICES = [
#         (GENDER_MALE, _("Male")),
#         (GENDER_FEMALE, _("Female")),
#         (GENDER_OTHER, _("Other")),
#         (GENDER_DONT_WANT_TO_TELL, _("N/A")),
#     ]

#     #: First and last name do not cover name patterns around the globe
#     name = CharField(_("Name of User"), blank=True, max_length=255)
#     first_name = None  # type: ignore
#     last_name = None  # type: ignore
#     image = ImageField(upload_to="users/profiles/avatars/", null=True, blank=True)
#     birthday = DateField(null=True, blank=True)
#     gender = PositiveSmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)

#     email = EmailField(unique=True, null=True)
#     location = CharField(max_length=20, null=True, blank=True)
#     bio = TextField(null=True, blank=True)
#     role = CharField(max_length=50, null=True, blank=True)
    
#     created_at = DateTimeField(auto_now_add=True)
#     updated_at = DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Profile")
#         verbose_name_plural = _("Profiles")

#     def get_absolute_url(self):
#         """Get url for user's detail view.

#         Returns:
#             str: URL for user detail.

#         """
#         return reverse("users:detail", kwargs={"username": self.username})

#     @property
#     def avatar(self):
#         try:
#             url = self.image.url
#             print("avatar url", url)
#         except Exception as e:
#             url = ""
#             print("avatar url exception", e)
#         return url

#     @property
#     def realname(self):
#         if self.name:
#             realname = self.name
#             print(f"realname: {realname}")
#         else:
#             realname = self.username
#         return realname
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    realname = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    location = models.CharField(max_length=20, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)
    
    @property
    # check if there is an image, if not, return default avatar
    def avatar(self):
        try: 
            avatar = self.image.url
        except:
            avatar = static('images/avatar_default.svg')
        return avatar

    @property
    # check if there is a realname, if not, return username
    def name(self):
        if self.realname:
            name = self.realname
            print(f"realname: {name}")
        else:
            name = self.user.username
        return name
