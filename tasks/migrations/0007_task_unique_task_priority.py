# Generated by Django 4.0.1 on 2022-01-22 12:09

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0006_task_priority"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="task",
            constraint=models.UniqueConstraint(
                django.db.models.expressions.F("priority"),
                django.db.models.expressions.F("user"),
                condition=models.Q(("deleted", False), ("completed", False)),
                name="unique_task_priority",
            ),
        ),
    ]