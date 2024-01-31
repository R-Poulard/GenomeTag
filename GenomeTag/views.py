from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, AnnotationForm
from GenomeTag.search_field import search_dic
import GenomeTag.build_query as bq
# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def main(request):
    return render(request, 'GenomeTag/main.html')


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

    data = search_dic
    context = {"data": data}
    return render(request, 'GenomeTag/search.html', context)


def result(request):
    form = request.POST
    code1,code2 = bq.check_query(form)
    if code1 is not 0:
        context = {"data":{"code1": code1,"code2":code2}}
        return render(request,'GenomeTag/error_result.html',context)
    else:
        data = bq.create_result_dic(form['result'],bq.build_query(form))
        data["query"] = code2
        context = {"data": data}    
    return render(request, 'GenomeTag/result.html', context)


def genome(request, id):
    genome = get_object_or_404(Genome, id=id)
    chr=Chromosome.objects.filter(genome=genome)
    return render(request, 'GenomeTag/display/display_genome.html', {'genome': genome,"chromosome":chr})


def chromosome(request, genome_id, id):

    chr=get_object_or_404(Chromosome, accession_number=id, genome=genome_id)
    return render(request, 'GenomeTag/display/display_chromosome.html', {"chromosome":chr,"annotation":[]})


def peptide(request, id):
    pep=get_object_or_404(Peptide, accesion=id)
    return render(request, 'GenomeTag/display/display_peptide.html', {"peptide":pep})


def annotation(request, id):
    annot=get_object_or_404(Annotation, accession=id)
    return render(request, 'GenomeTag/display/display_annotation.html', {"annotation":annot})

"""
example to restrict view : 

@permission_required('GenomeTag.viewer')
def my_search_view(request):
    …

# Inside a view

def my_search_view(request):
    request.user.has_perm('GenomeTag.viewer')
"""


def userPermission(request):
    return render(request, "GenomeTag/userPermission.html")
