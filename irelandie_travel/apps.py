from django.apps import AppConfig


class IrelandieTravelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irelandie_travel'

    def ready(self) -> None:
        from .signals import update_translation_status

        signal_list = [update_translation_status]
        print(signal_list)
        return super().ready()
