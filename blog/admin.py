from django.contrib import admin
from .models import Post,Preference,Category,Tag,Comments,CommentPreference


admin.site.register(Post)
admin.site.register(Comments)
admin.site.register(Preference)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(CommentPreference)
