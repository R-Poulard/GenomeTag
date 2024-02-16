from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Genome, Tag, Chromosome, Position, RoleChangeRequest
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role", "phone", "affiliation")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = False
        self.fields["affiliation"].required = False


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class ChangeForm(forms.Form):
    username = forms.CharField(required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    role = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    phone = PhoneNumberField(required=False)
    affiliation = forms.CharField(required=False)
    new_password = forms.CharField(required=False, widget=forms.PasswordInput())
    confirmation_new_password = forms.CharField(required=False, widget=forms.PasswordInput())


class SearchForm(forms.Form):
    result_type_choices = [
        ("Genome", "Genome"),
        ("Chromosome", "Chromosome"),
        ("Peptide", "Peptide"),
        ("Annotation", "Annotation"),
    ]

    result_type = forms.ChoiceField(choices=result_type_choices, label="")

    class Media:
        js = ("../projet_web/static/GenomeTag/search_form.js",)


class ReviewForm(forms.Form):
    Annotation = forms.CharField(widget=forms.HiddenInput(attrs={"readonly": "readonly"}))
    result_type_choices = [
        ("refused", "refused"),
        ("validated", "validated"),
    ]
    Status = forms.ChoiceField(choices=result_type_choices)
    Author = forms.CharField(widget=forms.TextInput(attrs={"readonly": "readonly"}))
    Commentary = forms.CharField(widget=forms.Textarea())


class AnnotationForm(forms.Form):
    accesion = forms.CharField()
    commentary = forms.CharField(widget=forms.Textarea())
    attribution = forms.CharField(widget=forms.HiddenInput(attrs={"readonly": "readonly"}))
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the rendering of the tags field
        self.fields["tags"].queryset = Tag.objects.all()
        self.fields["tags"].label = "Tags"
        self.fields["tags"].required = False
        self.fields["tags"].widget.choices = [(tag.tag_id, tag.tag_id) for tag in Tag.objects.all()]


def validate_amino_acid_sequence(value):
    """
    Validator function to ensure that the sequence contains only valid amino acid characters.
    """
    valid_characters = set("ACDEFGHIKLMNPQRSTVWY")
    if any(char not in valid_characters for char in value):
        raise ValidationError("Invalid amino acid sequence: Only valid amino acid characters are allowed.")
    pass


class createPeptideForm(forms.Form):
    accesion = forms.CharField()
    sequence = forms.CharField(widget=forms.Textarea, validators=[validate_amino_acid_sequence])
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple(), required=False)
    commentary = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the rendering of the tags field
        self.fields["tags"].queryset = Tag.objects.all()
        self.fields["tags"].label = "Tags"
        self.fields["tags"].required = False
        self.fields["tags"].widget.choices = [(tag.tag_id, tag.tag_id) for tag in Tag.objects.all()]


class PeptideForm(forms.Form):
    include_annotation = forms.BooleanField(initial=True, required=False, label="Include Annotations")
    include_tags = forms.BooleanField(initial=True, required=False, label="Include Tags")
    include_commentary = forms.BooleanField(initial=True, required=False, label="Include Commentary")


class ChromosomeDescrForm(forms.Form):
    include_accession_number = forms.BooleanField(initial=True, required=False, label="Include Accession Number")
    include_genome = forms.BooleanField(initial=True, required=False, label="Include Genome")
    include_sequence = forms.BooleanField(initial=True, required=False, label="Include Sequence")
    include_start = forms.BooleanField(initial=True, required=False, label="Include Start")
    include_end = forms.BooleanField(initial=True, required=False, label="Include End")


class AnnotationDescrForm(forms.Form):
    include_status = forms.BooleanField(initial=True, required=False, label="Include Status")
    include_genome = forms.BooleanField(initial=True, required=False, label="Include Genome")
    include_chromosome = forms.BooleanField(initial=True, required=False, label="Include Chromosome")
    include_sequence = forms.BooleanField(initial=True, required=False, label="Include Sequence")
    include_start = forms.BooleanField(initial=True, required=False, label="Include Start")
    include_end = forms.BooleanField(initial=True, required=False, label="Include End")
    include_start_relative = forms.BooleanField(initial=True, required=False, label="Include Start")
    include_end_relative = forms.BooleanField(initial=True, required=False, label="Include End")


class AttributionForm(forms.Form):
    Creator = forms.CharField(max_length=254, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    Annotator = forms.EmailField(widget=forms.TextInput)
    Chromosome = forms.ChoiceField(choices=[])
    Strand = forms.ChoiceField(choices=[("+", "+"), ("-", "-")])
    Start = forms.IntegerField()
    End = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["Chromosome"].label = "Chromosome"
        self.fields["Chromosome"].required = True
        choices = []
        for g in Genome.objects.filter(annotable=True):
            acc = g.id
            for chr in Chromosome.objects.filter(genome=g):
                choices.append((acc + "\t" + chr.accession_number, acc + ";" + chr.accession_number))
        self.fields["Chromosome"].choices = choices


class FileAttributionForm(forms.Form):
    Creator = forms.CharField(max_length=254, widget=forms.TextInput(attrs={"readonly": "readonly"}))
    File = forms.FileField()


class PositionSelectionForm(forms.Form):
    position = forms.ModelChoiceField(queryset=Position.objects.all(), empty_label=None)


class BacteriaForm(forms.Form):
    bacteria_choices = [
        ("escherichia_coli", "Escherichia coli"),
        ("staphylococcus_aureus", "Staphylococcus aureus"),
        ("mycobacterium_tuberculosis", "Mycobacterium tuberculosis"),
    ]
    bacteria = forms.ChoiceField(choices=bacteria_choices, label="Select Bacteria")
    database_choices = [
        ("ncbi", "NCBI Genome"),
        ("patric", "PATRIC"),
        ("bac", "Bac Dive"),
    ]
    database = forms.ChoiceField(choices=database_choices, label="Select Database")


class RoleChangeRequestForm(forms.ModelForm):
    class Meta:
        model = RoleChangeRequest
        fields = ["new_role", "reason"]
        widgets = {"new_role": forms.Select(choices=CustomUser.role_choices)}


class ComposeForm(forms.Form):
    recipient = forms.EmailField(label="Recipient")
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


class TopicForm(forms.Form):
    Name = forms.CharField(max_length=30, required=True)


class MessageForm(forms.Form):
    Message = forms.CharField(max_length=254, widget=forms.Textarea, required=True)


class addfileForm(forms.Form):
    genome_file = forms.FileField(required=True)
    cds_file = forms.FileField(required=False)
    peptide_file = forms.FileField(required=False)
