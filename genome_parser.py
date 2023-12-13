#création du dictionnaire Best Reciprocate Hits
import os


def genome_parser(genome_fasta_file):
    
    dic_genome = {}
    
    f = open(genome_fasta_file,'r')
    lines = f.readlines()
    f.close()
    
    genome = os.path.basename(genome_fasta_file).split(".")[0]
    dic_genome["genome_name"] = genome
    dic_genome[genome] = {}
    
    current_chromosome = None
        
    for line in lines:
        l = line.strip().split()
        if (l[0][0]=='>'):
            chromosome_name = l[2].split(":")[1]
            current_chromosome = chromosome_name #is a global scope variable to append the sequence
            dic_genome[genome]["chromosome"]=chromosome_name
            dic_genome[genome][chromosome_name] = {}
            
            start_position = l[2].split(":")[3]
            end_position = l[2].split(":")[4]
            chromosome_number = l[2].split(":")[5]
            
            dic_genome[genome][chromosome_name]["start_position"] = start_position
            dic_genome[genome][chromosome_name]["end_position"] = end_position
            dic_genome[genome][chromosome_name]["chromosome_number"] = chromosome_number
            dic_genome[genome][chromosome_name]["sequence"] = ""
                        
        else:
            line = line.strip()
            dic_genome[genome][current_chromosome]["sequence"]+=line
            
    return dic_genome
        
print(genome_parser("data/Escherichia_coli_cft073.fa"))