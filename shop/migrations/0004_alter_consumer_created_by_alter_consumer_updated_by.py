# Generated by Django 5.0.3 on 2024-04-03 10:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_payment_created_by_alter_payment_updated_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='consumer',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_consumers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='consumer',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_consumers', to=settings.AUTH_USER_MODEL),
        ),
    ]