# Generated by Django 3.2.11 on 2022-01-09 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20220109_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.ManyToManyField(related_name='tags', to='main.Tags'),
        ),
    ]
