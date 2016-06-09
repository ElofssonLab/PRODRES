Reminder: do a better readme...












jk..

try: >>python fastPSSM.py

>>python fastPSSM.py --input test/prova1.fa --output test/prova1/

!!!!!! WARNING: MUST MODIFY FIRST VARIABLES IN fastPSSM_environment !!!!!!!!!!!!

extra parameters up to now:

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
            [**] = compulsory parameter

            example call:
