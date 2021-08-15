from django import forms
from ckeditor.widgets import CKEditorWidget
from app.models import Trader


class TermsTextForm(forms.ModelForm):
    terms = forms.CharField(widget=CKEditorWidget(), label='')

    def __init__(self, terms_text):
        super().__init__()
        # if user_terms is not None:
        self.fields['terms'].initial = terms_text

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = Trader
        fields = ['terms']
