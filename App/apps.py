from django.apps import AppConfig


class AppConfigClass(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App'
