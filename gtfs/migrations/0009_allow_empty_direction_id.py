# Generated by Django 3.1.7 on 2021-04-08 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gtfs", "0008_remove_calendar_and_calendar_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trip",
            name="direction_id",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="direction ID"
            ),
        ),
    ]
