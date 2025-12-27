from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator


class Key(models.Model):
    label = models.CharField(unique=True, max_length=128)
    encrypted_key = models.BinaryField(validators=[MinLengthValidator(1), MaxLengthValidator(8192)])
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
