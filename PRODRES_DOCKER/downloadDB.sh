# uniprot-trembl
cd /db/uniprot/ && \
   curl -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/uniref/uniref90/uniref90.fasta.gz; exit 0

# pfam-A
cd /db/pfam/ && \
    curl -O ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam30.0/Pfam-A.hmm.gz && \
    curl -O ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam30.0/Pfam-A.hmm.dat.gz

# 1. unzip uniprot

cd /db/uniprot/ && \
    gunzip uniref90.fasta.gz && \
    makeblastdb -in uniref90.fasta -dbtype prot; exit 0

# 2. unzip PFAM-A (30.0)
cd /db/pfam/ && \
    gunzip Pfam-A.hmm.gz && \
    gunzip Pfam-A.hmm.dat.gz && \
    hmmpress Pfam-A.hmm; exit 0
