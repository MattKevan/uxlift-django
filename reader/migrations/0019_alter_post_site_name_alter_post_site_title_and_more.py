# Generated by Django 4.2 on 2023-12-12 17:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0018_alter_site_site_icon_alter_site_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="site_name",
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="site_title",
            field=models.CharField(blank=True, max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="title",
            field=models.CharField(max_length=600),
        ),
    ]
