# Generated by Django 4.2 on 2023-12-12 09:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0015_tool"),
    ]

    operations = [
        migrations.AddField(
            model_name="tool",
            name="slug",
            field=models.SlugField(blank=True, unique=True),
        ),
    ]