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
    Attribution,
    CustomUser,
    Tag,
    Review,
    CustomUser,
    Mailbox,
)
from django.views.generic.edit import CreateView
from .forms import (
    CustomUserCreationForm,
    AnnotationForm,
    SearchForm,
    ReviewForm,
    PeptideForm,
    ChromosomeDescrForm,
    AttributionForm,
    FileAttributionForm,
    AnnotationDescrForm,
    createPeptideForm,
    ChangeForm,
    RoleChangeRequestForm,
    ComposeForm,
    PositionSelectionForm,
    BacteriaForm,
)
from GenomeTag.search_field import search_dic
import GenomeTag.build_query as bq
from django.contrib.auth.decorators import permission_required, login_required
from .build_attribution import create_manual_attr, create_file_attr
from django.db.models import Q
import json
from django.views.generic.edit import CreateView
from GenomeTag.search_field import search_dic
import GenomeTag.build_query as bq
from django.contrib.auth.decorators import permission_required, login_required
import xml.etree.ElementTree as ET
from .blast_utils import perform_blast
import os

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def log_info(request):
    if request.user.is_authenticated:
        message = ""
        context = {}
        if request.method == "POST" and "sub1" in request.POST:
            form = ChangeForm(request.POST)
            print(form.errors)
            if form.is_valid():
                print(form.cleaned_data)
                if "username" in form.changed_data:
                    if (
                        form.cleaned_data["username"] != ""
                        or len(form.cleaned_data["username"]) <= 150
                    ) and all(
                        [
                            (i in ["@", "_", "+", "."] or i.isalnum())
                            for i in form.cleaned_data["username"]
                        ]
                    ):
                        print("here")
                        request.user.username = form.cleaned_data["username"]
                    else:
                        message += "Invalide username:\n Required. 150 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters. \n"
                if "phone" in form.changed_data:
                    if form.cleaned_data["phone"].is_valid():
                        request.user.phone = form.cleaned_data["phone"]
                    else:
                        message += "Phone number is not valid (+33 form is requiered)\n"
                elif form.cleaned_data["phone"].strip() == "":
                    request.user.phone = ""
                if "affiliation" in form.changed_data:
                    request.user.affiliation = form.cleaned_data["affiliation"]
                elif form.cleaned_data["affiliation"].strip() == "":
                    request.user.affiliation = ""
                if form.cleaned_data["new_password"] != "":
                    print("changed")
                    if (
                        form.cleaned_data["new_password"]
                        == form.cleaned_data["confirmation_new_password"]
                    ):
                        print("iciii")
                        if len(form.cleaned_data["new_password"]) >= 8 and any(
                            [not i.isdigit() for i in form.cleaned_data["new_password"]]
                        ):
                            print("laaaaa")
                            request.user.set_password(form.cleaned_data["new_password"])
                        else:
                            message += "Invalid password\n"
                    else:
                        message += " The confirmation password must be the same \n"
                request.user.save()
                context["message"] = message
            else:
                context["message"] = "Issue submitting the modifications to the website."
        role = "Annotator"
        if request.user.role == "v":
            role = "Viewer"
        elif request.user.role == "r":
            role = "Reviewer"
        form = ChangeForm(
            initial={
                "username": request.user.username,
                "email": request.user.email,
                "role": role,
                "phone": request.user.phone,
                "affiliation": request.user.affiliation,
            }
        )
        if request.method == "POST" and "sub2" in request.POST:
            form2 = RoleChangeRequestForm(request.POST)
            if form2.is_valid():
                role_change_request = form2.save(commit=False)
                role_change_request.user = request.user
                form2.save()
                return redirect(reverse("GenomeTag:test"))
        else:
            form2 = RoleChangeRequestForm()

        context["form"] = form
        context["form2"] = form2
        return render(request, "GenomeTag/loginfo.html", context)


def role_change_request(request):
    if request.method == "POST" and "sub2" in request.POST:
        form2 = RoleChangeRequestForm(request.POST)
        if form2.is_valid():
            role_change_request = form2.save(commit=False)
            role_change_request.user = request.user
            form2.save()
            return redirect(reverse("GenomeTag:test"))
    else:
        form2 = RoleChangeRequestForm()
    return render(request, "GenomeTag/role_change.html", {"form2": form2})


