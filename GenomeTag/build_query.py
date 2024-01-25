from GenomeTag.search_field import search_dic
from django.db.models import Q
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide
from django.db.models import Count

"""
search_dic = {
        "Genome": ["Access Number","Number Chromosome", "Chromosome accession number", "DOI link", "Species"],
        "Chromosome": ["Access Number", "Start Position", "End Position", "Length", "Genome id", "Sequence", "Species"],
        "Peptide": ["Access Number", "Proteique Sequence", "Size", "Tag id", "Annotation Acess Number"],
        "Annotation": ["Access Number", "Start Position", "End Position", "Chromosome access number", "Genome access number", "Author id", "Tag id", "Element in text"]
}
"""
#'result': ['Genome'], 'negation': ['0', '1'], 'condition': ['0', '1'], 'text_field': ['123', '345'], 'connector': ['0'], 'launch': ['Search']}>


def check_query(form):
    return True


def build_query(form):
    form=dict(form)
    print(form)
    res_list = []
    for i in range(len(form['text_field'])):
        dic = {"negation": int(form['negation'][i]), "condition": int(form['condition'][i]), "value": form["text_field"][i]}
        print("dic inside loop", dic)
        res_list.append(single_query(form['result'][0], dic))
    print(res_list)
    res = res_list[0]
    print("debut",res)
    if 'connector' in form:
        for i in range(len(form['connector'])):
            if int(form['connector'][i]) == 1:
                print("OR")
                res = res.union(res_list[i+1])
            else:
                res = res & res_list[i+1]
    
    return res


def single_query(result, form):
    cls = Genome
    condition = Q()
    print("---- debut single query---")
    print(result)
    if result == "Genome":
        print("ici")
        cls = Genome
        condition = ask_genome(form)
        print(condition)
    elif result == "Chromosome":
        cls = Chromosome
        condition = ask_chromosome(form)
    elif result == "Peptide":
        cls = Peptide
        condition = ask_peptide(form)
    elif result == "Annotation":
        cls = Annotation
        condition = ask_annotation(form)
    if form['negation'] == 1:
        print("ici")
        return cls.objects.filter(~condition)
    else:
        return cls.objects.filter(condition)


def ask_genome(form):
    print("------- into ask genome")

    cond = form['condition']
    #"Access Number","Number Chromosome", "Chromosome accession number", "DOI link", "Species"
    print(cond)
    if cond == 0:
        print("la")
        return Q(id=form['value'])
    elif cond == 1:
        grouped_data = Chromosome.objects.values('genome').annotate(category_count=Count('genome'))
        filtered_data = grouped_data.filter(category_count=int(form['value']))
        id_genome = [item['genome'] for item in filtered_data]
        return Q(id__in=id_genome)
    elif cond == 2:
        chr_data = Chromosome.objects.values(accession_number=form['value'])['genome']
        return Q(id == chr_data)
    elif cond == 3:
        return Q(DOI=form["value"])
    elif cond == 4:
        return Q(Species=form["value"])
    return Q()


def ask_chromosome(form):
    return Q()


def ask_peptide(form):
    return Q()


def ask_annotation(form):
    return Q()