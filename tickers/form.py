from django import forms

from .models import Ticker, Portfolio, User, UserTicker, Group


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserTickerForm(BaseForm, forms.ModelForm):
    portfolio = forms.ModelChoiceField(queryset=Portfolio.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = UserTicker
        fields = ['ticker', 'portfolio', 'starting_value_of_ticker', 'starting_investment']


class PortFolioForm(BaseForm, forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = Portfolio
        fields = ['is_public', 'title', 'maximum_cash', 'user']


class GroupForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Group
        fields = '__all__'


class TickerForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Ticker
        fields = ['title', 'ticker', 'group']


class TickerRefreshForm(forms.ModelForm):

    class Meta:
         model = Ticker
         fields = '__all__'

