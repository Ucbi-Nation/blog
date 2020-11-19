from django.db import models
from django.utils import timezone
from tinymce import HTMLField
from django.contrib.auth.models import User
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import slugify

class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    likes= models.IntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    dislikes= models.IntegerField(default=0)
    title = models.CharField(null=True, max_length=100)
    timestamp = models.DateTimeField(null=True,auto_now_add=True)
    slug = models.SlugField()
    date_posted = models.DateTimeField(default=timezone.now)
    content = HTMLField()
    thumbnail = models.ImageField(null=True, blank=True, upload_to='images/product')
    categories = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag)
    featured = models.BooleanField(default=False)
    top = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        original_slug = slugify(self.title)
        queryset = Post.objects.all().filter(slug__iexact=original_slug).count()

        count = 1
        slug = original_slug
        while (queryset):
            slug = original_slug + '-' + str(count)
            count += 1
            queryset = Post.objects.all().filter(slug__iexact=slug).count()

        self.slug = slug

        if self.featured:
            try:
                temp = Post.objects.get(featured=True)
                if self != temp:
                    temp.featured = False
                    temp.save()
            except Post.DoesNotExist:
                pass
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def number_of_comments(self):
        return Comment.objects.filter(post_connected=self).count()

    @property
    def imageURL(self):
        try:
            url = self.thumbnail.url
        except:
            url = ''
        return url \

    @property
    def ct(self):
        for i in range(1,100):
            x=i
        return x+1


    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'pk': self.pk
        })

    def get_update_url(self):
        return reverse('post-update', kwargs={
            'pk': self.pk
        })

    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'pk': self.pk
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')

    @property
    def comment_count(self):
        return Comments.objects.filter(post=self).count()



class Comment(models.Model):
    content = models.TextField(max_length=150)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_connected = models.ForeignKey(Post, on_delete=models.CASCADE)

class Comments(MPTTModel):
    author = models.ForeignKey(User, blank=True, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE,
                            null=True, blank=True, related_name='children')
    likes = models.IntegerField(default=0)
    thumbnail = models.ImageField(null=True, blank=True, upload_to='images/comment')
    dislikes = models.IntegerField(default=0)
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)


    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['publish']


    def get_update_url(self):
        return reverse('comment-update', kwargs={
            'pk': self.pk
        })


    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'pk': self.pk
        })

    @property
    def imageURL(self):
        try:
            url = self.thumbnail.url
        except:
            url = ''
        return url



class Preference(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    post= models.ForeignKey(Post, on_delete=models.CASCADE)
    value= models.IntegerField()
    date= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.user) + ':' + str(self.post) +':' + str(self.value)

    class Meta:
       unique_together = ("user", "post", "value")

class CommentPreference(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    post= models.ForeignKey(Comments, on_delete=models.CASCADE)
    value= models.IntegerField()
    date= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.user) + ':' + str(self.post) +':' + str(self.value)

    class Meta:
       unique_together = ("user", "post", "value")
