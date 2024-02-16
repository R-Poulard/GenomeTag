from GenomeTag.models import Annotation


def create_file(chr, path):
    tracks = ""
    print(chr)
    m = Annotation.objects.filter(position__chromosome=chr)
    for annot in m:
        for pos in annot.position.all():
            tracks += (
                pos.chromosome.accession_number
                + "\t"
                + str(pos.start)
                + "\t"
                + str(pos.end)
                + "\t"
                + annot.accession
                + "\t0\t"
                + str(pos.start)
                + "\t"
                + str(pos.end)
                + "\n"
            )
    with open(path, "w") as f:
        f.write(tracks)
    return True
