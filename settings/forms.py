from django import forms

from .models import ProfileSetting, UserDateRange, User


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class UserDateRangeForm(BaseForm, forms.ModelForm):
    settings = forms.ModelChoiceField(queryset=ProfileSetting.objects.all(), widget=forms.HiddenInput())
    start = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))
    end = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = UserDateRange
        fields = ['settings', 'is_primary', 'start', 'end']

    def clean(self):
        cleaned_data = super(UserDateRangeForm, self).clean()
        start = cleaned_data.get('start')
        end = cleaned_data.get('end')
        if start and end:
            if end < start:
                return forms.ValidationError('Pick right dates')
        return cleaned_data
