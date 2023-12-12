import json
from django.core.management.base import BaseCommand
from reader.models import Site, SiteType
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import sites from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        with open(json_file_path, 'r', encoding='utf-8') as file:
            sites_data = json.load(file)

            for data in sites_data:
                site_slug = slugify(data['title'])
                site, created = Site.objects.get_or_create(slug=site_slug)

                site.title = data['title']
                site.description = data['description']
                site.url = data['url']
                site.feed_url = data.get('feed_url')

                # Handle site type tags
                if 'site_type' in data and isinstance(data['site_type'], list):
                    site_type_str = ', '.join([f'"{site_type}"' if ' ' in site_type else site_type for site_type in data['site_type']])
                    site.site_type = site_type_str

                site.save()

                # Additional logging for debugging
                self.stdout.write(f"SiteType tags after save for '{site.title}': {', '.join([str(tag) for tag in site.site_type.all()])}")

        self.stdout.write(self.style.SUCCESS('Site import completed.'))
