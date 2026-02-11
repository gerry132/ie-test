from django.apps import AppConfig


class IrelandieInteractiveTablesConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irelandie_interactive_tables'

    def ready(self):
        from .interactive_tables import register_interactive_table_schemas
        register_interactive_table_schemas()
