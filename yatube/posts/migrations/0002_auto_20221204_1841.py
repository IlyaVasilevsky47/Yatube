# Generated by Django 2.2.6 on 2022-12-04 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="slug",
            field=models.SlugField(unique=True),
        ),
    ]
