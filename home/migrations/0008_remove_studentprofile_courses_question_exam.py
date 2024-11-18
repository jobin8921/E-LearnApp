# Generated by Django 5.1.2 on 2024-11-07 21:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0007_studentprofile_courses_delete_student"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="studentprofile",
            name="courses",
        ),
        migrations.AddField(
            model_name="question",
            name="exam",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="home.exam"
            ),
        ),
    ]
