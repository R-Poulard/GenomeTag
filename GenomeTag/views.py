from django.shortcuts import render
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
    qr=bq.check_query(form)
    if qr is None:
        raise Exception  # TO DO handle exception page
    else:
        data=bq.create_result_dic(form['result'],bq.build_query(form))
        data["query"]=qr
        context = {"data": data}
        
    return render(request, 'GenomeTag/result.html', context)


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
