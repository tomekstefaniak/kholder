from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError


class LocalAdminConfig(AppConfig):
    name = "local_admin"
