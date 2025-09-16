from django.apps import AppConfig
from loguru import logger

from api.models.register import ModelRegister


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = "Main"

    def ready(self):
        ModelRegister.load_all_characters()
        ModelRegister.check_registered()
        logger.success(f'Admin page url: http://127.0.0.1:8000/admin/, admin account: root, Rootpassword')