def main(request):
    context = {}
    if request.user.has_perm("GenomeTag.annotate"):
        annot = Annotation.objects.filter(author=request.user).filter(~Q(status="v"))
        attrib = Attribution.objects.filter(annotator=request.user)
        if annot.exists():
            context["annotation"] = annot
        if attrib.exists():
            context["attribution"] = attrib
    if request.user.has_perm("GenomeTag.review"):
        to_review = Annotation.objects.filter(reviewer=request.user, status="u")
        if to_review.exists():
            context["to_review"] = to_review
    #print(context['to_review'],context['annotation'],context['attribution'])
    return render(request, "GenomeTag/main.html", context)

#MISSING PERMS
def attributions(request):
    print(request.user.role)

    print("ici")
    allAtrributions = Attribution.objects.filter(annotator=request.user)
    print(allAtrributions)
    context = {"attributions": allAtrributions}
    return render(request, "GenomeTag/attributions.html", context)

def annotations(request):
    if not request.user.has_perm("GenomeTag.annotator"):
        return redirect(reverse("GenomeTag:userPermission"))

    allAnnotations = Annotation.objects.filter(author=request.user)
    context = {"annotations": allAnnotations}

    return render(request, "GenomeTag/annotations.html", context)


def create(request):
    if not request.user.has_perm("GenomeTag.annotate"):
        return redirect(reverse("GenomeTag:userPermission"))

    user = request.user

    userAttribution = Attribution.objects.filter(annotator=user)
    attributionIsAnnotatedList = []
    annotationsList = []
    for attribution in userAttribution:
        if Annotation.objects.filter(
            author=attribution.annotator, position=attribution.possition
        ).exists():
            attributionIsAnnotatedList.append(1)
            annotationsList.append(
                Annotation.objects.filter(
                    author=attribution.annotator, position=attribution.possition
                )
            )
        else:
            attributionIsAnnotatedList.append(0)
            annotationsList.append(None)

    context = {
        "attribution_zip": zip(userAttribution, attributionIsAnnotatedList, annotationsList),
    }

    return render(request, "GenomeTag/create.html", context)


def modify_annotation(request, annotation_id):
    if not request.user.has_perm("GenomeTag.annotate"):
        return redirect(reverse("GenomeTag:userPermission"))
    annotation = get_object_or_404(Annotation, accession=annotation_id)
    message = ""
    if request.method == "POST":
        form = AnnotationForm(request.POST)
        if form.is_valid() and request.user == annotation.author:
            annotation.status = "u"
            annotation.commentary = form.cleaned_data["commentary"]
            annotation.accession = form.cleaned_data["accesion"]
            annotation.tags.clear()
            annotation.peptide_set.clear()
            annotation.save()

            tag_ids = request.POST.getlist("tags")  # Assuming you have a 'tags' field in your form
            for tag_id in tag_ids:
                try:
                    tag = Tag.objects.get(pk=tag_id)
                except Exception:
                    message += "Could not add " + tag_id + "\n"
                    continue
                annotation.tags.add(tag)  # Associate the tag with the annotation

            pep_ids = request.POST.getlist(
                "peptide"
            )  # Assuming you have a 'tags' field in your form
            for pep in pep_ids:
                try:
                    peptide = Peptide.objects.get(accesion=pep)
                except Exception as e:
                    print(e)
                    message += "Could not add peptide " + pep + " it does not exist \n"
                    continue
                peptide.annotation.add(annotation)
                peptide.save()

            try:
                annotation.save()  # Save the annotation to the database
            except Exception:
                message = (
                    "Could not save the modification, be sure that the accession remain unique."
                )
        else:
            message = "Couldn't modify the annotation, issue in the form sent to the website"

        context = {"message": message}
        return render(
            request, "GenomeTag/create_annotation_result.html", context
        )  # Redirect to a success page after submission

    form = AnnotationForm(
        initial={
            "attribution": "None",
            "accesion": annotation.accession,
            "commentary": annotation.commentary,
            "tags": tuple(annotation.tags.all()),
        }
    )

    return render(
        request,
        "GenomeTag/modify_annotation.html",
        {
            "form": form,
            "annotation": annotation,
            "message": message,
            "peptide": repr(
                json.dumps([i["accesion"] for i in annotation.peptide_set.values("accesion")])
            ),
        },
    )

    return render(
        request, "GenomeTag/create_annotation.html", {"form": form, "annotation": annotation}
    )

