# Generated by Django 4.2 on 2023-12-12 22:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reader", "0033_alter_site_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="site",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
