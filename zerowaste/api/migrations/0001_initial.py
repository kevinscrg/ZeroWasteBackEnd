# Generated by Django 4.2.3 on 2024-10-14 16:37

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("password", models.CharField(max_length=128)),
                (
                    "preferred_notification_hour",
                    models.IntegerField(blank=True, null=True),
                ),
                ("preferences", models.JSONField(blank=True, default=list)),
                ("allergies", models.JSONField(blank=True, default=list)),
                ("rated_recipes", models.JSONField(blank=True, default=dict)),
                ("saved_recipes", models.JSONField(blank=True, default=list)),
            ],
        ),
    ]
