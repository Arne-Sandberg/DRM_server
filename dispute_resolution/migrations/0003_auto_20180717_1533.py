# Generated by Django 2.0.7 on 2018-07-17 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dispute_resolution', '0002_contractcase_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='eth_account',
            field=models.CharField(db_index=True, max_length=70, unique=True, verbose_name='ETH Address'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='organization_name',
            field=models.CharField(default='Some org', max_length=150, verbose_name='Organization'),
        ),
    ]