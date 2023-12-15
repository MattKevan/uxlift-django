import json
import logging
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from reader.models import Post, Site
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import posts from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        with open(json_file_path, 'r', encoding='utf-8') as file:
            posts_data = json.load(file)

            user = get_user_model().objects.get(id=1)  # Get the user with ID 1
            count = 0

            for item in posts_data:
                if item.get('Status') != 'Error':
                    title = item['title']
                    site_title = item.get('site')

                    if not site_title:  # Skip if site title is missing or null
                        self.stdout.write(f"Skipping item due to missing 'site' field: {title}")
                        continue

                    date_created_str = item.get('date_created')
                    date_published_str = item.get('date_published')

                    date_created = parse_datetime(date_created_str) if isinstance(date_created_str, str) else None
                    date_published = parse_datetime(date_published_str) if isinstance(date_published_str, str) else None

                    if not date_created:
                        date_created = date_published if date_published else timezone.now()

                    if not date_published:
                        date_published = date_created

                    site_slug = slugify(site_title)
                    site, created = Site.objects.get_or_create(slug=site_slug, defaults={'title': site_title})

                    if not Post.objects.filter(title=title, date_created=date_created).exists():
                        try:
                            topics_str = ', '.join(f'"{topic}"' if ' ' in topic else topic for topic in item.get('topics', [])) if 'topics' in item else None
                            tags_str = ', '.join(f'"{tag}"' if ' ' in tag else tag for tag in item.get('tags', [])) if 'tags' in item else None

                            post = Post(
                                title=title,
                                description=item.get('description', ''),
                                summary=item.get('summary', ''),
                                user=user,
                                date_created=date_created,
                                date_published=date_published,
                                site=site,
                                link=item.get('link', ''),
                                image_path=None,  # Assuming no image path in JSON; adjust as needed
                                topics=topics_str,
                                tags=tags_str
                            )
                            post.save()

                            count += 1
                            self.stdout.write(f"Imported {count}: {post.title}")
                        except Exception as e:
                            logging.error(f"Error importing post '{title}': {e}")
                    else:
                        self.stdout.write(f"Post '{title}' already exists and will not be re-imported.")

                else:
                    self.stdout.write(f"Skipping item due to 'Error' status: {item}")

        self.stdout.write(self.style.SUCCESS(f'Post import completed. {count} posts imported.'))