#never used in theory
def delete_annotation(request, attribution_id):
    attribution = get_object_or_404(Attribution, id=attribution_id)

    if Annotation.objects.filter(
        author=attribution.annotator, position=attribution.possition
    ).exists():
        annotation_to_delete = Annotation.objects.filter(
            author=attribution.annotator, position=attribution.possition
        )
        annotation_to_delete.delete()
        return redirect("GenomeTag:create")
    else:
        return HttpResponseBadRequest("Annotation does not exist")


def create_peptide(request):
    if not request.user.has_perm("GenomeTag.review"):
        return redirect(reverse("GenomeTag:userPermission"))

    if request.method == "POST":
        form = createPeptideForm(request.POST)
        if form.is_valid():
            peptide = Peptide(
                accesion=form.cleaned_data["accesion"],
                sequence=form.cleaned_data["sequence"],
                commentary=form.cleaned_data["commentary"],
            )
            peptide.save()
            tag_ids = request.POST.getlist("tags")  # Assuming you have a 'tags' field in your form
            for tag_id in tag_ids:
                try:
                    tag = Tag.objects.get(pk=tag_id)
                except Exception:
                    message += "Could not add " + tag_id + "\n"
                    continue
                peptide.tags.add(tag)  # Associate the tag with the annotation

            peptide.save()
            return redirect("/GenomeTag:create_peptide")
    else:
        form = createPeptideForm()

    context = {"form": form}

    return render(request, "GenomeTag/create_peptide.html", context)


def create_annotation(request, attribution_id):
    if not request.user.has_perm("GenomeTag.annotate"):
        return redirect(reverse("GenomeTag:userPermission"))
    message = ""
    attribution = get_object_or_404(Attribution, id=attribution_id)
    if request.method == "POST":
        form = AnnotationForm(request.POST)
        if form.is_valid():
            # Create a new instance of Annotation with form data
            attribution = get_object_or_404(Attribution, id=form.cleaned_data["attribution"])
            if request.user != attribution.annotator:
                message = "Only the attributed author can create the annotation"
            else:
                try:
                    annotation = Annotation(
                        accession=form.cleaned_data["accesion"],
                        author=attribution.annotator,
                        reviewer=attribution.requester,
                        commentary=form.cleaned_data["commentary"],
                        status="u",
                    )
                    annotation.save()  # Save the annotation to the database
                    #annotator = attribution.annotator

                    #subject = "New Annotation Added"
                    #message = f"Hello {attribution.annotator},\n\nA new annotation has been added for you. Please check it."
                    #sender = request.user.email

                    #Mailbox.objects.create(
                    #    user=annotator, subject=subject, message=message, sender=sender
                    #)
                except Exception:
                    message = (
                        "Could not create annotation, be sure that the accession number is unique"
                    )
                    context = {"message": message}
                    return render(
                        request, "GenomeTag/create_annotation_result.html", context
                    )  # Redirect to a success page after submission
                annotation.position.add(*list(attribution.possition.all()))
                # Process tags
                tag_ids = request.POST.getlist(
                    "tags"
                )  # Assuming you have a 'tags' field in your form
                for tag_id in tag_ids:
                    try:
                        tag = Tag.objects.get(pk=tag_id)
                    except Exception:
                        message += "Could not add " + tag_id + "\n"
                        continue
                    annotation.tags.add(tag)  # Associate the tag with the annotation

                pep_ids = request.POST.getlist(
                    "peptide"
                )  # Assuming you have a 'tags' field in your form
                for pep in pep_ids:
                    try:
                        peptide = Peptide.objects.get(accesion=pep)
                    except Exception:
                        message += "Could not add peptide " + pep + " it does not exist\n"
                        continue
                    peptide.annotation.add(annotation)
                    peptide.save()
                add_tracks(annotation)
                annotation.save()  # Save the annotation to the database
                attribution.delete()

        else:
            message = "Couldn't create the annotation, issue in the form sent to the website"

        context = {"message": message}
        return render(
            request, "GenomeTag/create_annotation_result.html", context
        )  # Redirect to a success page after submission

    attribution = get_object_or_404(Attribution, id=attribution_id)

    form = AnnotationForm(initial={"attribution": attribution_id})

    context = {
        "attribution": attribution,
        "form": form,
    }
    return render(request, "GenomeTag/create_annotation.html", context)


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
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    genome = get_object_or_404(Genome, id=id)
    chr = Chromosome.objects.filter(genome=genome)
    return render(
        request, "GenomeTag/display/display_genome.html", {"genome": genome, "chromosome": chr}
    )


