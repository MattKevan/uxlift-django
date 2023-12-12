from django.conf import settings
from django.contrib.auth.models import Group
from cloudinary.models import CloudinaryField
from django.db import models
import feedparser
import requests  # Make sure you have this line
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.contrib.auth.models import User  # Add this line
from django.utils import timezone
from tagulous.models import TagField, TagModel
import os
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from urllib.parse import urlparse

#from .feed_utils import fetch_posts_for_site

class Topic(TagModel):
    class TagMeta:
        # Tag options go here (optional)
        pass

class SiteType(TagModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    class TagMeta:
        # Tag options go here (optional)
        pass

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate slug from name
            self.slug = slugify(self.name)

            # Ensure the slug is unique
            original_slug = self.slug
            counter = 1
            while SiteType.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Site(models.Model):
    STATUS_CHOICES = [
        ('D', 'Draft'),
        ('P', 'Published'),
    ]
    title = models.CharField(max_length=1000)
    description = models.TextField()
    url = models.URLField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='D')
    feed_url = models.URLField(null=True, blank=True)
    site_icon = CloudinaryField('image', null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # Allow null for user
    site_type = TagField(to=SiteType, null=True)

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
            
            # Upload icon to Cloudinary and store the public_id
            if icon_url:
                try:
                    uploaded_image = upload(icon_url)
                    cloudinary_public_id = uploaded_image.get('public_id')
                    self.site_icon = cloudinary_public_id
                except Exception as e:
                    print(f"Error uploading icon for site '{self.title}': {e}")

    def save(self, *args, **kwargs):

        self.find_feed()  # Update the feed url before saving
        self.find_meta_info()
        self.find_and_save_icon()

        # Set default user if not provided
        if not self.user_id:
            default_user = get_user_model().objects.get(id=1)
            self.user = default_user

        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Optionally fetch posts after saving, if the site is included in feed
        #if self.include_in_feed:
        #   fetch_posts_for_site(self)

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(default=timezone.now)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True)
    site_name = models.CharField(max_length=1000, null=True, blank=True) # new field for site name
    site_title = models.CharField(max_length=1000, null=True, blank=True) # new field for site title
    site_icon = models.URLField(null=True, blank=True) # new field for site icon URL
    title = models.CharField(max_length=1000)
    url = models.URLField(max_length=1000)
    image_path = models.URLField(max_length=1000,null=True, blank=True) # or models.ImageField() depending on how you are handling images
    content = models.TextField(blank=True)  # the introduction or excerpt field
    topics = TagField(to=Topic)
    categories = models.CharField(max_length=1000, null=True, blank=True)  # or a many-to-many relation to a Category model
    date_published = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    def fetch_og_image(self):
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                return og_image["content"]
        except Exception as e:
            print(f"Error fetching OG image for post '{self.title}': {e}")
        return None
    
    def fetch_web_data(self):
        # Only fetch web data if content is blank
        if not self.content:
            try:
                response = requests.get(self.url)
                soup = BeautifulSoup(response.content, 'html.parser')
                og_description = soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else None
                if og_description:
                    self.content = og_description
            except Exception as e:
                print(f"Error while fetching web data for post '{self.title}': {e}")

    def find_or_create_site(self):
        post_url_parsed = urlparse(self.url)
        post_root_url = f"{post_url_parsed.scheme}://{post_url_parsed.netloc}"
        site, created = Site.objects.get_or_create(url=post_root_url)
        return site

    def save(self, *args, **kwargs):
        self.fetch_web_data()

        if not self.user_id:
            # Set default user if not provided
            default_user = get_user_model().objects.get(id=1)
            self.user = default_user

        # Get the og:image and save it to image_path
        if not self.image_path:
            self.image_path = self.fetch_og_image()

        # Match or create a Site and link it
        if not self.site:
            self.site = self.find_or_create_site()

        super().save(*args, **kwargs)

class Tool(models.Model):
    title = models.CharField(max_length=600)
    description = models.TextField()
    link = models.URLField()
    image = CloudinaryField('image')
    date = models.DateTimeField(default=timezone.now)
    topics = TagField(to='Topic')  # Referencing your shared topic model
    body = models.TextField()  # This can be used for the full content of the tool
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Tool, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
