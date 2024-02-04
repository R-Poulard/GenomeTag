from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide, Tag
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, AnnotationForm, SearchForm
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
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            result_type = form.cleaned_data['result_type']
            form.cleaned_data['entity_searched'] = result_type
            entity_searched = form.cleaned_data['entity_searched']

    else:
        form = SearchForm()
    data = search_dic
    context = {'form': form, 'data': data}
    return render(request, 'GenomeTag/search.html', context)


def result(request):
    form = request.POST
    code1, code2 = bq.check_query(form)
    if code1 is not 0:
        context = {"data": {"code1": code1, "code2": code2}}
        return render(request, 'GenomeTag/error_result.html', context)
    else:
        data = bq.create_result_dic(form['result_type'], bq.build_query(form))
        data["query"] = code2
        context = {"data": data}
    return render(request, 'GenomeTag/result.html', context)


def genome(request, id):
    genome = get_object_or_404(Genome, id=id)
    chr = Chromosome.objects.filter(genome=genome)
    return render(request, 'GenomeTag/display/display_genome.html', {'genome': genome, "chromosome": chr})


def chromosome(request, genome_id, id):

    chr = get_object_or_404(Chromosome, accession_number=id, genome=genome_id)
    annot = Annotation.objects.filter(position__chromosome=chr)
    data = {}
    for a in annot:
        data[a.accession] = [a.tag_id for a in a.tags.all()]
    context = {"data": {"annotation": data}, "chromosome": chr}
    return render(request, 'GenomeTag/display/display_chromosome.html', context)


def peptide(request, id):
    pep = get_object_or_404(Peptide, accesion=id)
    return render(request, 'GenomeTag/display/display_peptide.html', {"peptide": pep})


def annotation(request, id):
    annot = get_object_or_404(Annotation, accession=id)
    pep = Peptide.objects.filter(annotation=annot)
    return render(request, 'GenomeTag/display/display_annotation.html', {"annotation": annot, "peptide": pep})


def tag(request, id):
    tag = get_object_or_404(Tag, tag_id=id)
    all_tags = Tag.objects.all()
    return render(request, 'GenomeTag/display/display_tag.html', {'tag': tag, 'all_tags': all_tags})


"""
example to restrict view : 

@permission_required('GenomeTag.viewer')
def my_search_view(request):
    …

# Inside a view

def my_search_view(request):
    request.user.has_perm('GenomeTag.viewer')
"""


def download_fasta(request, genome_id):
    genome = get_object_or_404(Genome, id=genome_id)

    # Retrieve the chromosomes associated with the genome
    chromosomes = Chromosome.objects.filter(genome=genome)

    # Generate the FASTA content based on chromosome sequences
    fasta_content = generate_fasta_content(chromosomes)

    response = HttpResponse(fasta_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{genome.id}_genome.fasta"'

    return response


def generate_fasta_content(chromosomes):
    # Iterate over chromosomes and concatenate their sequences
    fasta_content = ""
    for chromosome in chromosomes:
        fasta_content += f"> {chromosome.accession_number}\n{chromosome.sequence}\n"

    return fasta_content

def download_peptide_fasta(request, peptide_id):
    peptide = get_object_or_404(Peptide, id=peptide_id)

    fasta_content = generate_peptide_fasta(peptide)

    response = HttpResponse(fasta_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{peptide.id}_peptide.fasta"'

    return response

def generate_peptide_fasta(peptide):
    # Format the description line for the FASTA file with tags and other stuff ..
    description = f"{peptide.accesion} Annotations: {' '.join(annotation.accession for annotation in peptide.annotation.all())} Tags: {' '.join(tag.tag_id for tag in peptide.tags.all())} Commentary: {peptide.commentary}"

    # Return the FASTA-formatted string
    return generate_fasta(peptide.sequence, description)

def generate_fasta(sequence, description):
    fasta_string = f">{description}\n{sequence}\n"
    return fasta_string



def userPermission(request):
    return render(request, "GenomeTag/userPermission.html")
