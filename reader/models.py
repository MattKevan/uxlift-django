from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
import feedparser
import requests  # Make sure you have this line
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.contrib.auth.models import User  # Add this line
from django.utils import timezone
import tagulous.models
import os
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from django.conf import settings
from django.db import models

class Topic(tagulous.models.TagModel):
    class TagMeta:
        # Tag options go here (optional)
        pass

class Site(models.Model):
    STATUS_CHOICES = [
        ('D', 'Draft'),
        ('P', 'Published'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    feed_url = models.URLField(null=True, blank=True)
    site_icon = models.ImageField(upload_to='site_icons/', null=True, blank=True)

    def __str__(self):
        return self.title

    def find_feed(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        feed_urls = [link['href'] for link in soup.find_all('link', type='application/rss+xml')]
        if feed_urls:
            self.feed_url = feed_urls[0]
        else:
            self.feed_url = None

    def find_meta_info(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Fetch site title
        if not self.title:
            meta_title = soup.find("meta", property="og:title") or soup.find("title")
            if meta_title:
                self.title = meta_title.get("content", "") or meta_title.text

        # Fetch site description
        if not self.description:
            meta_description = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
            if meta_description:
                self.description = meta_description.get("content", "")

    def find_and_save_icon(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        icon_link = soup.find("link", rel="shortcut icon")
        if icon_link:
            icon_url = icon_link['href']
            icon_url = urljoin(self.url, icon_url)
            
            icon_response = requests.get(icon_url)
            if icon_response.status_code == 200:
                file_name = os.path.basename(icon_url)
                self.site_icon.save(file_name, ContentFile(icon_response.content), save=False)

    def fetch_posts(self):
        if self.feed_url is None:
            print(f"No valid feed URL found for site: {self}")
            return

        feed = feedparser.parse(self.feed_url)
        for entry in feed.entries:
            title = entry.title
            content = entry.description if 'description' in entry else ''  # Use description field here
            link = entry.link
            date_published = parse(entry.published) if 'published' in entry else None
            image = entry.get('image', '')
            categories = ", ".join(term['term'] for term in entry.tags if 'term' in term) if 'tags' in entry else ''
            try:
                post = Post.objects.get(site=self, title=title, url=link)
                # If post exists, update the fields
                changes_made = False
                if post.content != content:
                    post.content = content
                    changes_made = True
                if post.date_published != date_published:
                    post.date_published = date_published
                    changes_made = True
                if post.image_path != image:  
                    post.image_path = image
                    changes_made = True
                if post.categories != categories:
                    post.categories = categories
                    changes_made = True
                # Only save if changes were made
                if changes_made:
                    post.save()
            except Post.DoesNotExist:
                # If post does not exist, create a new one
                Post.objects.create(
                    site=self,
                    title=title,
                    content=content,
                    url=link,
                    date_published=date_published,
                    image_path=image,  # use image_path instead of image
                    categories=categories,
                )

    def save(self, *args, **kwargs):
        # Check if the user is in the 'Editor' group
        if self.user.groups.filter(name='Editor').exists():
            self.status = 'P'  # Set status to 'Published'

        self.find_feed()  # Update the feed url before saving
        self.find_meta_info()
        self.find_and_save_icon()

        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Fetch posts after the site is saved, so we have an ID to associate posts with
        if self.status == 'P':  # Change this to match your 'published' status value
            self.fetch_posts()



class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default=timezone.now)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    site_name = models.CharField(max_length=200, null=True, blank=True) # new field for site name
    site_title = models.CharField(max_length=200, null=True, blank=True) # new field for site title
    site_icon = models.URLField(null=True, blank=True) # new field for site icon URL
    title = models.CharField(max_length=200)
    url = models.URLField()
    image_path = models.URLField(null=True, blank=True) # or models.ImageField() depending on how you are handling images
    content = models.TextField(blank=True)  # the introduction or excerpt field
    topics = tagulous.models.TagField(to=Topic)
    categories = models.CharField(max_length=200, null=True, blank=True)  # or a many-to-many relation to a Category model
    date_published = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


from django.db import models
from django.utils import timezone
import tagulous.models

# Assuming SharedTopic is already defined as your shared tag model
class Tool(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.URLField()
    image = models.ImageField(upload_to='tools_images/')
    date = models.DateTimeField(default=timezone.now)
    topics = tagulous.models.TagField(to='Topic')  # Referencing your shared topic model
    body = models.TextField()  # This can be used for the full content of the tool

    def __str__(self):
        return self.title
