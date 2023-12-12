import json
from django.core.management.base import BaseCommand
from reader.models import Tool
from django.utils.text import slugify
from cloudinary.uploader import upload

class Command(BaseCommand):
    help = 'Import tools from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file_path = kwargs['json_file']

        with open(json_file_path, 'r', encoding='utf-8') as file:
            tools_data = json.load(file)

            for data in tools_data:
     

                tool_slug = slugify(data['title'])
                tool, created = Tool.objects.get_or_create(slug=tool_slug)

                tool.title = data['title']
                tool.description = data['description']
                tool.link = data['link']
                tool.date = data['date']
                tool.body = data['body']

                # Handling topics
                if 'topics' in data and isinstance(data['topics'], list):
                    # Convert list of topics into a comma-separated string, with quotes if necessary
                    topics_str = ', '.join(f'"{topic}"' if ' ' in topic else topic for topic in data['topics'])
                    tool.topics = topics_str
                else:
                    tool.topics = None

                tool.save()

                # Additional logging for debugging
                self.stdout.write(f"Topics after save for '{tool.title}': {', '.join([str(topic) for topic in tool.topics.all()])}")

        self.stdout.write(self.style.SUCCESS('Tool import completed.'))
