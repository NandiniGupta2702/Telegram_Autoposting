
from apps.home import views as e
from django.urls import path
from .views import login_view,delete_user, register_user,configure_bot,  user_bot_data, run_bot, delete_bot, user_list, upload_csv_file, save_api_key, upload_csv_page, use_api_key, login_as_user, logout_view, bot_details, run_csv, update_bot
from django.contrib import admin

urlpatterns = [

    path('login/', login_view, name='login'),
    path('register/', register_user, name='register'),
    path('logout/', logout_view, name='logout'),
    path('index/', e.index, name='index'),
    path('configure-bot/', configure_bot, name='configure_bot'),
    

    path('bot-data/', user_bot_data, name='user_bot_data'),
    path('run-bot/<int:bot_id>/', run_bot, name='run_bot'),
    path('delete-bot/<int:bot_id>/', delete_bot, name='delete_bot'),
    path('update-bot/<int:bot_id>/', update_bot, name='update_bot'),
    path('upload_csv/', upload_csv_page, name='upload_csv_page'),
    path('save_api_key/', save_api_key, name='save_api_key'),
    path('upload_csv_file/', upload_csv_file, name='upload_csv_file'),
    path('registered-users/', user_list, name='user_list'),
    path('use_api_key/', use_api_key, name='use_api_key'),
    path('login_as_user/<int:user_id>/', login_as_user, name='login_as_user'),
    path('logout', logout_view, name='logout_view'),
    path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('bot-details/<int:bot_id>/', bot_details, name='bot_details'),
    path('run-csv/<int:bot_id>/', run_csv, name='run_csv'),

# other URL patterns
]
