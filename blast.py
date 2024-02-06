from Bio.Blast import NCBIWWW

seq = "MATGGRRGAA AAPLLVAVAA LLLGAAGHLY PGEVCPGMDI RNNLTRLHEL ENCSVIEGHL QILLMFKTRP EDFRDLSFPK LIMITDYLLL FRVYGLESLK DLFPNLTVIR GSRLFFNYAL"

result = NCBIWWW.qblast("blastp", "nr", seq)
with open("my_blast.xml", "w") as save_to:
    save_to.write(result.read())

# Don't close the result here, as it has already been consumed.

with open("my_blast.xml") as result_handle:
    print(result_handle.read())

def blast(blast_type, database, seq):
    result = NCBIWWW.qblast(blast_type, database, seq)


