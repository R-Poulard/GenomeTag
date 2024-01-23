from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide

# Create your views here.


def main(request):
    return render(request, 'GenomeTag/main.html')
    #return HttpResponse("bruh")


def authenticate(request):
    return HttpResponse("Here you will be able to authenticate")


def annotations(request):
    return HttpResponse("Here you will be able to make see annotations")


def create(request):
    return HttpResponse("Here you will be able to create new annotations")


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
