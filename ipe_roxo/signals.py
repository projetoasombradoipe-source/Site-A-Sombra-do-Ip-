from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()

@receiver(post_migrate)
def criar_admin(sender, **kwargs):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='123456',
            tipo='ADMIN'

        )

