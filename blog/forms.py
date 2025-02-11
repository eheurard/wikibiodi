from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'ISIN_number', 'Ticker', 'sector']

class AssetUploadForm(forms.Form):
    file = forms.FileField(label="Upload an Excel file")
