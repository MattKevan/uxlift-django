# Generated by Django 4.2 on 2023-12-12 21:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0030_alter_site_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="content",
            field=models.TextField(null=True),
        ),
    ]
