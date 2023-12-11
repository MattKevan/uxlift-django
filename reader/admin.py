from django.contrib import admin
from .models import Site, Post, Topic, Tool
import tagulous.admin
admin.site.register(Site)
admin.site.register(Post)
admin.site.register(Tool)

# Optional: Custom admin for SharedTopic
class SharedTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']  # Customize as needed

# Register the shared tag model
admin.site.register(Topic, SharedTopicAdmin)
