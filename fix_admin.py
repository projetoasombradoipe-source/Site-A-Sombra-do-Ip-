from django.contrib.auth import get_user_model
import os

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")

user = User.objects.filter(username=username).first()

if user:
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print("Usuário promovido a admin")
else:
    print("Usuário não encontrado")