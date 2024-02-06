from Bio.Blast import NCBIWWW


def perform_blast(blast_type, database, seq):
    result = NCBIWWW.qblast(blast_type, database, seq)

    return result.read()
