from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Site, Post  # import Post model
from dateutil.parser import parse
import feedparser  # make sure this library is installed
import requests
from feedparser.api import _FeedParserMixin

@shared_task
def fetch_posts(site_id):
    site = Site.objects.get(id=site_id)

    if site.feed_url is None:
        print(f"No valid feed URL found for site: {site}")
        return

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537"
    }

    response = requests.get(site.feed_url, headers=headers)
    feed = _FeedParserMixin().parse(response.content)

    for entry in feed.entries:
        title = entry.title
        content = entry.description if 'description' in entry else ''  # Use description field here
        link = entry.link
        date_published = parse(entry.published) if 'published' in entry else None
        image = entry.get('image', '')
        categories = ", ".join(term['term'] for term in entry.tags if 'term' in term) if 'tags' in entry else ''
        try:
            post = Post.objects.get(site=site, title=title, url=link)  # replace self with site
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
                site=site,  # replace self with site
                title=title,
                content=content,
                url=link,
                date_published=date_published,
                image_path=image,  # use image_path instead of image
                categories=categories,
            )
