from django.db.models import TextChoices


class RoleType(TextChoices):
    MODERATOR = 'MODERATOR', 'Модератор'
    MANAGER = 'MANAGER', 'Менеджер'
    DIRECTOR = 'DIRECTOR', 'Директор'
    CLIENT = 'CLIENT', 'Клиент'
    ADMIN = 'ADMIN', 'Админ'


class ClientManagerRoleType(TextChoices):
    CLIENT = 'CLIENT', 'Клиент'
    MANAGER = 'MANAGER', 'Менеджер'
