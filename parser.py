import os


def genome_parser(genome_fasta_file):
    """
    Parse the genome and create a dictionary containing the sequence of
    each chromosome

    Parameters:
        genome_fasta_file (string): FASTA file containing the genome of a prokaryote

    Returns:
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
    """
    dic_genome = {}

    with open(genome_fasta_file, "r") as file:
        lines = file.readlines()

    genome = os.path.basename(genome_fasta_file).split(".")[0].replace("Escherichia_coli_", "")
    dic_genome["genome_name"] = genome
    dic_genome[genome] = {}
    dic_genome["Species"] = "Escherichia coli"

    current_chromosome = None
    dic_genome[genome]["chromosome"] = []
    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            line_parts = line.split()
            chromosome_name = line_parts[2].split(":")[1]
            current_chromosome = chromosome_name

            dic_genome[genome]["chromosome"].append(chromosome_name)
            dic_genome[genome][chromosome_name] = {
                "start_position": line_parts[2].split(":")[3],
                "end_position": line_parts[2].split(":")[4],
                "chromosome_number": line_parts[2].split(":")[5],
                "sequence": "",
            }
        else:
            if current_chromosome:
                dic_genome[genome][current_chromosome]["sequence"] += line

    return dic_genome


def cds_parser(cds_fasta_file):
    """
    Parse the genome and create a dictionary containing the sequence of
    each CDS of the genome

    Parameters:
        cds_fasta_file (string): FASTA file containing the CDS of a prokaryote

    Returns:
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
    """
    dic_genome = {}

    with open(cds_fasta_file, "r") as f:
        lines = f.readlines()

    genome = os.path.basename(cds_fasta_file).split(".")[0].replace("_cds", "").replace("Escherichia_coli_", "")
    dic_genome["genome_name"] = genome
    dic_genome[genome] = {}
    dic_genome[genome]["gene"] = []
    current_gene = None

    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            line_parts = line.split()
            gene_name = line_parts[0][1:]
            current_gene = gene_name

            dic_genome[genome]["gene"].append(gene_name)
            dic_genome[genome][gene_name] = {
                "start_position": line_parts[2].split(":")[3],
                "end_position": line_parts[2].split(":")[4],
                "chromosome_name": line_parts[2].split(":")[1],
                "sequence": "",
                "commentary": '\n'.join(line_parts[3:])
            }
        else:
            if current_gene:
                dic_genome[genome][current_gene]["sequence"] += line

    return dic_genome


def protein_parser(protein_fasta_file):
    """
    Parse the genome and create a dictionary containing the sequence of
    each protein of the genome

    Parameters:
        protein_fasta_file (string): FASTA file containing the protein of a prokaryote

    Returns:
        dict: A dictionary of this format:
            {
                'genome_name': genome,
                genome: {
                    'protein': {
                        'start_position': start_position,
                        'end_position': end_position,
                        'chromosome_name': chromosome_name,
                        'sequence': protein_sequence
                    }
                }
            }
    """
    dic_genome = {}

    with open(protein_fasta_file, "r") as f:
        lines = f.readlines()

    genome = os.path.basename(protein_fasta_file).split(".")[0].replace("_pep","").replace("Escherichia_coli_", "")
    dic_genome["genome_name"] = genome
    dic_genome[genome] = {}
    dic_genome[genome]["protein"] = []
    current_protein = None

    for line in lines:
        line = line.strip()
        if line.startswith(">"):
            line_parts = line.split()
            protein_name = line_parts[0][1:]
            current_protein = protein_name
            dic_genome[genome]["protein"].append(protein_name)
            dic_genome[genome][protein_name] = {
                "start_position": line_parts[2].split(":")[3],
                "end_position": line_parts[2].split(":")[4],
                "chromosome_name": line_parts[2].split(":")[1],
                "sequence": "",
                "commentary": '\n'.join(line_parts[3:])
            }
        else:
            if current_protein:
                dic_genome[genome][current_protein]["sequence"] += line

    return dic_genome
