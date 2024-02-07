from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genome, Annotation, Tag, Chromosome
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
    
class AnnotationForm(forms.ModelForm):
    class Meta:
        model = Annotation
        fields = ['accession', 'tags', 'commentary']
        widgets = {
            'tags': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the rendering of the tags field
        self.fields['tags'].queryset = Tag.objects.all()
        self.fields['tags'].label = 'Tags'
        self.fields['tags'].required = False
        self.fields['tags'].widget.choices = [(tag.tag_id, tag.text) for tag in Tag.objects.all()]

class PeptideForm(forms.Form):
    include_annotation = forms.BooleanField(initial=True, required=False, label='Include Annotations')
    include_tags = forms.BooleanField(initial=True, required=False, label='Include Tags')
    include_commentary = forms.BooleanField(initial=True, required=False, label='Include Commentary')

class ChromosomeDescrForm(forms.Form):
    include_accession_number = forms.BooleanField(initial=True, required=False, label='Include Accession Number')
    include_genome = forms.BooleanField(initial=True, required=False, label='Include Genome')
    include_sequence = forms.BooleanField(initial=True, required=False, label='Include Sequence')
    include_start = forms.BooleanField(initial=True, required=False, label='Include Start')
    include_end = forms.BooleanField(initial=True, required=False, label='Include End')



class AttributionForm(forms.Form):
    
    Creator = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    Annotator = forms.EmailField(widget=forms.TextInput)
    Chromosome = forms.ChoiceField(choices=[])
    Strand = forms.ChoiceField(choices=[("+","+"),("-","-")])
    Start = forms.IntegerField()
    End = forms.IntegerField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Chromosome'].label = 'Chromosome'
        self.fields['Chromosome'].required = True
        choices=[]
        for g in Genome.objects.all():
            acc=g.id
            for chr in Chromosome.objects.filter(genome=g):
                choices.append((acc+"\t"+chr.accession_number,acc+";"+chr.accession_number))
        self.fields['Chromosome'].choices = choices

class FileAttributionForm(forms.Form):
    Creator = forms.CharField(max_length=254,widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    File= forms.FileField()
