from django import forms
from django.forms import inlineformset_factory
from .models import Batch, TargetDate, Bay, Product, Comment
from django.forms.widgets import DateInput


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class TargetDateForm(forms.ModelForm):
    class Meta:
        model = TargetDate
        fields = ["bay", "target_start_date", "target_end_date"]
        widgets = {
            "target_start_date": DateInput(attrs={"type": "date"}),
            "target_end_date": DateInput(attrs={"type": "date"}),
        }


BatchFormSet = inlineformset_factory(
    Batch, TargetDate, form=TargetDateForm, extra=1)


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
            "complete_date_target": DateInput(attrs={"type": "date", "class": "py-1 px-2 rounded-2 border text-uppercase"}),
            "manufacture_date": DateInput(attrs={"type": "date", "class": "py-1 px-2 rounded-2 border text-uppercase"}),
            "product_code": forms.Select(attrs={'class': 'form-select'}),
            "batch_number": forms.TextInput(attrs={'class': 'form-control border'}),
            "assigned_to": forms.Select(attrs={'class': 'form-select'}),
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


class BayForm(forms.ModelForm):
    class Meta:
        model = Bay
        fields = ["name"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["product_code", "product", "presentation"]
