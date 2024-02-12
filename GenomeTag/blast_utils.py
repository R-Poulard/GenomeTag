from Bio.Blast import NCBIWWW


def perform_blast(blast_type, database, seq, hitlist_size=50, expect=10.0):
    result = NCBIWWW.qblast(blast_type, database, seq, hitlist_size=hitlist_size, expect=expect)

    return result.read()
