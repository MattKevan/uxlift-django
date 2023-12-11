# Generated by Django 4.2 on 2023-12-11 19:05

from django.db import migrations, models
import django.utils.timezone
import tagulous.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0014_rename_topics_topic"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tool",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("link", models.URLField()),
                ("image", models.ImageField(upload_to="tools_images/")),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("body", models.TextField()),
                (
                    "topics",
                    tagulous.models.fields.TagField(
                        _set_tag_meta=True,
                        help_text="Enter a comma-separated tag string",
                        to="reader.topic",
                    ),
                ),
            ],
        ),
    ]
