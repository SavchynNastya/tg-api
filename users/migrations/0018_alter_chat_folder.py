# Generated by Django 4.2.5 on 2023-09-16 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_chat_category_name_folder_chat_folder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='folder',
            field=models.ManyToManyField(null=True, related_name='chats', to='users.folder'),
        ),
    ]
