# Generated by Django 5.1.2 on 2024-11-07 17:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="exam",
        ),
    ]