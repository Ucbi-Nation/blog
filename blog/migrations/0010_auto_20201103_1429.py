# Generated by Django 3.0.7 on 2020-11-03 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20201103_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='comments',
            name='dislikes',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='comments',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]
