from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, AnnotationForm

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def main(request):
    return render(request, 'GenomeTag/main.html')


def authenticate(request):
    return HttpResponse("Here you will be able to authenticate")


def annotations(request):
    return HttpResponse("Here you will be able to make see annotations")


def create(request):
    form = None
    if request.method == 'POST':
        form = AnnotationForm(request.POST)
    else:
        form = AnnotationForm()

    return render(request, 'GenomeTag/create_annotation_form.html', {'form': form})


def search(request):
    return render(request, 'GenomeTag/search.html')

def result(request):

    form = request.POST
    data = {}
    print("FORM HERE:", form)
    if form['result'] == "Genome":
        data = {"type":"Genome", "id": [], "chrs": []}    
        g=Genome.objects.filter()
        for genome in g:
            data["id"].append(genome.id)
            chr_g = []
            for chr in Chromosome.objects.filter(genome=genome):
                chr_g.append(chr.accession_number)
            data["chrs"].append(chr_g) 
    else:
        # do nothing yet
        data["type"] = form['result']
    context = {"data": data}
    return render(request, 'GenomeTag/result.html', context)

