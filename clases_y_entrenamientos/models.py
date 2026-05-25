from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from gestion.models import Cliente, Profesor
# Create your models here.
