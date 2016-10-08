# FastPSSM : Fast generation of Position-Specific Scoring Matrices

- Download (or clone) the FastPSSM Git repository
- Dowload and unzip the database from http://topcons.net/static/download/topcons2_database.zip inside the FastPSSM folder that is created 
- There are three pathes in fastPSSM_environment.py that need to be adjusted:
  - pfam: /pfam/to/the/pfam/folder/
  - pfamscan: /path/to/pfam_scan.pl
  - uniprot_db: /path/to/uniprot|uniref/database

Running the workflow:

>>>fastPSSM pipeline<<<
            usage: python fastPSSM.py <param>

            parameters:
                --input <input file>:                   needs to be in fasta format, can be one or more sequences [**]
                --output <output folder>:               the path to the output folder [**]
                --psiblast / --jackhmmer:               option to decide the second search to be performed (by default it is hmmer)
                --pfamscan_e-val <e-value>:             e-value threshold for pfamscan passage (default is 10)
                --pfamscan_clan-overlap <T/F>:          set clan-overlap parameter of pfamscan (default is True)
                --jackhmmer_iter <# of iterations>:     set the number of iterations for jackhmmer (default is 3)
                --jackhmmer_e-val <e-value>:            set the e-value threshold for jackhmmer
                --jackhmmer_bitscore <bitscore>:        set the bitscore threshold for jackhmmer (default is 25)
                --psiblast_iter <# of iterations>:      set the number of iterations for psiblast (default is 3)
                --psiblast_e-val <e-value>:             set the e-value threshold for psiblast (default is 0.1)
                --psiblast_outfmt <int_value>:          set the outformat for psiblast, refer to blast manual
            [**] = compulsory parameter

example call for 1 sequence:
python fastPSSM.py --input test/single_seq.fa --output test/rst_1_seq/ --psiblast

example call for multipls sequences:
python fastPSSM.py --input test/multiple_seq.fa.fa --output test/rst_many_seqs/ --jackhmmer
