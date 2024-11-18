# Generated by Django 5.1.2 on 2024-11-07 21:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0008_remove_studentprofile_courses_question_exam"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="question",
            name="assigned_subject",
        ),
        migrations.AlterField(
            model_name="question",
            name="exam",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="home.exam",
            ),
        ),
    ]