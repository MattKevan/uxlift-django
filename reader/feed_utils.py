import feedparser
from dateutil.parser import parse
from django.conf import settings
from .models import Site, Post  # Import your Site and Post models

def fetch_posts_for_site(site):
    if site.feed_url is None:
        print(f"No valid feed URL found for site: {site}")
        return

    feed = feedparser.parse(site.feed_url)
    for entry in feed.entries:
        title = entry.title
        content = entry.get('description', '')  # Use description field
        link = entry.link
        date_published = parse(entry.published) if 'published' in entry else None
        image = entry.get('image', '')
        categories = ", ".join(term['term'] for term in entry.get('tags', []) if 'term' in term)

        post, created = Post.objects.get_or_create(
            site=site,
            title=title,
            url=link,
            defaults={
                'content': content,
                'date_published': date_published,
                'image_path': image,
                'categories': categories,
            }
        )

        # Update post if not created (existing post)
        if not created:
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

            if changes_made:
                post.save()

def fetch_posts_for_all_sites():
    for site in Site.objects.filter(include_in_feed=True):
        fetch_posts_for_site(site)