def chromosome(request, genome_id, id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    chr = get_object_or_404(Chromosome, accession_number=id, genome=genome_id)
    annot = Annotation.objects.filter(position__chromosome=chr)
    data = {}
    for a in annot:
        data[a.accession] = [a.tag_id for a in a.tags.all()]
    context = {
        "data": {"annotation": data},
        "chromosome": chr,
        "url_fasta": "/data/" + chr.genome.id + "--" + chr.accession_number + ".fa",
        "url_index": "/data/" + chr.genome.id + "--" + chr.accession_number + ".fai",
        "url_tracks": "/data/" + chr.genome.id + "--" + chr.accession_number + "_tracks.bed",
    }
    return render(request, "GenomeTag/display/display_chromosome.html", context)


def peptide(request, id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    pep = get_object_or_404(Peptide, accesion=id)
    return render(request, "GenomeTag/display/display_peptide.html", {"peptide": pep})


def annotation(request, id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    annot = get_object_or_404(Annotation, accession=id)
    pep = Peptide.objects.filter(annotation=annot)
    return render(
        request, "GenomeTag/display/display_annotation.html", {"annotation": annot, "peptide": pep}
    )


def tag(request, id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
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
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    genome = get_object_or_404(Genome, id=genome_id)
    chromosomes = Chromosome.objects.filter(genome=genome)

    if request.method == "POST":
        form = ChromosomeDescrForm(request.POST)
        if form.is_valid():
            include_accession_number = form.cleaned_data.get("include_accession_number")
            include_genome = form.cleaned_data.get("include_genome")
            include_sequence = form.cleaned_data.get("include_sequence")
            include_start = form.cleaned_data.get("include_start")
            include_end = form.cleaned_data.get("include_end")

            fasta_content = generate_fasta_content(
                chromosomes,
                include_accession_number,
                include_genome,
                include_sequence,
                include_start,
                include_end,
            )

            response = HttpResponse(fasta_content, content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="{genome.id}.fasta"'
            return response
    else:
        form = ChromosomeDescrForm()

    return render(
        request, "GenomeTag/display/display_genome.html", {"genome": genome, "form": form}
    )


def generate_fasta_content(
    chromosomes,
    include_accession_number=True,
    include_genome=True,
    include_sequence=True,
    include_start=True,
    include_end=True,
):
    fasta_content = ""
    for chromosome in chromosomes:
        header = f">{chromosome.accession_number}"
        if include_genome:
            header += f";Genome: {chromosome.genome.id}"
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


def download_fasta_single_chromosome(request, genome_id, chromosome_id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    genome = get_object_or_404(Genome, id=genome_id)
    chromosomes = Chromosome.objects.filter(genome=genome, accession_number=chromosome_id)

    if request.method == "POST":
        form = ChromosomeDescrForm(request.POST)
        if form.is_valid():
            include_accession_number = form.cleaned_data.get("include_accession_number")
            include_genome = form.cleaned_data.get("include_genome")
            include_sequence = form.cleaned_data.get("include_sequence")
            include_start = form.cleaned_data.get("include_start")
            include_end = form.cleaned_data.get("include_end")

            fasta_content = generate_fasta_content(
                chromosomes,
                include_accession_number,
                include_genome,
                include_sequence,
                include_start,
                include_end,
            )

            response = HttpResponse(fasta_content, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{genome.id}-{chromosomes[0].accession_number}.fasta"'
            return response
    else:
        form = ChromosomeDescrForm()

    return chromosome(request, genome_id, chromosome_id)


def download_peptide_fasta(request, peptide_id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    peptide = get_object_or_404(Peptide, id=peptide_id)

    # Check if the form is submitted
    if request.method == "POST":
        form = PeptideForm(request.POST)
        if form.is_valid():
            include_annotation = form.cleaned_data.get("include_annotation")
            include_tags = form.cleaned_data.get("include_tags")
            include_commentary = form.cleaned_data.get("include_commentary")

            fasta_content = generate_peptide_fasta(
                peptide, include_annotation, include_tags, include_commentary
            )

            response = HttpResponse(fasta_content, content_type="text/plain")
            response["Content-Disposition"] = f'attachment; filename="{peptide.id}_peptide.fasta"'
            return response
    else:
        form = PeptideForm()

    return render(
        request, "GenomeTag/display/display_peptide.html", {"peptide": peptide, "form": form}
    )


def generate_peptide_fasta(
    peptide, include_annotation=True, include_tags=True, include_commentary=True
):
    annotation_info = (
        " ".join(annotation.accession for annotation in peptide.annotation.all())
        if include_annotation
        else ""
    )
    tags_info = " ".join(tag.tag_id for tag in peptide.tags.all()) if include_tags else ""
    commentary_info = peptide.commentary if include_commentary else ""

    description = f"{peptide.accesion}"
    if include_annotation and annotation_info:
        description += f";Annotations: {annotation_info}"
    if include_tags and tags_info:
        description += f";Tags: {tags_info}"
    if include_commentary and commentary_info:
        description += f";Commentary: {commentary_info}"
    return generate_fasta(peptide.sequence, description)


def generate_annotation_fasta(
    annotation,
    chr,
    include_genome,
    include_chromosome,
    include_sequence,
    include_start,
    include_end,
    include_end_relative,
    include_start_relative,
    include_status,
):
    accession = f"{annotation.accession}"
    file = ""
    if chr == None:
        pos_list = annotation.position.all()
    else:
        pos_list = annotation.position.filter(chromosome=chr)
    for pos in pos_list:
        line = ">" + accession
        if include_status:
            line += ";Status: " + annotation.status
        if include_genome:
            line += ";Genome: " + pos.chromosome.genome.id
        if include_chromosome:
            line += ";Chromosome: " + pos.chromosome.accession_number
        if include_start:
            line += ";Start: " + str(pos.start)
        if include_end:
            line += ":End: " + str(pos.end)
        if include_start_relative:
            line += ";Start: " + str(pos.start_relative)
        if include_end_relative:
            line += ":End: " + str(pos.end_relative)
        if include_sequence:
            line += ";Sequence:\n" + pos.chromosome.sequence[pos.start - 1 : pos.end - 1]
        line += "\n"
        file += line
    return file


def download_annotation_fasta(request, annotation_id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    annotation = get_object_or_404(Annotation, accession=annotation_id)

    # Check if the form is submitted
    if request.method == "POST":
        form = AnnotationDescrForm(request.POST)
        if form.is_valid():
            include_genome = form.cleaned_data.get("include_genome")
            include_chromosome = form.cleaned_data.get("include_chromosome")
            include_sequence = form.cleaned_data.get("include_sequence")
            include_start = form.cleaned_data.get("include_start")
            include_end = form.cleaned_data.get("include_end")
            include_end_relative = form.cleaned_data.get("include_end_relative")
            include_start_relative = form.cleaned_data.get("include_start_relative")
            include_status = form.cleaned_data.get("include_status")

            fasta_content = generate_annotation_fasta(
                annotation,
                None,
                include_genome,
                include_chromosome,
                include_sequence,
                include_start,
                include_end,
                include_end_relative,
                include_start_relative,
                include_status,
            )

            response = HttpResponse(fasta_content, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{annotation.accession}_annotation.fasta"'
            return response
    else:
        form = PeptideForm()

    return render(
        request,
        "GenomeTag/display/display_annotation.html",
        {"annotation": annotation, "form": form},
    )


def download_all_annotation_fasta(request, genome_id, chromosome_id):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    chromosome = get_object_or_404(Chromosome, genome=genome_id, accession_number=chromosome_id)
    annotation = Annotation.objects.filter(position__chromosome=chromosome)

    # Check if the form is submitted
    if request.method == "POST":
        form = AnnotationDescrForm(request.POST)
        if form.is_valid():
            include_genome = form.cleaned_data.get("include_genome")
            include_chromosome = form.cleaned_data.get("include_chromosome")
            include_sequence = form.cleaned_data.get("include_sequence")
            include_start = form.cleaned_data.get("include_start")
            include_end = form.cleaned_data.get("include_end")
            include_end_relative = form.cleaned_data.get("include_end_relative")
            include_start_relative = form.cleaned_data.get("include_start_relative")
            include_status = form.cleaned_data.get("include_status")

            fasta_content = ""
            for annot in annotation:
                fasta_content += generate_annotation_fasta(
                    annot,
                    chromosome,
                    include_genome,
                    include_chromosome,
                    include_sequence,
                    include_start,
                    include_end,
                    include_end_relative,
                    include_start_relative,
                    include_status,
                )

            response = HttpResponse(fasta_content, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{chromosome.genome.id}-{chromosome.accession_number}_annotation.fasta"'
            return response
    else:
        form = PeptideForm()

    return render(
        request,
        "GenomeTag/display/display_chromosome.html",
        {"annotation": annotation, "form": form},
    )


def generate_fasta(sequence, description):
    fasta_string = f">{description}\n{sequence}\n"
    return fasta_string


def userPermission(request):
    return render(request, "GenomeTag/userPermission.html")


def create_attribution(request):
    err = ""
    if not request.user.has_perm("GenomeTag.review"):
        return redirect(reverse("GenomeTag:userPermission"))
    if request.method == "POST":
        print("HERE")
        if not request.user.has_perm("GenomeTag.review"):
            return redirect(reverse("GenomeTag:userPermission"))
        if "sub1" in request.POST:
            print("THERE")
            form = AttributionForm(request.POST)
            if form.is_valid() and form.cleaned_data["Creator"] == request.user.email:
                print(dict(request.POST))
                err = create_manual_attr(dict(request.POST))
            else:
                err = "Error with the standard field of the form"
        else:
            form = FileAttributionForm(request.POST, request.FILES)
            print(dict(request.POST), request.FILES)
            if form.is_valid():
                err = create_file_attr(form, request.FILES)
            else:
                err = "Error with the file inputed"
    print("START")
    form = AttributionForm(initial={"Creator": request.user.email})

    context = {"form": form, "form2": FileAttributionForm(initial={"Creator": request.user.email})}
    if err != "":
        context["message"] = err
    return render(request, "GenomeTag/create_attribution.html", context)




def add_tracks(annotation):
    for pos in annotation.position.all():
        chr = pos.chromosome.accession_number
        genome = pos.chromosome.genome.id
        line = (
            chr
            + "\t"
            + str(pos.start)
            + "\t"
            + str(pos.end)
            + "\t"
            + annotation.accession
            + "\t0\t"
            + str(pos.start)
            + "\t"
            + str(pos.end)
            + "\n"
        )

        print(os.listdir())
        with open("./projet_web/static/data/" + genome + "--" + chr + "_tracks.bed", "a") as f:
            f.write(line)


def remove_tracks(annotation):
    chr_list = []
    for pos in annotation.position.all():
        chr_list.append(pos.chromosome)
    for chr in chr_list:
        genome = chr.genome.id

        with open("./projet_web/static/data/" + genome + "--" + chr + "_tracks.bed", "r") as f:
            lines = f.readlines()
        with open("./projet_web/static/data/" + genome + "--" + chr + "_tracks.bed", "w") as f:
            for l in lines:
                if annotation.accession_number not in l:
                    f.write(l)


def blast(request):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    type = request.GET.get("type")
    id = request.GET.get(f"{type}_id")
    attribute_dict = {"id": id, "type": type}
    if type == "annotation":
        annotation = get_object_or_404(Annotation, id=id)
        positions = Position.objects.all()
        form = PositionSelectionForm()
        attribute_dict.update({"annotation": annotation, "positions": positions, "form": form})
    if type == "peptide":
        peptide = get_object_or_404(Peptide, id=id)
        sequence = peptide.sequence
        attribute_dict.update({"peptide": peptide})

    if request.method == "POST":
        blast_type = request.POST.get("blast_type")
        database = request.POST.get("database")
        max_hit = request.POST.get("max_hit")
        evalue = request.POST.get("evalue")
        if type == "annotation":
            position_id = request.POST.get("position")
            position = get_object_or_404(Position, id=position_id)
            chromosome_sequence = position.chromosome.sequence
            start = position.start
            end = position.end
            sequence = chromosome_sequence[start - 1 : end]
        result = perform_blast(blast_type, database, sequence, max_hit, evalue)
        return blast_result(request, result=result)

    return render(request, "GenomeTag/blast.html", attribute_dict)


def blast_result(request, result):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    root = ET.fromstring(result)

    blast_program = root.find(".//BlastOutput_program").text
    blast_version = root.find(".//BlastOutput_version").text
    query_id = root.find(".//BlastOutput_query-ID").text
    hits = []

    for hit in root.findall(".//Hit"):
        hit_data = {
            "hit_id": hit.find("Hit_id").text,
            "hit_def": hit.find("Hit_def").text,
            "hit_len": hit.find("Hit_len").text,
            "hit_accession": hit.find("Hit_accession").text,
        }
        hits.append(hit_data)

    context = {
        "blast_program": blast_program,
        "blast_version": blast_version,
        "query_id": query_id,
        "hits": hits,
    }

    return render(request, "GenomeTag/blast_result.html", context)


def alternative_database(request):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    if request.method == "POST":
        form = BacteriaForm(request.POST)
        if form.is_valid():
            bacteria = form.cleaned_data["bacteria"]
            database = form.cleaned_data["database"]
            if bacteria == "escherichia_coli":
                if database == "ncbi":
                    return redirect("https://www.ncbi.nlm.nih.gov/genome/?term=Escherichia%20coli")
                elif database == "patric":
                    return redirect(
                        "https://www.patricbrc.org/view/GenomeList/?tab=databases&search=Escherichia%20coli"
                    )
                elif database == "bac":
                    # Redirect to an alternative database for Escherichia coli
                    return redirect("https://bacdive.dsmz.de/strain/10509")
            elif bacteria == "staphylococcus_aureus":
                if database == "ncbi":
                    return redirect(
                        "https://www.ncbi.nlm.nih.gov/genome/?term=Staphylococcus%20aureus"
                    )
                elif database == "patric":
                    return redirect(
                        "https://www.patricbrc.org/view/GenomeList/?tab=databases&search=Staphylococcus%20aureus"
                    )
                elif database == "bac":
                    # Redirect to an alternative database for Staphylococcus aureus
                    return redirect("https://bacdive.dsmz.de/strain/10124")
            elif bacteria == "mycobacterium_tuberculosis":
                if database == "ncbi":
                    return redirect(
                        "https://www.ncbi.nlm.nih.gov/genome/?term=Mycobacterium%20tuberculosis"
                    )
                elif database == "patric":
                    return redirect(
                        "https://www.patricbrc.org/view/GenomeList/?tab=databases&search=Mycobacterium%20tuberculosis"
                    )
                elif database == "bac":
                    # Redirect to an alternative database for Mycobacterium tuberculosis
                    return redirect("https://bacdive.dsmz.de/strain/13165")
    else:
        form = BacteriaForm()
    return render(request, "GenomeTag/alternative_database.html", {"form": form})


def mailbox(request):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    user_mailbox = Mailbox.objects.filter(user=request.user)
    return render(request, "GenomeTag/mailbox.html", {"user_mailbox": user_mailbox})

    return render(request, "GenomeTag/compose_email.html", {"form": form})


def compose_email(request):
    if not request.user.has_perm("GenomeTag.view"):
        return redirect(reverse("GenomeTag:userPermission"))
    if request.method == "POST":
        form = ComposeForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            sender = request.user.email
            recipient = form.cleaned_data["recipient"]
            Mailbox.objects.create(
                user=request.user, subject=subject, message=message, sender=sender
            )
            return redirect(reverse("GenomeTag:mailbox"))
    else:
        form = ComposeForm()
    return render(request, "GenomeTag/compose_email.html", {"form": form})
