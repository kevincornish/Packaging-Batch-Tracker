from django.db import models

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
    batch_complete = models.BooleanField()

    def __str__(self):
        return f"{self.batch_number} - {self.product_code}"

class Bay(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class TargetDate(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)
    target_start_date = models.DateField()
    target_end_date = models.DateField()

    def __str__(self):
        return f"{self.batch} - {self.bay} - {self.target_start_date} to {self.target_end_date}"