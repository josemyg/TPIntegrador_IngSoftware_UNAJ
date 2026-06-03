from django.apps import AppConfig


class ReservasConfig(AppConfig): 
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas' # nombre de la aplicación, se usa para referenciarla en otros lugares del proyecto, como en las URLs o en los modelos.
