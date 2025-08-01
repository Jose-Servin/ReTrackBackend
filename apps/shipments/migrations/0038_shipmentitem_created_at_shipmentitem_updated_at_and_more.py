# Generated by Django 5.2 on 2025-06-21 17:10

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shipments", "0037_remove_carrier_unique_carrier_name_and_mc_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="shipmentitem",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shipmentitem",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="carrier",
            name="mc_number",
            field=models.CharField(
                max_length=50,
                validators=[
                    django.core.validators.RegexValidator(
                        message="MC number must be in the format 'MC' followed by 6 digits (e.g., MC123456).",
                        regex="^[mM][cC]\\d{6}$",
                    )
                ],
            ),
        ),
    ]
