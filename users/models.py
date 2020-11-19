from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from blog.models import CommentPreference,Preference
from .constants import GENDER_CHOICE
from django_countries.fields import CountryField

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    city = models.CharField(max_length=256)
    country = CountryField(blank_label='(select country)')
    quote = models.CharField(max_length=512)

    def __str__(self):
        return f'{self.user.username} Profile'

    @property
    def followers(self):
        return Follow.objects.filter(follow_user=self.user).count()


    @property
    def following(self):
        return Follow.objects.filter(user=self.user).count()

    @property
    def comments(self):
        return CommentPreference.objects.filter(user=self.user).count()

    @property
    def likes(self):
        return Preference.objects.filter(user=self.user).count()

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save()

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Follow(models.Model):
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    follow_user = models.ForeignKey(User, related_name='follow_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def imageURL(self):
        try:
            xx = Profile.objects.get(user=self.user)
            url = xx.image.url
        except:
            url = ''
        return url