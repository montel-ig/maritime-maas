# Generated by Django 3.1.7 on 2021-03-29 19:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("maas", "0004_add_ticketing_system"),
        ("gtfs", "0004_make_api_id_unique"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="feed",
            options={
                "default_related_name": "feeds",
                "verbose_name": "feed",
                "verbose_name_plural": "feeds",
            },
        ),
        migrations.AddField(
            model_name="feed",
            name="ticketing_system",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="feeds",
                to="maas.ticketingsystem",
                verbose_name="ticketing system",
            ),
        ),
    ]
