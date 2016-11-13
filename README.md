# PRODRES : PROtein Domain REduced Search

- Download (or clone) the PRODRES Git repository
- Download and unzip the following files from Pfam:
  - Pfam-A.hmm.dat.gz (ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.dat.gz)
  - Pfam-A.hmm.gz (ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz)
- Download and unzip PfamScan.pl tool from ftp://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/PfamScan.tar.gz
- Dowload the database from http://topcons.net/static/download/prodres_db/30.0/prodres_db.nr90.sqlite3 inside the PRODRES folder 
- Download a fall-back database, e.g. Uniref90 (from ftp://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz)
- Download current PSI-BLAST version (from ftp://ftp.ncbi.nih.gov/blast/executables/LATEST/)
- Download hmmer software (from http://hmmer.org/download.html)
- Use the hmmpress command from the hmmer software on the Pfam-A.hmm file
- Create a folder, e.g. pfam/ and put the files Pfam-A.hmm.dat, Pfam-A.hmm and the created files Pfam-A.hmm.h3f, Pfam-A.hmm.h3m, Pfam-A.hmm.h3i and Pfam-A.hmm.h3p inside it
- Running the workflow:
  - Basic usage: `python PRODRES.py [parameters]`
                  -h show help 
                  --pfamscan_e-val PFAMSCAN_E_VAL
                        e-value threshold for pfamscan passage, usage:
                        --pfamscan_e-val 0.1 (default: 10.0)
                  --pfamscan_bitscore PFAMSCAN_BITSCORE
                        bit-value threshold for pfamscan passage, usage:
                        --pfamscan_bitscore 5 (default: None)
                  --pfamscan_clan-overlap PFAMSCAN_CLAN_OVERLAP
                        enable pfamscan resolve clan overlaps (default: True)
                  --jackhmmer_max_iter JACKHMMER_MAX_ITER
                        set the maximum number of iterations for jackhmmer
                        (default: 3)
                  --jackhmmer_e-val JACKHMMER_E_VAL
                        set the e-value threshold for jackhmmer, usage:
                        --jackhmmer_e-val 0.1 (default: None)
                  --jackhmmer_bitscore JACKHMMER_BITSCORE
                        set the bitscore threshold for jackhmmer (jackhmmer
                        option --incT), usage: --jackhmmer_bitscore 10
                        (default: 25.0)
                  --psiblast_iter PSIBLAST_ITER
                        set the number of iterations for psiblast (default: 3)
                  --psiblast_e-val PSIBLAST_E_VAL
                        set the e-value threshold for psiblast, usage:
                        --psiblast_e-val 0.1 (default: 0.1)
                  --psiblast_outfmt PSIBLAST_OUTFMT
                        set the outformat for psiblast, refer to blast manual
                        (default: None)
                  --input INPUT_FILE    
                        input file that needs to be in fasta format, can be
                        one or more sequences (default: None)
                  --output OUTPUT       
                        the path to the output folder. The folder will be
                        created if it does not exist already. (default: None)
                  --second-search {psiblast,jackhmmer}
                  --jackhmmer-threshold-type {e-value,bit-score}
                  --pfam-dir PFAM_DIR   
                        pfam dir path (default: None)
                  --pfamscan-script PFAMSCAN_SCRIPT
                        path to pfam_scan.pl (default: None)
                  --uniprot-db-fasta UNIPROT_DB_FASTA
                        path to uniprot_db fasta file (default: None)
                  --pfam_database_dimension PFAM_DATABASE_DIMENSION
                        dimension of pfam database (default: 28332677)
                  --verbose  output more information (default: False)

- example call for 1 sequence using PSI-BLAST to create the PSSM:       
`python PRODRES.py --input test/single_seq.fa --output test/ --pfam-dir pfam --pfamscan-script PfamScan/pfam_scan.pl --pfamscan_bitscore 2 --uniprot-db-fasta uniref90.fasta --second-search psiblast --psiblast_e-val 0.001 --psiblast_iter 3`

- example call for multiple sequences using JACKHMMER to create the PSSM:        
`python PRODRES.py --input test/multiple_seq.fa --output test/ --pfam-dir pfam --pfamscan-script PfamScan/pfam_scan.pl --pfamscan_bitscore 2 --uniprot-db-fasta uniref90.fasta --second-search jackhmmer --jackhmmer-threshold-type e-value --jackhmmer_e-val 0.001`

# PRODRES Docker portable version 

in order to install: 

1. have DockerFile in the same folder of src/ and test/

2. execute the following command (*remember the dot at the end*):      
`docker build -t fastpssm .`

3. wait for the required databases to be downloaded

4. Access the virtual machine with a ready-to-execute prodres pipeline using:              
  - `docker run -t -i prodres`
  - then access prodres/ folder and call the pipeline     
  - example call for 1 sequence using PSI-BLAST to create the PSSM:    
  `python PRODRES.py --input test/single_seq.fa --output test/ --pfam-dir pfam --pfamscan-script PfamScan/pfam_scan.pl --pfamscan_bitscore 2 --uniprot-db-fasta uniref90.fasta --second-search psiblast --psiblast_e-val 0.001 --psiblast_iter 3`
  - example call for multiple sequences using JACKHMMER to create the PSSM:    
  `python PRODRES.py --input test/multiple_seq.fa --output test/ --pfam-dir pfam --pfamscan-script PfamScan/pfam_scan.pl --pfamscan_bitscore 2 --uniprot-db-fasta uniref90.fasta --second-search jackhmmer --jackhmmer-threshold-type e-value --jackhmmer_e-val 0.001`

5. Alternatively, import an input folder from local machine with:     
  `docker run -t -i -v /path/to/import/:/path/in/virtualmachine/ prodres`     
  then access prodres/ folder and call the pipeline to the imported data:      
  `python PRODRES.py --input /path/in/virtualmachine/filename.fasta --output /path/in/virtualmachine/output/`    
