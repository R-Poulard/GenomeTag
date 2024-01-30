from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Annotation, Tag
from django import forms


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

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

