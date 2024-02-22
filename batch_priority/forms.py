from django import forms
from django.forms import inlineformset_factory
from django.forms.widgets import DateInput
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from batchtracker import settings
from .models import (
    Batch,
    TargetDate,
    Bay,
    Product,
    Comment,
    DailyDiscussionComment,
    Tray,
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        expected_domain = getattr(settings, "EMAIL_DOMAIN")

        if not email.endswith(f"@{expected_domain}"):
            raise ValidationError(f"Email must end with {expected_domain}")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
        return user


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class TargetDateForm(forms.ModelForm):
    class Meta:
        model = TargetDate
        fields = ["bay", "target_start_date", "target_end_date", "is_active"]
        widgets = {
            "target_start_date": DateInput(attrs={"type": "date"}),
            "target_end_date": DateInput(attrs={"type": "date"}),
        }


BatchFormSet = inlineformset_factory(Batch, TargetDate, form=TargetDateForm, extra=1)


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            "batch_number",
            "product_code",
            "manufacture_date",
            "complete_date_target",
            "on_hold",
            "notes",
            "bom_received",
            "samples_received",
            "batch_complete",
            "production_check",
            "assigned_to",
        ]
        widgets = {
            "complete_date_target": DateInput(
                attrs={
                    "type": "date",
                    "class": "py-1 px-2 rounded-2 border text-uppercase",
                }
            ),
            "manufacture_date": DateInput(
                attrs={
                    "type": "date",
                    "class": "py-1 px-2 rounded-2 border text-uppercase",
                }
            ),
            "product_code": forms.Select(attrs={"class": "form-select"}),
            "batch_number": forms.TextInput(attrs={"class": "form-control border"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
        }

    target_dates = BatchFormSet()

    def save(self, commit=True, created_by=None, *args, **kwargs):
        instance = super().save(commit=False, *args, **kwargs)

        if commit:
            instance.save()

            if created_by and not instance.created_by:
                instance.created_by = created_by
                instance.save()

        return instance


class BatchPartialEditForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = [
            "on_hold",
            "bom_received",
            "samples_received",
            "batch_complete",
        ]


class BayForm(forms.ModelForm):
    class Meta:
        model = Bay
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_code", "product", "presentation", "expected_yield", "tray"]
        widgets = {
            "product_code": forms.TextInput(attrs={"class": "form-control"}),
            "product": forms.TextInput(attrs={"class": "form-control"}),
            "presentation": forms.TextInput(attrs={"class": "form-control"}),
            "expected_yield": forms.TextInput(attrs={"class": "form-control"}),
            "tray": forms.Select(attrs={"class": "form-select"}),
        }


class DailyDiscussionCommentForm(forms.ModelForm):
    class Meta:
        model = DailyDiscussionComment
        fields = ["text"]


class TrayCalculatorForm(forms.Form):
    presentation = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Presentation",
    )
    yield_amount = forms.DecimalField(
        label="Yield", widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["presentation"].choices = self.get_tray_choices()

    def get_tray_choices(self):
        tray_choices = Tray.objects.all().values_list("tray_type", "tray_type")
        return tray_choices
