from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy, reverse
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide, Attribution, CustomUser, Tag, Tag, Review, CustomUser
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, AnnotationForm, SearchForm, ReviewForm
from GenomeTag.search_field import search_dic
import GenomeTag.build_query as bq
from django.contrib.auth.decorators import permission_required, login_required
import json

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def main(request):
    return render(request, "GenomeTag/main.html")


def annotations(request):
    if not request.user.has_perm('GenomeTag.view'):
        return redirect(reverse('GenomeTag:userPermission'))
    
    allAnnotations = Annotation.objects.all()
    
    context = {
        'annotations': allAnnotations
    }
    
    return render(request, 'GenomeTag/annotations.html', context)


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


def modify_annotation(request, annotation_id):
    if not request.user.has_perm('GenomeTag.annotate'):
        return redirect(reverse('GenomeTag:userPermission'))
    annotation = get_object_or_404(Annotation, accession=annotation_id)
    message = ""
    if request.method == 'POST':
        form = AnnotationForm(request.POST)
        if form.is_valid() and request.user==annotation.author:
            annotation.commentary=form.cleaned_data['commentary']
            annotation.accession=form.cleaned_data['accesion']
            annotation.tags.clear()
            annotation.peptide_set.clear()
            annotation.save()

            tag_ids = request.POST.getlist('tags')  # Assuming you have a 'tags' field in your form
            for tag_id in tag_ids:
                try:
                    tag=Tag.objects.get(pk=tag_id)
                except Exception:
                    message += "Could not add "+tag_id+"\n"
                    continue
                annotation.tags.add(tag)  # Associate the tag with the annotation
            
            pep_ids = request.POST.getlist('peptide')  # Assuming you have a 'tags' field in your form
            for pep in pep_ids:
                try:
                    peptide=Peptide.objects.get(accesion=pep)
                except Exception as e:
                    print(e)
                    message += "Could not add peptide "+pep+" it does not exist \n"
                    continue
                peptide.annotation.add(annotation)
                peptide.save()

            try:
                annotation.save()  # Save the annotation to the database
            except Exception:
                message="Could not save the modification, be sure that the accession remain unique."
        else:
            message = "Couldn't modify the annotation, issue in the form sent to the website"

        context={
            "message":message
        }
        return render(request, 'GenomeTag/create_annotation_result.html', context) # Redirect to a success page after submission
        
    form = AnnotationForm(initial={'attribution':"None",'accesion': annotation.accession,
                                    'commentary': annotation.commentary,
                                    'tags':tuple(annotation.tags.all())})

    return render(request, 'GenomeTag/modify_annotation.html', 
                  {'form': form, 'annotation': annotation, "message":message,
                    "peptide":repr(json.dumps([i["accesion"] for i in annotation.peptide_set.values("accesion")]))})


def delete_annotation(request, annotation_id):
    if not request.user.has_perm('GenomeTag.review'):
        return redirect(reverse('GenomeTag:userPermission'))
    annotation = get_object_or_404(Annotation, id=annotation_id)
    if request.user == annotation.reviewer:
        annotation.delete()
        return redirect('GenomeTag:create')
    else:
        return HttpResponseBadRequest("Annotation does not exist")


def create_annotation(request, attribution_id):
    if not request.user.has_perm('GenomeTag.annotate'):
        return redirect(reverse('GenomeTag:userPermission'))
    message = ""
    if request.method == 'POST':
        form = AnnotationForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            # Create a new instance of Annotation with form data
            attribution = get_object_or_404(Attribution, id=form.cleaned_data['attribution'])
            if request.user!=attribution.annotator:
                message="Only the attributed author can create the annotation"
            else:
                try:
                    annotation = Annotation(accession=form.cleaned_data['accesion'],
                                        author=attribution.annotator,
                                        reviewer=attribution.requester,
                                        commentary=form.cleaned_data['commentary'],
                                        status="u")
                    annotation.save()  # Save the annotation to the database
                except Exception:
                    message= "Could not create annotation, be sure that the accession number is unique"
                    context={
                        "message":message
                    }
                    return render(request, 'GenomeTag/create_annotation_result.html', context) # Redirect to a success page after submission
                annotation.position.add(*list(attribution.possition.all()))
                # Process tags
                tag_ids = request.POST.getlist('tags')  # Assuming you have a 'tags' field in your form
                for tag_id in tag_ids:
                    try:
                        tag=Tag.objects.get(pk=tag_id)
                    except Exception:
                        message += "Could not add "+tag_id+"\n"
                        continue
                    annotation.tags.add(tag)  # Associate the tag with the annotation
                
                pep_ids = request.POST.getlist('peptide')  # Assuming you have a 'tags' field in your form
                for pep in pep_ids:
                    try:
                        peptide=Peptide.objects.get(accesion=pep)
                    except Exception:
                        message += "Could not add peptide "+pep+" it does not exist\n"
                        continue
                    peptide.annotation.add(annotation)
                    peptide.save()

                annotation.save()  # Save the annotation to the database
                attribution.delete()
        else:
            message = "Couldn't create the annotation, issue in the form sent to the website"

        context={
            "message":message
        }
        return render(request, 'GenomeTag/create_annotation_result.html', context) # Redirect to a success page after submission
        
    attribution = get_object_or_404(Attribution, id=attribution_id)  

    form = AnnotationForm(initial={'attribution':attribution_id})
        
    context = {
        'attribution': attribution,
        'form': form,
        'message': message
    }
    return render(request, 'GenomeTag/create_annotation.html', context)

def search(request):
    if not request.user.has_perm('GenomeTag.view'):
        return redirect(reverse('GenomeTag:userPermission'))
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
    if not request.user.has_perm('GenomeTag.view'):
        return redirect(reverse('GenomeTag:userPermission'))
    form = request.POST
    code1, code2 = bq.check_query(form)
    if code1 != 0:
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


def review_add(request, id):
    if request.method == "POST":
        if not request.user.has_perm('GenomeTag.review'):
            return redirect(reverse('GenomeTag:userPermission'))
        form = ReviewForm(request.POST)
        if form.is_valid():
            annot = get_object_or_404(Annotation, accession=form.cleaned_data['Annotation'])
            reviewer = get_object_or_404(CustomUser, username=form.cleaned_data['Author'])
            commentary = form.cleaned_data['Commentary']
            status = form.cleaned_data['Status']
            if annot.status != 'u' or annot.accession != id or reviewer != request.user:
                render(request, "GenomeTag/error_review.html", {})
            else:
                rev = Review(annotation=annot, author=reviewer, commentary=commentary)
                if status == 'validated':
                    annot.status = 'v'
                    annot.save()
                elif status == 'refused':
                    annot.status = 'r'
                    annot.save()
                rev.save()
                # send_mail(subject='review made',message="This review has been made",recipient_list=['remipoul@gmail.com'],fail_silently=False,from_email=settings.DEFAULT_FROM_EMAIL)
                # print("Review",rev,"annot",annot)
    annot = get_object_or_404(Annotation, accession=id)
    review = Review.objects.filter(annotation=annot).order_by('posted_date')
    context = {"annotation": annot, "review": review}
    if annot.status != "u" and request.user.has_perm('GenomeTag.review'):
        return render(request, 'GenomeTag/review_view.html', context)
    else:
        form = ReviewForm(initial={'Author': str(request.user.username),
                          'Commentary': "", "Annotation": id})
        context["form"] = form
    return render(request, 'GenomeTag/review_submission.html', context)


"""
example to restrict view : 

@permission_required('GenomeTag.view')
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
