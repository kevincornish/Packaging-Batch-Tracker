from django import forms
from django.forms import inlineformset_factory
from .models import Batch, TargetDate, Bay, Product
from django.forms.widgets import DateInput

class TargetDateForm(forms.ModelForm):
    class Meta:
        model = TargetDate
        fields = ['bay', 'target_start_date', 'target_end_date']
        widgets = {
            'target_start_date': DateInput(attrs={'type': 'date'}),
            'target_end_date': DateInput(attrs={'type': 'date'}),
        }

BatchFormSet = inlineformset_factory(Batch, TargetDate, form=TargetDateForm, extra=1)

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['batch_number', 'product_code', 'complete_date_target', 'comments', 'bom_received', 'batch_complete']
        widgets = {
            'complete_date_target': DateInput(attrs={'type': 'date'}),
        }

    target_dates = BatchFormSet()

class BayForm(forms.ModelForm):
    class Meta:
        model = Bay
        fields = ['name']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_code', 'product', 'presentation']