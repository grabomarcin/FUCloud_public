# Generated by Django 3.2 on 2021-06-15 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0004_rename_go_to_yout_files_button_context_go_to_your_files_button'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='used_space',
            field=models.FloatField(default=0),
        ),
    ]
