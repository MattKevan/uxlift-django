from django.contrib import admin
from .models import Site, Post, Topic, Tool, SiteType
import tagulous.admin

admin.site.register(Tool)
admin.site.register(Post)



class TopicAdmin(tagulous.admin.TaggedModelAdmin):
    list_display = ['name', 'slug']
tagulous.admin.enhance(Topic, TopicAdmin)
admin.site.register(Topic, TopicAdmin)

class SiteTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']  # Customize as needed
tagulous.admin.register(SiteType, SiteTypeAdmin)

class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'include_in_newsfeed']
admin.site.register(Site)