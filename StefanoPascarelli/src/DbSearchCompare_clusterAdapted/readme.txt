*** When importing in other machine, modify first parameters of "Trigger" and "Pfamscan/pfamscan.pl" *** 
(and maybe more)
params to be mod: slowoverwatch,Trigger

####################################################################################################
### Quick Pipeline for comparison of fast DB search versus a standard slow jackhmmer on whole DB ###
####################################################################################################


MOD FOR CLUSTER





there are two pipelines.

SAVE: 4 pfamscan parameters + slow, each jackhmmer is performed on one core therefore the number of submitted jobs is 5*Number of fasta seqs.
It is initiated by "python SAVE_provaslowoverwatch.py

node: only 1 pfamscan parameter + slow. all commands are performed on a node with 16 cores.
It is initiated by "sbatch nodejob.sh"

standard input for both is a folder with single sequences in fasta format.

All parameters to be set, like outputfolder, inputfiles, jackhmmer exclusion threshold are inside the scripts
(usually provaslowoverwatch.py or jackbigs.py)














### Parameters file ###

up to now, it HAS to be formatted this way:

          pscan Evalue=0.01 clan_overlap=True

only in the first line


### Legend: ###

slowoverwatch.py - to queue slow jobs
overwatch.py - to queue fast jobs
db is split in groups of two sequences


Trigger - usage: Trigger infile.fasta outdir
 dependencies:
    fa2prfs_pfamscan.sh: bash evocation of pipeline each query
    pfam_scan_to_profile.py: pfamscan hits database creation
         myfunc.py: collection of functions, mainly database management
             mydb_common.py: dependencies
                   mybase: dependencies
         my_uniqueseq.py: from temporary database, removes repeated sequences
    legend.py: creates legend.txt in main directory

jackbigs.py - pipeline for slow and big or small fast jackhmmer
domtest.py - comparison of domains
scoredistr.py - graph of domtest results, either in score distribution and pie charts of overlapping
parsejackcompare.py - quick comparison between fast and slow results


    
gather from fastpssm what is needed for pfamscan.





Parameters of PFAMSCAN: pfam_scan_to_profile.py
Parameters of HMMER: jackbigs.py




to do:
-improve comparison of sequences between the two modes
-improve time statistics?!?

ver 0.92
-minor bugs
-added input parameter file handling

ver 0.91
-fixed minor bugs...
-jk
-implemented quick time comparison and widened superposition of hits statistics


SP+coll.
