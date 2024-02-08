from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genome, Annotation, Tag
from django import forms

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

        
class SearchForm(forms.Form): 
    result_type_choices = [
        ('Genome', 'Genome'),
        ('Chromosome', 'Chromosome'),
        ('Peptide', 'Peptide'),
        ('Annotation', 'Annotation'),
    ]

    result_type = forms.ChoiceField(choices=result_type_choices, label='')

    class Media:
        js = ('../projet_web/static/GenomeTag/search_form.js', )


class ReviewForm(forms.Form):
    Annotation = forms.CharField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))
    result_type_choices = [
        ('refused', 'refused'),
        ('validated', 'validated'),
    ]
    Status = forms.ChoiceField(choices=result_type_choices)
    Author = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    Commentary = forms.CharField(widget=forms.Textarea())    


class AnnotationForm(forms.Form):

    accesion = forms.CharField()
    commentary = forms.CharField(widget=forms.Textarea())
    attribution = forms.CharField(widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),widget=forms.CheckboxSelectMultiple(), required=False)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the rendering of the tags field
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].label = 'Tags'
        self.fields['tags'].required = False
        self.fields['tags'].widget.choices = [(tag.tag_id, tag.text) for tag in Tag.objects.all()]