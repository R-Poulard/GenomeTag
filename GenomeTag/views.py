from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse_lazy, reverse
from GenomeTag.models import (
    Genome,
    Chromosome,
    Position,
    Annotation,
    Peptide,
    Tag,
    Review,
    CustomUser,
)
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, AnnotationForm, SearchForm, ReviewForm, PeptideForm,ChromosomeDescrForm
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
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            result_type = form.cleaned_data["result_type"]
            form.cleaned_data["entity_searched"] = result_type
            entity_searched = form.cleaned_data["entity_searched"]

    else:
        form = SearchForm()
    data = search_dic
    context = {"form": form, "data": data}
    return render(request, "GenomeTag/search.html", context)


def result(request):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    form = request.POST
    code1, code2 = bq.check_query(form)
    if code1 != 0:
        context = {"data": {"code1": code1, "code2": code2}}
        return render(request, "GenomeTag/error_result.html", context)
    else:
        data = bq.create_result_dic(form["result_type"], bq.build_query(form))
        data["query"] = code2
        context = {"data": data}
    return render(request, "GenomeTag/result.html", context)


def genome(request, id):
    genome = get_object_or_404(Genome, id=id)
    chr = Chromosome.objects.filter(genome=genome)
    return render(
        request, "GenomeTag/display/display_genome.html", {"genome": genome, "chromosome": chr}
    )


def chromosome(request, genome_id, id):
    chr = get_object_or_404(Chromosome, accession_number=id, genome=genome_id)
    annot = Annotation.objects.filter(position__chromosome=chr)
    data = {}
    for a in annot:
        data[a.accession] = [a.tag_id for a in a.tags.all()]
    context = {"data": {"annotation": data}, "chromosome": chr}
    return render(request, "GenomeTag/display/display_chromosome.html", context)


def peptide(request, id):
    pep = get_object_or_404(Peptide, accesion=id)
    return render(request, "GenomeTag/display/display_peptide.html", {"peptide": pep})


def annotation(request, id):
    annot = get_object_or_404(Annotation, accession=id)
    pep = Peptide.objects.filter(annotation=annot)
    return render(
        request, "GenomeTag/display/display_annotation.html", {"annotation": annot, "peptide": pep}
    )


def tag(request, id):
    tag = get_object_or_404(Tag, tag_id=id)
    all_tags = Tag.objects.all()
    return render(request, "GenomeTag/display/display_tag.html", {"tag": tag, "all_tags": all_tags})


def review_add(request, id):
    if request.method == "POST":
        if not request.user.has_perm("GenomeTag.review"):
            return redirect(reverse("GenomeTag:userPermission"))
        form = ReviewForm(request.POST)
        if form.is_valid():
            annot = get_object_or_404(Annotation, accession=form.cleaned_data["Annotation"])
            reviewer = get_object_or_404(CustomUser, username=form.cleaned_data["Author"])
            commentary = form.cleaned_data["Commentary"]
            status = form.cleaned_data["Status"]
            if annot.status != "u" or annot.accession != id or reviewer != request.user:
                render(request, "GenomeTag/error_review.html", {})
            else:
                rev = Review(annotation=annot, author=reviewer, commentary=commentary)
                if status == "validated":
                    annot.status = "v"
                    annot.save()
                elif status == "refused":
                    annot.status = "r"
                    annot.save()
                rev.save()
                # send_mail(subject='review made',message="This review has been made",recipient_list=['remipoul@gmail.com'],fail_silently=False,from_email=settings.DEFAULT_FROM_EMAIL)
                # print("Review",rev,"annot",annot)
    annot = get_object_or_404(Annotation, accession=id)
    review = Review.objects.filter(annotation=annot).order_by("posted_date")
    context = {"annotation": annot, "review": review}
    if annot.status != "u" and request.user.has_perm("GenomeTag.review"):
        return render(request, "GenomeTag/review_view.html", context)
    else:
        form = ReviewForm(
            initial={"Author": str(request.user.username), "Commentary": "", "Annotation": id}
        )
        context["form"] = form
    return render(request, "GenomeTag/review_submission.html", context)


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
    chromosomes = Chromosome.objects.filter(genome=genome)

    if request.method == 'POST':
        form = ChromosomeDescrForm(request.POST)
        if form.is_valid():
            include_accession_number = form.cleaned_data.get('include_accession_number')
            include_genome = form.cleaned_data.get('include_genome')
            include_sequence = form.cleaned_data.get('include_sequence')
            include_start = form.cleaned_data.get('include_start')
            include_end = form.cleaned_data.get('include_end')

            fasta_content = generate_fasta_content(chromosomes, include_accession_number, include_genome, include_sequence, include_start, include_end)

            response = HttpResponse(fasta_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{genome.id}_genome.fasta"'
            return response
    else:
        form = ChromosomeDescrForm()

    return render(request, 'GenomeTag/display/display_chromosome.html', {'genome': genome, 'form': form})


def generate_fasta_content(chromosomes, include_accession_number=True, include_genome=True, include_sequence=True, include_start=True, include_end=True):
    fasta_content = ""
    for chromosome in chromosomes:
        header = f">{chromosome.accession_number}"
        if include_genome:
            header += f";Genome: {chromosome.genome}"
        if include_accession_number:
            header += f";Accession Number: {chromosome.accession_number}"
        if include_sequence:
            header += f";Sequence: {chromosome.sequence}"
        if include_start:
            header += f";Start: {chromosome.start}"
        if include_end:
            header += f";End: {chromosome.end}"

        fasta_content += f"{header}\n{chromosome.sequence}\n"

    return fasta_content


def download_peptide_fasta(request, peptide_id):
    peptide = get_object_or_404(Peptide, id=peptide_id)

    # Check if the form is submitted
    if request.method == 'POST':
        form = PeptideForm(request.POST)
        if form.is_valid():
            include_annotation = form.cleaned_data.get('include_annotation')
            include_tags = form.cleaned_data.get('include_tags')
            include_commentary = form.cleaned_data.get('include_commentary')

            fasta_content = generate_peptide_fasta(peptide, include_annotation, include_tags, include_commentary)

            response = HttpResponse(fasta_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{peptide.id}_peptide.fasta"'
            return response
    else:
        form = PeptideForm()

    return render(request, 'GenomeTag/display/display_peptide.html', {'peptide': peptide, 'form': form})


def generate_peptide_fasta(peptide, include_annotation=True, include_tags=True, include_commentary=True):
    annotation_info = ' '.join(annotation.accession for annotation in peptide.annotation.all()) if include_annotation else ''
    tags_info = ' '.join(tag.tag_id for tag in peptide.tags.all()) if include_tags else ''
    commentary_info = peptide.commentary if include_commentary else ''

    description = f"{peptide.accesion}"
    if include_annotation and annotation_info:
        description += f";Annotations: {annotation_info}"
    if include_tags and tags_info:
        description += f";Tags: {tags_info}"
    if include_commentary and commentary_info:
        description += f";Commentary: {commentary_info}"
    return generate_fasta(peptide.sequence, description)


def generate_fasta(sequence, description):
    fasta_string = f">{description}\n{sequence}\n"
    return fasta_string


def userPermission(request):
    return render(request, "GenomeTag/userPermission.html")


def blast(request):
    type = request.GET.get("type")
    id = request.GET.get(f"{type}_id")
    if type == "annotation":
        annot = get_object_or_404(Annotation, id=id)
    return render(request, "GenomeTag/blast.html", {"id": id, "type": type, "annot": annot})
