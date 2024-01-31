from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords


class Product(models.Model):
    product_code = models.CharField(max_length=255, unique=True)
    product = models.CharField(max_length=255)
    presentation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_code.strip()}"


class Batch(models.Model):
    batch_number = models.CharField(max_length=255, unique=True)
    product_code = models.ForeignKey(Product, on_delete=models.CASCADE)
    manufacture_date = models.DateField()
    complete_date_target = models.DateField()
    on_hold = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    bom_received = models.BooleanField()
    samples_received = models.BooleanField()
    batch_complete = models.BooleanField()
    batch_complete_date = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="completed_batches",
    )
    production_check = models.BooleanField()
    production_check_date = models.DateTimeField(null=True, blank=True)
    production_checked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="production_checked_batches",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_to",
        verbose_name="Assigned To",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_batches",
    )
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="modified_batches",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if not self.id:
            if hasattr(self, "user") and self.user.is_authenticated:
                self.created_by = self.user


        if hasattr(self, "user") and self.user.is_authenticated:
            self.last_modified_by = self.user

            if self.production_check and not self.production_check_date:
                self.production_check_date = timezone.now()
                self.production_checked_by = self.user
            elif not self.production_check:
                self.production_check_date = None
                self.production_checked_by = None

            if self.batch_complete and not self.batch_complete_date:
                self.batch_complete_date = timezone.now()
                self.completed_by = self.user
            elif not self.batch_complete:
                self.batch_complete_date = None
                self.completed_by = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch_number} - {self.product_code}"


class Comment(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


class Bay(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class TargetDate(models.Model):
    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="targetdate"
    )
    bay = models.ForeignKey(Bay, on_delete=models.CASCADE)
    target_start_date = models.DateField()
    target_end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.batch} - {self.bay} - {self.target_start_date} to {self.target_end_date}"
