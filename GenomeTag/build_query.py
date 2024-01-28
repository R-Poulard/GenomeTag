from django.db.models import Q, F
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide
from django.db.models import Count
from django.db.models.functions import Length
import re


def check_query(form):
    return "Query not yet implemented"


def find_all_indices_regex(main_string, substring):
    if substring[0] == '*':
        substring = ".{0,200}"+substring[1:]
    pattern = re.compile(substring.replace("*", "{0,200}"))
    return [(match.start(), match.end()) for match in pattern.finditer(main_string)]


def build_query(form):
    form = dict(form)
    res_list = []
    for i in range(len(form['text_field'])):
        dic = {"negation": int(form['negation'][i]), "condition": int(form['condition'][i]), "value": form["text_field"][i]}
        res_list.append(single_query(form['result'][0], dic))
    res = res_list[0]
    if 'connector' in form:
        for i in range(len(form['connector'])):
            if int(form['connector'][i]) == 1:
                res = res.union(res_list[i+1])
            else:
                res = res & res_list[i+1]
    
    return res


def single_query(result, form):
    cls = Genome
    condition = Q()
    if result == "Genome":
        cls = Genome
        condition = ask_genome(form)
    elif result == "Chromosome":
        cls = Chromosome
        condition = ask_chromosome(form)
    elif result == "Peptide":
        cls = Peptide
        condition = ask_peptide(form)
    elif result == "Annotation":
        cls = Annotation
        condition = ask_annotation(form) & Q(status="u")
    if form['negation'] == 1:
        return cls.objects.filter(~condition)
    else:
        return cls.objects.filter(condition)


