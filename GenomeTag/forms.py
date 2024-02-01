from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genome
from django import forms

class MonFormulaire(forms.Form):
    genome = forms.ModelChoiceField(queryset=Genome.objects.all(), empty_label=None, label='Sélectionnez un génome')
    # Ajoutez d'autres champs de formulaire si nécessaire

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")
        
class AnnotationForm(forms.Form):
        genome = forms.ModelChoiceField(queryset=Genome.objects.all(), empty_label=None, label='Sélectionnez un génome')
        
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
 