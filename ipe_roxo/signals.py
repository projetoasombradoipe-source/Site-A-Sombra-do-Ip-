from django.contrib.auth import get_user_model
import os
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def criar_admin(sender, **kwargs):
    if os.environ.get("CRIAR_ADMIN") == "True":
        User = get_user_model()

        username = "admini"
        email = "adminis@email.com"
        password = "123Adm@"

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.is_staff = True
            user.is_superuser = True

            # se tiver campo tipo
            if hasattr(user, 'tipo'):
                user.tipo = 'ADMIN'

            user.save()

            print("ADMIN CRIADO COM SUCESSO")