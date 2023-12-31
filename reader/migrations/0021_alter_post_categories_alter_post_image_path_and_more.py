# Generated by Django 4.2 on 2023-12-12 18:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0020_alter_post_categories_alter_tool_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="categories",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="image_path",
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="site_name",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="site_title",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="post",
            name="url",
            field=models.URLField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="site",
            name="title",
            field=models.CharField(max_length=1000),
        ),
    ]
