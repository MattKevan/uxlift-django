# Generated by Django 4.2 on 2023-12-11 18:02

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0013_rename_tagulous_post_topics_topics"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Topics",
            new_name="Topic",
        ),
    ]