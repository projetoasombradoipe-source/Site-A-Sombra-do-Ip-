from django.apps import AppConfig


class IpeRoxoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ipe_roxo'


class IpeRoxoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ipe_roxo'

    def ready(self):
        import ipe_roxo.signals