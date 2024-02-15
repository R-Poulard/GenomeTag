from GenomeTag.models import Genome, Chromosome, Position, Annotation, Peptide, Attribution, CustomUser, Tag, Tag, Review, CustomUser,Mailbox


def not_found(l,start,end,strand,chr):
    for pos in l:
        if pos.start==start and pos.end==end and pos.strand==strand and pos.chromosome==chr:
            return False
    return True


def create_manual_attr(form):
    creat = CustomUser.objects.filter(email=form['Creator'][0])
    if not creat.exists():
        return "Error identifying who is the creator, be sure to be correctly logged in and a valid email."
    creat = creat[0]
    annotator = CustomUser.objects.filter(email=form['Annotator'][0])
    if not annotator.exists():
        return "The user you are trying to attribute the annotation does not exist."
    annotator = annotator[0]
    if not annotator.has_perm('GenomeTag.annotate'):
        return "The user you are trying to attribute the annotation doesn't have a role allowing him to."
    position = []
    unsaved_pos = []
    for i in range(len(form['Strand'])):
        strand = form['Strand'][i]
        f=form['Chromosome'][i].split('\t')
        genome=f[0]
        acces=f[1]
        chr = Chromosome.objects.filter(genome__annotable=True,genome__id=genome, accession_number=acces)
        start = form['Start'][i]
        end = form['End'][i]
        if strand not in ['+', '-'] or not chr.exists() or not start.isdigit() or not end.isdigit():
            return "The position "+str(i)+" has strange field that should not be allowed."
        start = int(start)
        end = int(end)
        chr = chr[0]
        if start <= 0 or end <= 0 or start < chr.start or end > chr.end:
            return "The position "+str(i)+" has impossible start and end position."
        if strand == '-':
            start_temp = max(start, end)
            end = min(start, end)
            start = start_temp
        else:
            end_temp = max(start, end)
            start = min(start, end)
            end = end_temp
        
        end_relative = end+chr.start
        start_relative = start+chr.start
        pos = Position.objects.filter(start=start, end=end,
                                      strand=strand, chromosome=chr)
        if pos.exists() and pos[0] not in position:
            position.append(pos[0])
        elif not_found(unsaved_pos, start, end, strand, chr):
            pos = Position(start=start, end=end,
                                          strand=strand,
                                          end_relative=end_relative,
                                          start_relative=start_relative,
                                          chromosome=chr)
            unsaved_pos.append(pos)
            position.append(pos)
    for p in unsaved_pos:
        p.save()
    a = Attribution(annotator=annotator, requester=creat)
    a.save()
    a.possition.add(*position)
    a.save()
    return "Attribution created succesfuly"

def not_found_return(l,start,end,strand,chr):
    for pos in l:
        if pos.start==start and pos.end==end and pos.strand==strand and pos.chromosome==chr:
            return pos
    return None

#email  genom   chr strand  start   end ect...
def create_file_attr(form,file):
    creat = CustomUser.objects.filter(email=form.cleaned_data['Creator'])
    if not creat.exists():
        return "Error identifying who is the creator, be sure to be correctly logged in or have a valid email."
    creat = creat[0]   
    file_name, file_content = next(iter(file.items()), (None, None))
    i=1
    atrribution=[]
    position=[]
    unsaved_position=[]
    for line in file_content:
        line=str(line,'utf-8').strip()
        
        sp=line.split('\t')
        print(sp)
        print(len(sp[1:]))
        if len(sp)<5 or len(sp[1:])%5!=0:
            return "Error of format in line "+str(i)+" some filed might be missing"
        annotator = CustomUser.objects.filter(email=sp[0])
        if not annotator.exists():
            return "Line "+str(i)+": The user you are trying to attribute the annotation does not exist."
        annotator = annotator[0]
        if not annotator.has_perm('GenomeTag.annotate'):
            return "Line "+str(i)+": The user you are trying to attribute the annotation doesn't have a role allowing him to."
        pos_sinlge_attribution=[]
        for pos in range(1,len(sp),5):
            genome=sp[pos]
            acces=sp[pos+1]
            strand=sp[pos+2]
            start=sp[pos+3]
            end=sp[pos+4]
            print(genome,acces,strand,start,end)
            chr = Chromosome.objects.filter(genome__annotable=True,genome__id=genome, accession_number=acces)
            if strand not in ['+', '-'] or not chr.exists() or not start.isdigit() or not end.isdigit():
                return "Line "+str(i)+": The position "+str(pos+1)+" has incoherent field or the chromosome doesn't exist"
            start = int(start)
            end = int(end)
            chr = chr[0]
            if start <= 0 or end <= 0 or start < chr.start or end > chr.end:
                return "Line "+str(i)+": The position "+str(pos+1)+" has impossible start and end position."
            if strand == '-':
                start_temp = max(start, end)
                end = min(start, end)
                start = start_temp
            else:
                end_temp = max(start, end)
                start = min(start, end)
                end = end_temp
        
            end_relative = end+chr.start
            start_relative = start+chr.start
            pos = Position.objects.filter(start=start, end=end,
                                      strand=strand, chromosome=chr)
            if pos.exists() and pos[0] not in pos_sinlge_attribution:
                pos_sinlge_attribution.append(pos[0])
            else:
                new_pos=not_found_return(unsaved_position, start, end, strand, chr)
                if new_pos==None:
                    pos = Position(start=start, end=end,
                                          strand=strand,
                                          end_relative=end_relative,
                                          start_relative=start_relative,
                                          chromosome=chr)
                    pos_sinlge_attribution.append(pos)
                    unsaved_position.append(pos)
                else:
                    pos_sinlge_attribution.append(new_pos)
            i+=1
        position.append(pos_sinlge_attribution)
        atrribution.append(Attribution(annotator=annotator, requester=creat))
    for i in unsaved_position:
        i.save()
    err=""
    print(position)
    print(atrribution)
    for att in range(len(atrribution)):
        try:
            attrib=atrribution[att]
            attrib.save()
            print(position[att])
            attrib.possition.add(*position[att])
            attrib.save()
            annotator = attrib.annotator
            subject = "New Attribution Added"
            message = f"Hello {attrib.annotator.email},\n\nAn attribution has been added to you."
            sender = attrib.requester.email

            Mailbox.objects.create(
               user=annotator, subject=subject, message=message, sender=sender
            )
        except Exception as e:
            print(e)
            err+="Issue creating the attribution on line "+str(att)+"\n"
            continue
    if err!="":
        err+="The rest of the field has been processed correctly"
    else:
        err="The whole file has been processed correctly"

    return err
