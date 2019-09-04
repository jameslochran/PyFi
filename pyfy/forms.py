from .models import Stock
from django import forms


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = ['ticker', 'count', 'unit_cost', 'acq_date']

    acq_date = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d'),
        input_formats=('%Y-%m-%d', )
        )


class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=255, label='Search for stocks')
