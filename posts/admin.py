from django.contrib import admin

from .models import Group, Post, Comment, Follow, ProfilePhoto


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author") 
    search_fields = ("text",) 
    list_filter = ("pub_date",) 
    empty_value_display = "-пусто-"

class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "description", "slug") 
    search_fields = ("title",) 
    empty_value_display = "-пусто-"

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "author", "created") 
    search_fields = ("author",) 
    empty_value_display = "-пусто-"

class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author") 
    search_fields = ("user", "author",) 
    empty_value_display = "-пусто-"

class PhotoAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "photo") 
    search_fields = ("pk", "author",) 
    empty_value_display = "-пусто-"

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentsAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ProfilePhoto, PhotoAdmin)
