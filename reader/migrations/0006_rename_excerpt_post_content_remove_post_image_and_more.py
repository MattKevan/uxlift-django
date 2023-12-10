# Generated by Django 4.2 on 2023-07-06 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0005_site_feed_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='excerpt',
            new_name='content',
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.RemoveField(
            model_name='post',
            name='post_date',
        ),
        migrations.AddField(
            model_name='post',
            name='categories',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='date_published',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='image_path',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
