
from django.contrib import admin
from django.urls import path, include, re_path
from users import views as users_views
from chats import views as chats_views
from user_settings import views as settings_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(([
        path('auth/', include([
            path('login/', users_views.UserLoginView.as_view(), name='login'),
            path('logout/', users_views.logout, name='logout'),
            path('sign-up/', users_views.UserRegistrationView.as_view(), name='sign_up'),
            path('generate_otp/', users_views.generate_otp, name='generate_otp'),
        ])),
        path('users/', include([
            path('update-username-status/', users_views.update_username_and_status, name='update_username_and_status'),
            path('profile-pic/', users_views.update_profile_pic, name='update_profile_pic'),
            re_path(r'^(?P<id>[0-9]+|[a-zA-Z]+)/$', users_views.get_user, name='user_obj'),
        ])),
        path('settings/', include([
            path('', settings_views.user_settings, name='settings'),
            path('block-user/<int:id>/', settings_views.block_user, name='block_user'),
            path('unblock-user/<int:id>/', settings_views.unblock_user, name='unblock_user'),
        ])),
        path('chats/', include([
            path('', chats_views.create_chat, name='create_chat'),
            path('list/', chats_views.list_chats, name='chat_list'),
            path('<int:id>/', chats_views.get_chat, name='get_chat'),
            path('user/<int:user_id>/', chats_views.get_chats_by_user_id, name='get_chat_by_user_id'),
            path('<int:id>/user/<int:user_id>/', chats_views.get_chat_user, name='get_chat_user'),
            path('message/', include([
                path('', chats_views.send_message, name='send_message'),
                path('like/<int:id>/', chats_views.like_message, name='like_message'),
                path('delete/<int:id>/', chats_views.delete_message, name='delete_message'),
            ])),
            path('<int:id>/add-user/<int:user_id>/', chats_views.add_user, name='add_user'),
            path('<int:id>/delete-user/<int:user_id>/', chats_views.delete_user, name='delete_user'),
            path('<int:id>/role/<int:user_id>/', chats_views.grant_role, name='delete_message'),
        ])),
        path('folder/', include([
            path('', chats_views.create_folder, name='create_folder'),
            path('list/', chats_views.folder_list, name='folder_list'),
            path('<int:id>/', chats_views.get_folder_chats, name='folder_chats'),
            path('<int:id>/add/<int:chat_id>/', chats_views.add_to_folder, name='add_to_folder'),
            path('<int:id>/remove/<int:chat_id>/', chats_views.remove_from_folder, name='remove_from_folder'),
            path('<int:id>/delete/', chats_views.delete_folder, name='delete_folder'),
            path('<int:id>/rename/', chats_views.rename_folder, name='rename_folder'),
        ])),
    ], 'api'))),
]
