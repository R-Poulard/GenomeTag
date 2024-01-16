# improt of the model
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide


"""
assert function,
 used to check if the information are meetings all the criteria 
 before being entered in the database
This will later one be completed and put in a different file
"""


def assert_genome(b):
    # assert the informations for a genome are correct
    return True


def assert_chromosome(a):
    # assert the informations for a chromosome are correct
    return True


def assert_annotation(a):
    # assert the informations for an annotation are correct
    return True


def assert_position(a):
    # assert the informations for a position are correct
    return True


def assert_peptide(a):
    # assert the informations for a peptide are correct
    return True


def assert_position_peptide(a):
    # assert the information for the position are correct
    # this is used only for peptide 
    # (might reveal useless and suppressed later one)
    return True


def chromosome_loader(dic_genome, add_genome=False):
        """
        Input:
            dict: A dictionary of this format:
                {
                    'genome_name': genome,
                    genome: {
                        'chromosome': {
                            'start_position': start_position,
                            'end_position': end_position,
                            'chromosome_number': chromosome_number,
                            'sequence': chromosome_sequence
                        }
                    }
                }

        create and add chromosome to a genome
        if add_genome is True,
        the programme will create the genome if not in dbd

        Returns: (Genome object added to the database ,
                    List of Chromosome added to the database)
                or None if error
        """
        try:
            to_save = False
            if not Genome.objects.filter(id=dic_genome['genome_name']).exists():
                if not add_genome:
                    raise Exception("Genome not found")
                else:
                    assert_genome(dic_genome)
                    g = Genome(id=dic_genome['genome_name'])
                    to_save = True
            else:
                g = Genome.objects.filter(id=dic_genome['genome_name']).first()
            chr_list = []
            genome_name = dic_genome['genome_name']
            for chr in dic_genome[genome_name]['chromosome']:
                assert_chromosome(dic_genome[genome_name][chr])
            if to_save:
                g.save()
            for chr in dic_genome[genome_name]['chromosome']:
                start = dic_genome[genome_name][chr]["start_position"]
                end = dic_genome[genome_name][chr]["end_position"]
                seq = dic_genome[genome_name][chr]["sequence"]
                chr_list.append(
                    Chromosome(accession_number=chr, genome=g, start=start, end=end, sequence=seq)
                    )
            for chr in chr_list:
                chr.save()
            return (g, chr_list)
        except Exception as e:
            print(e)
            return None


def annotation_loader(dic_annot):
        """
        Input:
            dict: A dictionary of this format:
                {
                    'genome_name': genome,
                    genome: {
                        'gene': {
                            'start_position': start_position,
                            'end_position': end_position,
                            'chromosome_name': chromosome_name,
                            'sequence': gene_sequence
                        }
                    }
                }

        create annotation of cds and add them to the dbd for an existing
        Geneome and Chromosome

        This will also create the Position along the Chromosome 
        if not already in dbd

        Returns: list of all cds added
                or None if error
        """

        try:
            genome_name = dic_annot['genome_name']
            g = Genome.objects.filter(id=genome_name)
            if not g.exists():
                raise Exception("Genome not found")
            g = g.first()
            for cds in dic_annot[genome_name]:
                assert_annotation(dic_annot[genome_name][cds])
                assert_position(dic_annot[genome_name][cds])
            cds_list = []
            for cds in dic_annot[genome_name]['gene']:
                start = int(dic_annot[genome_name][cds]["start_position"])
                end = int(dic_annot[genome_name][cds]["end_position"])
                chromosome = dic_annot[genome_name][cds]["chromosome_name"]
                chr = Chromosome.objects.filter(accession_number=chromosome, genome=g)
                if not chr.exists():
                    raise Exception("Chromosome not found" + cds)
                chr = chr.first()
                pos = Position.objects.filter(start=start, end=end, chromosome=chr, strand="+")
                if not pos.exists():
                    start_relative = start - chr.start
                    end_relative = end - chr.end
                    pos = Position(start=start, end=end, start_relative=start_relative,
                                   end_relative=end_relative, strand="+", chromosome=chr)
                    pos.save()
                else:
                    pos = pos.first()
                a = Annotation(accession=cds, status="u")
                a.save()
                a.position.add(pos)
                cds_list.append(a)
            return cds_list
        except Exception as e:
            print(e)
            return None


def peptide_loader(dic_peptide):
        """
        Input:
            dict: A dictionary of this format:
                {
                    'genome_name': genome,
                    genome: {
                        'gene': {
                            'start_position': start_position,
                            'end_position': end_position,
                            'chromosome_name': chromosome_name,
                            'sequence': gene_sequence
                        }
                    }
                }
        create peptide for an existing Genome and Chromosome

        This will try to link them to annotation on the same position interval
        but won't create any additional annotation and position

        Returns: list of all peptide added
                or None if error
        """

        try:
            genome_name = dic_peptide['genome_name']
            g = Genome.objects.filter(id=genome_name)
            if not g.exists():
                raise Exception("Genome not found")
            g = g.first()
            for pep in dic_peptide[genome_name]:
                assert_peptide(dic_peptide[genome_name][pep])
                assert_position_peptide(dic_peptide[genome_name][pep])
            pep_list = []
            for pep in dic_peptide[genome_name]['protein']:
                start = int(dic_peptide[genome_name][pep]["start_position"])
                end = int(dic_peptide[genome_name][pep]["end_position"])
                chromosome = dic_peptide[genome_name][pep]["chromosome_name"]
                sequence = dic_peptide[genome_name][pep]["sequence"]
                chr = Chromosome.objects.filter(accession_number=chromosome, genome=g)
                if not chr.exists():
                    raise Exception("Chromosome not found " + pep)
                chr = chr.first()
                pos = Position.objects.filter(start=start, end=end, chromosome=chr, strand="+")
                p = Peptide(accesion=pep, sequence=sequence)
                p.save()
                if pos.exists():
                    pos = list(pos)
                    a = Annotation.objects.filter(position__in=pos)
                    if a.exists():
                        a=list(a)
                        p.annotation.add(*a)
                pep_list.append(p)
            return pep_list
        except Exception as e:
            print(e)
            return None


# Script to run in manage shell to add the mg1655 annotation to the database
# This will take a little bit of time (15 min)
# NO NEED TO RERUN THE SCRIPT ON EACH START OF SERVER
"""
import loader
import parser
g=parser.genome_parser("data/Escherichia_coli_str_k_12_substr_mg1655.fa")
m=loader.chromosome_loader(g,True)
c=parser.cds_parser("data/Escherichia_coli_str_k_12_substr_mg1655_cds.fa")
n=loader.annotation_loader(c)
p=parser.protein_parser("data/Escherichia_coli_str_k_12_substr_mg1655_pep.fa")
pep = loader.peptide_loader(p)
"""
