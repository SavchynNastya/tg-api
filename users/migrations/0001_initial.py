# # Generated by Django 4.2.6 on 2023-10-29 19:45

# from django.db import migrations, models
# import django.db.models.deletion
# import django.utils.timezone


# class Migration(migrations.Migration):

#     initial = True

#     operations = [
#         migrations.CreateModel(
#             name='Chat',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('name', models.CharField(max_length=50, null=True)),
#                 ('chat_pic', models.ImageField(blank=True, null=True, upload_to='pictures/chat/')),
#             ],
#         ),
#         migrations.CreateModel(
#             name='CustomUser',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('password', models.CharField(max_length=128, verbose_name='password')),
#                 ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
#                 ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
#                 ('username', models.CharField(max_length=30, unique=True)),
#                 ('phone_number', models.CharField(max_length=40, unique=True)),
#                 ('profile_pic', models.ImageField(blank=True, null=True, upload_to='pictures/profile/')),
#                 ('status', models.CharField(blank=True, max_length=30)),
#                 ('is_active', models.BooleanField(default=True)),
#                 ('is_staff', models.BooleanField(default=False)),
#                 ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
#                 ('otp_secret', models.CharField(max_length=29)),
#                 ('last_seen', models.DateTimeField(null=True)),
#                 ('groups', models.ManyToManyField(blank=True, related_name='customuser_set', to='auth.group', verbose_name='groups')),
#                 ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_set', to='auth.permission', verbose_name='user permissions')),
#             ],
#             options={
#                 'abstract': False,
#             },
#         ),
#         migrations.CreateModel(
#             name='UserSettings',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('hide_phone_number', models.BooleanField(default=False)),
#                 ('hide_photo', models.BooleanField(default=False)),
#                 ('hide_online', models.BooleanField(default=False)),
#                 ('blocked_users', models.ManyToManyField(null=True, to='users.customuser')),
#                 ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_settings', to='users.customuser')),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Message',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('created_at', models.DateTimeField(auto_now_add=True)),
#                 ('text', models.TextField()),
#                 ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='users.chat')),
#                 ('likes', models.ManyToManyField(null=True, to='users.customuser')),
#                 ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='users.customuser')),
#             ],
#         ),
#         migrations.CreateModel(
#             name='Folder',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('name', models.CharField(max_length=50)),
#                 ('chats', models.ManyToManyField(null=True, related_name='folder', to='users.chat')),
#                 ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.customuser')),
#             ],
#         ),
#         migrations.CreateModel(
#             name='ChatUser',
#             fields=[
#                 ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
#                 ('role', models.CharField(choices=[('owner', 'owner'), ('editor', 'editor'), (None, None)], max_length=10, null=True)),
#                 ('chat', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.chat')),
#                 ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_users', to='users.customuser')),
#             ],
#         ),
#         migrations.AddField(
#             model_name='chat',
#             name='users',
#             field=models.ManyToManyField(related_name='chats', to='users.customuser'),
#         ),
#     ]
