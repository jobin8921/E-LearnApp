# Generated by Django 5.1.2 on 2024-11-08 09:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0011_exam_end_time_exam_is_started_exam_start_time_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="exam",
            name="staff",
        ),
        migrations.AddField(
            model_name="exam",
            name="staff_profile",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="home.staffprofile",
            ),
            preserve_default=False,
        ),
    ]