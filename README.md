# fastPSSM : fast generation of Position-Specific Scoring Matrices

- Download (or clone) the FastPSSM Git repository
- Dowload and unzip the database from http://topcons.net/static/download/topcons2_database.zip (e.g. inside the FastPSSM folder) 
- There are three paths in fastPSSM_environment.py that need to be adjusted:
  - **pfam**: /pfam/to/the/pfam/folder/
  - **pfamscan**: /path/to/pfam_scan.pl
  - **uniprot_db**: /path/to/fall-back/database [e.g. Uniref90]

- Running the workflow:
  - Basic usage: `python fastPSSM.py [parameters]`

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

- example call for 1 sequence using PSI-BLAST to create the PSSM:
  - `python fastPSSM.py --input test/single_seq.fa --output test/rst_1_seq/ --psiblast`

- example call for multiple sequences using JACKHMMER to create the PSSM:
  - `python fastPSSM.py --input test/multiple_seq.fa --output test/rst_many_seqs/ --jackhmmer`

# fastPSSM Docker portable version 

in order to install: 

1. have DockerFile in the same folder of src/ and test/

2. execute the following command (*remember the dot at the end*): 
  - `docker build -t fastpssm .`

3. wait for the required databases to be downloaded

4a. you can access the virtual machine with the ready-to-execute fastpssm pipeline using: 
  - `docker run -t -i fastpssm`
  - then access fastpssm/ folder and call the pipeline 
  - example call for 1 sequence using PSI-BLAST to create the PSSM:
    - `python fastPSSM.py --input test/single_seq.fa --output test/rst_1_seq/ --psiblast`
  - example call for multiple sequences using JACKHMMER to create the PSSM:
    - `python fastPSSM.py --input test/multiple_seq.fa --output test/rst_many_seqs/ --jackhmmer`

4b. or you can import an input folder from local machine with: 
  - `docker run -t -i -v /path/to/import/:/path/in/virtualmachine/ fastpssm`
  - then access fastpssm/ folder and call the pipeline to the imported data: 
    - `python fastPSSM.py --input /path/in/virtualmachine/filename.fasta --output /path/in/virtualmachine/output/`
