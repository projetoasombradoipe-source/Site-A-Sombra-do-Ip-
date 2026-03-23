from django.contrib.auth import get_user_model

User = get_user_model()

user = User.objects.get(username="ADMIN")  # coloque seu usuário aqui

user.is_staff = True
user.is_superuser = True
user.tipo = 'ADMIN'  # opcional (se quiser alinhar)

user.save()

print("Usuário promovido a admin")