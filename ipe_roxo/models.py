from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import date
from django.db.models import Count

from cloudinary_storage.storage import MediaCloudinaryStorage




class CustomUser(AbstractUser):
    TIPO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('COLAB', 'Colaborador'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='COLAB')
    ativo = models.BooleanField(default=True)
    funcao = models.CharField(max_length=100, blank=True, null=True)  # Novo campo função


    def __str__(self):
        return self.username


#########################################################################################

class PlantaCuidador(models.Model): 
    STATUS_CHOICES = [ ('PENDENTE', 'REVISÃO'), ('APROVADO', 'APROVADO'), ('CORRECAO', 'CORREÇÃO'), ] 
    STATUS_PLANTA_CHOICES = [('VIVA', 'VIVA'),('MORTA', 'MORTA'),('REPLANTADA', 'REPLANTADA'),]
    status = models.CharField( max_length=10, choices=STATUS_CHOICES, default='PENDENTE' ) 
    status_planta = models.CharField(max_length=20,choices=STATUS_PLANTA_CHOICES,default='VIVA')
    admin_responsavel = models.ForeignKey( CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='formularios_revisados' ) 
    motivo_correcao = models.TextField(blank=True, null=True)
    numero_registro = models.CharField(max_length=20,unique=True,null=True,blank=True,editable=False) 
    horario_cadastro = models.DateTimeField(default=timezone.now) # Novo campo 
    colaborador = models.ForeignKey(CustomUser,on_delete=models.SET_NULL,null=True,blank=True,related_name='formularios')
    nome = models.CharField(max_length=100) 
    ativo = models.BooleanField(default=True) 
    telefone = models.CharField(max_length=11) 
    cidade = models.CharField(max_length=100) 
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=100) 
    numero = models.CharField(max_length=20) 
    especie = models.CharField(max_length=100) 
    
    @property
    def idade(self):
        if not self.data:
            return "Não informado"

        hoje = date.today()
        diferenca = hoje - self.data

        dias = diferenca.days

        if dias < 30:
            return f"{dias} dia{'s' if dias > 1 else ''}"

        meses = dias // 30
        if meses < 12:
            return f"{meses} mês{'es' if meses > 1 else ''}"

        anos = meses // 12
        meses_restantes = meses % 12

        if meses_restantes == 0:
            return f"{anos} ano{'s' if anos > 1 else ''}"

        return f"{anos} ano{'s' if anos > 1 else ''} e {meses_restantes} mês{'es' if meses_restantes > 1 else ''}"
    data = models.DateField() 
    foto = models.ImageField(
    upload_to='fotos_plantas/',
    storage=MediaCloudinaryStorage())

    data_envio = models.DateTimeField(auto_now_add=True) 
    observacao_admin = models.TextField(blank=True) 
   
    def save(self, *args, **kwargs):
        if not self.pk and not self.numero_registro:  # Só para novos registros
            self.numero_registro = timezone.now().strftime("IP%Y%m") + str(uuid.uuid4().hex[:6]).upper()
        super().save(*args, **kwargs)  # Agora sempre salva

@receiver(post_save, sender=PlantaCuidador)
def create_historico(sender, instance, created, **kwargs):
    if created:
        PlantaHistorico.objects.create(
            planta=instance,
            usuario_responsavel=instance.colaborador,
            status_planta=instance.status_planta,
            descricao= (
                     f"Primeiro cadastro da planta. Cuidador: {instance.nome}, "
                     f"1º Plantio: {instance.data}, "
                     f"Espécie: {instance.especie}, "
                     f"Bairro: {instance.bairro}, "
                     f"Número de Registro: {instance.numero_registro}"
                     ),
            data_evento=instance.horario_cadastro,
            foto=instance.foto
        )

#################################3##
class PlantaHistorico(models.Model):
    planta = models.ForeignKey("PlantaCuidador", on_delete=models.CASCADE, related_name="historicos")
    foto = models.ImageField(upload_to="plantas/historico/",storage=MediaCloudinaryStorage(),blank=True, null=True)
    data_evento = models.DateTimeField(auto_now_add=True)
    descricao = models.TextField(blank=True, null=True)  # Ex: "Nova foto após 3 meses", "Planta morreu", etc.
    status_planta= models.CharField(
        max_length=20,
        choices=[
            ('VIVA', 'Planta Viva'),
            ('MORTA', 'Planta Morta'),
            ('REPLANTADA', 'Replantada'),
        ],
        default='VIVA'
    )
    usuario_responsavel = models.ForeignKey(
        'CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='historicos_alterados'
    )

    def __str__(self):
        return f"Histórico da {self.planta.id} - {self.data_evento}"
    
#######################################################################
class Relatorio:

    @staticmethod
    def gerar():
        return {
            'por_bairro': PlantaCuidador.objects.values('bairro', 'status_planta')
                .annotate(total=Count('id'))
                .order_by('bairro'),

            'por_status': PlantaCuidador.objects.values('status_planta')
                .annotate(total=Count('id')),

            'usuarios_ativos': PlantaCuidador.objects.values('colaborador__username')
                .annotate(total=Count('id'))
                .order_by('-total')
        }