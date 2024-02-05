from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.urls import reverse_lazy, reverse
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide, Attribution, CustomUser, Tag
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, AnnotationForm
from GenomeTag.search_field import search_dic
import GenomeTag.build_query as bq
from django.contrib.auth.decorators import permission_required, login_required


# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def main(request):
    return render(request, "GenomeTag/main.html")


def annotations(request):
    return HttpResponse("Here you will be able to make see annotations")


def create(request):
    if not request.user.has_perm('GenomeTag.annotate'):
        return redirect(reverse('GenomeTag:userPermission'))

    user = request.user

    userAttribution = Attribution.objects.filter(annotator=user)
    attributionIsAnnotatedList = []
    annotationsList = []
    for attribution in userAttribution:
        if Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).exists():
            attributionIsAnnotatedList.append(1)
            annotationsList.append(Annotation.objects.filter(author=attribution.annotator, position=attribution.possition))
        else:
            attributionIsAnnotatedList.append(0)
            annotationsList.append(None)

    
    context = {
        'attribution_zip': zip(userAttribution, attributionIsAnnotatedList, annotationsList),
    }

    return render(request, 'GenomeTag/create.html', context)


def modify_annotation(request, attribution_id):
    attribution = get_object_or_404(Attribution, id=attribution_id)
    if Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).exists():
        annotation = Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).first()
    
    if request.method == 'POST':
        form = AnnotationForm(request.POST, instance=annotation)
        if form.is_valid():
            form.save()
            return redirect('GenomeTag:create')
    else:
        form = AnnotationForm(instance=annotation)

    return render(request, 'GenomeTag/create_annotation.html', {'form': form, 'annotation': annotation})

def delete_annotation(request, attribution_id):
    attribution = get_object_or_404(Attribution, id=attribution_id)

    if Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).exists():
        annotation_to_delete = Annotation.objects.filter(author=attribution.annotator, position=attribution.possition)
        annotation_to_delete.delete()
        return redirect('GenomeTag:create')
    else:
        return HttpResponseBadRequest("Annotation does not exist")

def create_annotation(request, attribution_id):
    if not request.user.has_perm('GenomeTag.annotate'):
        return redirect(reverse('GenomeTag:userPermission'))
    
    attribution = get_object_or_404(Attribution, id=attribution_id)
    
    if Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).exists():
        annotation = Annotation.objects.filter(author=attribution.annotator, position=attribution.possition).first()
    else:
        annotation = Annotation.objects.create(accession='', author=request.user, status='u', commentary='')

    
    if request.method == 'POST':
        form = AnnotationForm(request.POST, instance=annotation)
        if form.is_valid():
            # Create a new instance of Annotation with form data
            annotation = form.save(commit=False)  # Don't save to database yet
            annotation.save()  # Save the annotation to the database
            annotation.author = request.user  # Assign the current user as the author
            annotation.position.set([attribution.possition])
            
            # Process tags
            tag_ids = request.POST.getlist('tags')  # Assuming you have a 'tags' field in your form
            for tag_id in tag_ids:
                tag = get_object_or_404(Tag, pk=tag_id)  # Get the Tag object
                annotation.tags.add(tag)  # Associate the tag with the annotation
            
            annotation.save()  # Save the annotation to the database
            return redirect('GenomeTag:create')  # Redirect to a success page after submission
    else:
        form = AnnotationForm(instance=annotation)
        
    context = {
        'attribution': attribution,
        'form': form,
    }
    return render(request, 'GenomeTag/create_annotation.html', context)

def search(request):
    if not request.user.has_perm('GenomeTag.view'):
        return redirect(reverse('GenomeTag:userPermission'))
    data = search_dic
    context = {"data": data}
    return render(request, "GenomeTag/search.html", context)


def result(request):
    form = request.POST
    data = {}
    if bq.check_query(form) is False:
        raise Exception
    if form["result"] == "Genome":
        data = {"type": "Genome", "id": [], "chrs": []}
        g = bq.build_query(form)
        print(g)
        for genome in g:
            data["id"].append(genome.id)
            chr_g = []
            for chr in Chromosome.objects.filter(genome=genome):
                chr_g.append(chr.accession_number)
            data["chrs"].append(chr_g)
    else:
        # do nothing yet
        data["type"] = form["result"]
    context = {"data": data}
    return render(request, "GenomeTag/result.html", context)

"""
example to restrict view : 

@permission_required('GenomeTag.view')
def my_search_view(request):
    …

# Inside a view

def my_search_view(request):
    request.user.has_perm('GenomeTag.view')
"""


def userPermission(request):
    return render(request, "GenomeTag/userPermission.html")
