# Generated by Django 3.0.7 on 2020-11-03 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_commentpreference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comments',
            name='email',
        ),
    ]