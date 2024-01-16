from django.utils import timezone
from django.db import models
from auditlog.registry import auditlog
from django.contrib.auth.models import User

class Product(models.Model):
    product_code = models.CharField(max_length=255, unique=True)
    product = models.CharField(max_length=255)
    presentation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_code.strip()}"
    
class Batch(models.Model):
    batch_number = models.CharField(max_length=255, unique=True)
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)    
    complete_date_target = models.DateField()
    comments = models.TextField(blank=True)
    bom_received = models.BooleanField()
    samples_received = models.BooleanField()
    batch_complete = models.BooleanField()
    production_check = models.BooleanField()
    production_check_date = models.DateTimeField(null=True, blank=True)
    production_checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.production_check and not self.production_check_date:
            self.production_check_date = timezone.now()
            if hasattr(self, 'user') and self.user.is_authenticated:
                self.production_checked_by = self.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch_number} - {self.product_code}"

class Bay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class TargetDate(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='targetdate')
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)
    target_start_date = models.DateField()
    target_end_date = models.DateField()

    def __str__(self):
        return f"{self.batch} - {self.bay} - {self.target_start_date} to {self.target_end_date}"
    
auditlog.register(Batch)
auditlog.register(Bay)
auditlog.register(Product)