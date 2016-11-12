FROM ubuntu:14.04

MAINTAINER Stefano Pascarelli "pasca1989@hotmail.it"

#update
RUN sudo apt-get update; apt-get install -y curl

# dirs
RUN mkdir -p /opt/BLAST /opt/HMMER3 /db/uniprot /db/pfam

# download databases

# uniprot-trembl
RUN cd /db/uniprot/ && \
    curl --ftp-port -O ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_trembl.fasta.gz; exit 0

# pfam-A
RUN cd /db/pfam/ && \
    curl -O ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam30.0/Pfam-A.hmm.gz && \
    curl -O ftp://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam30.0/Pfam-A.hmm.dat.gz

# download Nanjiang fragmented database
RUN cd /db/pfam && \
    curl -O http://protein.bio.unipd.it/stepas/pfamfull.tar.gz

# download PFAMSCAN
RUN cd opt && \
    curl -O ftp://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/PfamScan.tar.gz

# download PSIBLAST
RUN cd opt/BLAST && \
    curl -O ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.4.0+-x64-linux.tar.gz 

# download hmmer
RUN cd /opt/HMMER3 && \
    curl -O ftp://ftp.hgc.jp/pub/mirror/wustl/hmmer3/CURRENT/hmmer-3.1b1-linux-intel-x86_64.tar.gz


# update system and install apt dependencies
RUN apt-get install -y ant cmake git openjdk-7-jdk littler \
    python-numpy python-biopython python-scipy python-joblib python-matplotlib samtools xvfb && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64


# unzip PFAMSCAN
RUN cd opt && tar xzf PfamScan.tar.gz

# unzip nanjiang fragmented DB
RUN cd /db/pfam/ && tar xzf pfamfull.tar.gz

# unzip PSIBLAST
RUN cd /opt/BLAST/ && \
    tar zxf /opt/BLAST/ncbi-blast-2.4.0+-x64-linux.tar.gz

# install hmmer
RUN cd /opt/HMMER3/ && \
    tar zxvf /opt/HMMER3/hmmer-*.tar.gz && \
    cd /opt/HMMER3/hmmer* && \
    ./configure && \ 
    make && \
    make install;
    
# set database files

# 1. trembl uniprot

RUN cd /db/uniprot/ && \
    gunzip uniprot_trembl.fasta.gz && \
    makeblastdb -in uniprot_trembl.fasta -dbtype prot; exit 0

# 2. PFAM-A (30.0)
RUN cd /db/pfam/ && \
    gunzip Pfam-A.hmm.gz && \
    gunzip Pfam-A.hmm.dat.gz && \
    hmmpress Pfam-A.hmm; exit 0

# add code and modify variables
RUN mkdir fastpssm examples
ADD ./src /fastpssm
#modify variables if they are variables

# add folder with examples
ADD ./test/prova1.fa /examples/
ADD ./test/prova2.fa /examples/

# modify PfamScan source lib
RUN sed -i '7s/.*/use lib "\/opt\/PfamScan\/";/' /opt/PfamScan/pfam_scan.pl

# install dependencies of PfamScan
RUN PERL_MM_USE_DEFAULT=1 && cpan install CPAN && cpan reload 
RUN cpan install Moose
RUN cpan install Bio::SeqFeature::Generic && cpan install IPC::Run

# export $PATH
ENV PATH $PATH:/opt/BLAST/ncbi-blast-2.4.0+/bin