def ask_genome(form):
    cond = form['condition']
    # ["Access Number","Number Chromosome", "Chromosome accession number", "in DOI", "in Text", "Species"
    if cond == 0:
        return Q(id=form['value'])
    elif cond == 1:
        grouped_data = Chromosome.objects.values('genome').annotate(category_count=Count('genome'))
        if form['value'][0] == ">":
            filtered_data = grouped_data.filter(category_count__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            filtered_data = grouped_data.filter(category_count__lt=int(form['value'][1:]))
        else:
            filtered_data = grouped_data.filter(category_count=int(form['value']))
        id_genome = [item['genome'] for item in filtered_data]
        return Q(id__in=id_genome)
    elif cond == 2:
        chr_data = Chromosome.objects.values(accession_number=form['value'])['genome']
        return Q(id=chr_data)
    elif cond == 3:
        return Q(DOI__contains=form["value"])
    elif cond == 4:
        return Q(commentary__icontains=form["value"])
    elif cond == 5:
        return Q(species=form["value"])
    return Q()


def ask_chromosome(form):
    # ["Access Number", "Start Position", "End Position", "Length", "Genome id", "Sequence", "Species"]
    cond = form['condition']
    if cond == 0:
        return Q(accession_number=form['value'])
    elif cond == 1:
        if form['value'][0] == ">":
            return Q(start__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(start__lt=int(form['value'][1:]))
        else:
            return Q(start=int(form['value']))
    elif cond == 2:
        if form['value'][0] == ">":
            return Q(end__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(end__lt=int(form['value'][1:]))
        else:
            return Q(end=int(form['value']))
    elif cond == 3:
        if form['value'][0] == ">":
            return Q(end__gt=F('start')+int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(end__lt=F('start')+int(form['value'][1:]))
        return Q(end=F('start')+int(form['value']))
    elif cond == 4:
        genome = Genome.objects.filter(id=form['value'])
        return Q(genome__in=genome)
    elif cond == 5:
        substring = form['value']
        if substring[0] == '*':
            substring = ".{0,200}"+substring[1:]
        return Q(sequence__regex=substring.replace('*', "{0,200}"))
    elif cond == 6:
        genome = Genome.objects.filter(species=form['value'])
        return Q(genome__in=genome)
    return Q()


def ask_peptide(form):
    # "Peptide": ["Access Number", "Proteique Sequence", "Size", "Tag id", "Annotation Acess Number","in Text"],
    cond = form['condition']
    if cond == 0:
        return Q(accesion=form['value'])
    elif cond == 1:
        substring = form['value']
        if substring[0] == '*':
            substring = ".{0,200}"+substring[1:]
        return Q(sequence__regex=substring.replace('*', '{0,200}'))
    elif cond == 2:
        grouped_data = Peptide.objects.annotate(length=Length('sequence'))
        if form['value'][0] == ">":
            filtered_data = grouped_data.filter(length__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            filtered_data = grouped_data.filter(length__lt=int(form['value'][1:]))
        else:
            filtered_data = grouped_data.filter(length=int(form['value']))
        id_peptide = [item.accesion for item in filtered_data]
        return Q(accesion__in=id_peptide)
    elif cond == 3:
        return Q(tags__tag_id=form['value'])
    elif cond == 4:
        return Q(annotation__accession=form['value'])
    elif cond == 5:
        return Q(commentary__icontains=form["value"])
    return Q()


def ask_annotation(form):
    # "Annotation": ["Access Number", "Start Position","Start Relative Position", "End Position","End Relative Position","length","sequence", "strand", "Chromosome access number", "Genome access number", "Author id", "Tag id", "Element in text"]
    cond = form['condition']
    if cond == 0:
        return Q(accession=form['value'])
    elif cond == 1:
        if form['value'][0] == ">":
            return Q(position__start__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(position__start__lt=int(form['value'][1:]))
        else:
            return Q(position__start=int(form['value']))
    elif cond == 2:
        if form['value'][0] == ">":
            return Q(position__start_relative__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(position__start_relative__lt=int(form['value'][1:]))
        else:
            return Q(position__start_relative=int(form['value']))
    elif cond == 3:
        if form['value'][0] == ">":
            return Q(position__end__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(position__end__lt=int(form['value'][1:]))
        else:
            return Q(position__end=int(form['value']))
    elif cond == 4:
        if form['value'][0] == ">":
            return Q(position__end_relative__gt=int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(position__end_relative__lt=int(form['value'][1:]))
        else:
            return Q(position__end_relative=int(form['value']))
    elif cond == 5:
        if form['value'][0] == ">":
            return Q(position__end__gt=F('position__start')+int(form['value'][1:]))
        elif form['value'][0] == "<":
            return Q(position__end__lt=F('position__start')+int(form['value'][1:]))
        return Q(position__end=F('position__start')+int(form['value']))
    elif cond == 6:
        chr_list = Chromosome.objects.all()
        pos_list = []
        for chr in chr_list:
            for pos in find_all_indices_regex(chr.sequence, form['value']):
                start, end = pos
                pos_list.extend(list(Position.objects.filter(
                    chromosome=chr, start=start+1, end=end)))
        return Q(position__in=pos_list)
    elif cond == 7:
        return Q(position__strand=form['value'])
    elif cond == 8:
        return Q(position__chromosome__accession_number=form['value'])
    elif cond == 9:
        return Q(position__chromosome__genome=form['value'])
    elif cond == 10:
        return Q(author__username=form['value'])
    elif cond == 11:
        return Q(tags__tag_id=form['value'])
    elif cond == 12:
        return Q(commentary__icontains=form["value"])
    return Q()


def create_result_dic(result, query):
    data={}
    print("query",query)
    if result == "Genome":
        data= {"type": "Genome", "Id":[], "Commentary":[],"Species":[],"#Chromosome":[],"Length":[]}
        for genome in query:
            data["Id"].append(genome.id)
            data["Species"].append(genome.species)
            data["Commentary"].append(genome.commentary.replace('\n',''))
            max_length=0
            tot_chrs=0
            for chr in Chromosome.objects.filter(genome=genome):
                tot_chrs+=1
                max_length=max(max_length,chr.end)
            data["#Chromosome"].append(str(tot_chrs))
            data["Length"].append(str(max_length))
    if result == "Chromosome":
        data= {"type": "Chromosome", "Id":[], "Start":[],"End":[],"Length":[],"Genome id":[],"Species":[]}
        for chr in query:
            data["Id"].append(chr.accession_number)
            data["Start"].append(chr.start)
            data["End"].append(chr.end)
            data["Length"].append(chr.end-chr.start+1)
            data["Genome id"].append(chr.genome.id)
            data["Species"].append(chr.genome.species)
    if result == "Annotation":
        data= {"type": "Annotation", "Accession":[], "Commentary":[], "Tags":[],"#Position":[]}
        for annotation in query:
            data["Accession"].append(annotation.accession)
            data["Commentary"].append(annotation.commentary.replace("\n",""))
            data["#Position"].append(len(annotation.position.all()))
            tag_list = []
            for i in annotation.tags.all():
                tag_list.append(i.tag_id)
            data["Tags"].append(tag_list)
        print(data)
    if result == "Peptide":
        data= {"type": "Peptide", "Accession":[], "Commentary":[], "Tags":[],"Length":[]}
        for peptide in query:
            data["Accession"].append(peptide.accesion)
            data["Commentary"].append(peptide.commentary.replace("\n",""))
            data["Length"].append(len(peptide.sequence))
            tag_list = []
            for i in peptide.tags.all():
                tag_list.append(i.tag_id)
            data["Tags"].append(tag_list)
        print(data)
    return data

