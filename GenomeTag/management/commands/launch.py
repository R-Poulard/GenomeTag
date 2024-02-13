from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide, Tag, CustomUser
import loader as ld
import parser as pr
import create_tracks
import os
import shutil

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("path", nargs="+", type=str)

    def handle(self, *args, **options):
        self.stdout.write("#Creation of the database", ending="\n")
        self.stdout.flush()
        call_command('makemigrations','GenomeTag')
        call_command('migrate')
        self.stdout.write(" Done",ending="\n")
        self.stdout.flush()
        path=options['path'][0]
        for file in os.listdir(options['path'][0]):
            #fill database
            if '_cds.fa' in file:
                name = file.replace('_cds.fa', '')
                self.stdout.write("##Treating data of genome: "+name, ending="")
                self.stdout.flush()
                g=pr.genome_parser(path+name+".fa")
                m = ld.chromosome_loader(g,True)
                self.stdout.write("-----", ending="")
                self.stdout.flush()
                c = pr.cds_parser(path+name+"_cds.fa")
                n = ld.annotation_loader(c)
                self.stdout.write("-----", ending="")
                self.stdout.flush()
                p = pr.protein_parser(path+name+"_pep.fa")
                pep = ld.peptide_loader(p)
                self.stdout.write("DONE", ending="\n")
                self.stdout.flush()                
                for chr in m[1]:
                    with open(path+name+".fa","r") as from_file:
                        from_file.readline()
                        with open("./projet_web/static/data/"+name+"--"+chr.accession_number+".fa",'w') as to_file:
                            to_file.write(">"+chr.accession_number+"\n")
                            shutil.copyfileobj(from_file,to_file)
                    os.system("samtools faidx ./projet_web/static/data/"+name+"--"+chr.accession_number+".fa -o ./projet_web/static/data/"+name+"--"+chr.accession_number+".fai")
                    create_tracks.create_file(chr,"./projet_web/static/data/"+name+"--"+chr.accession_number+"_tracks.bed")
        self.stdout.write("#Creation of users", ending="\n")
        call_command('createsuperuser',interactive=False,username="admin_example",role="r")
        adm=CustomUser.objects.get(username="admin_example")
        adm.set_password("example")
        adm.save()
        c1=CustomUser(role="r",is_active=True,phone="+33798765432",affiliation="GenomeTag",username="Reviewer_User",email="reviewer@genometag.com")
        c2=CustomUser(role="a",is_active=True,phone="+33798765432",affiliation="GenomeTag",username="Annotator_User",email="annotator@genometag.com")
        c3=CustomUser(role="v",is_active=True,phone="+33798765432",affiliation="GenomeTag",username="Viewer_User",email="viewer@genometag.com")
        c1.save()
        c1.set_password('example')
        c1.save()
        c2.save()
        c2.set_password('example')
        c2.save()
        c3.save()
        c3.set_password('example')
        c3.save()
        self.stdout.write("ADMIN\n username= admin_example password= example", ending="\n")
        self.stdout.write("Viewer\n email= viewer@genometag.com username= View_User password= example", ending="\n")
        self.stdout.write("Annotator\n email= annotator@genometag.com username= Annotator_User password= example", ending="\n")
        self.stdout.write("Reviewer\n email= reviewer@genometag.com username= Reviewer_User password= example", ending="\n")

        self.stdout.write("#Finishing last details", ending="\n")
        t1=Tag(tag_id="CDS",text="This tag is used to represent coding sequence in the genome")
        t2=Tag(tag_id="Non coding",text="This tag is used to represent non coding sequence on the genome, it can be mutiple things")
        t3=Tag(tag_id="IGORF",text="Ancestrally non coding sequence that started to be synthetise in peptide after evolution mecanisme")
        t4=Tag(tag_id="Promoter",text="This tag is used to represent non coding sequence on the genome, more specificaly promoter of cds")
        t5=Tag(tag_id="TFactor",text="Transcription Factor are used to allow transcription of their corresponding cds")
        t1.save()
        t2.save()
        t3.save()
        t4.save()
        t5.save()
        for annot in Annotation.objects.all():
            annot.tags.add(t1)
            annot.status="v"
            annot.author=c2
            annot.reviewer=c3
            annot.save()
        t6=Tag(tag_id="Protein",text="Protein tag")
        t7=Tag(tag_id="Hydrophobe",text="Hydrophobe protein")
        t8=Tag(tag_id="Hydrophile",text="Hydrophile protein")
        t6.save()
        t7.save()
        t8.save()
        for pep in Peptide.objects.all():
            pep.tags.add(t6)
            pep.save()
        self.stdout.write("##### DONE ENJOY ######", ending="")
