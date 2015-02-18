*** When importing in other machine, modify first parameters of "Trigger" and "Pfamscan/pfamscan.pl" *** 
(and maybe more)


####################################################################################################
### Quick Pipeline for comparison of fast DB search versus a standard slow jackhmmer on whole DB ###
####################################################################################################


### Legend: ###

domtest.py - comparison of domains
scoredistr.py - graph of domtest results, either in score distribution and pie charts of overlapping
parsejackcompare.py - quick comparison between fast and slow results
jackbigs.py - pipeline for slow and big or small fast jackhmmer

Trigger - usage: Trigger infile.fasta outdir
 dependencies:
    fa2prfs_pfamscan.sh: bash evocation of pipeline each query
    pfam_scan_to_profile.py: pfamscan hits database creation
         myfunc.py: collection of functions, mainly database management
             mydb_common.py: dependencies
                   mybase: dependencies
         my_uniqueseq.py: from temporary database, removes repeated sequences
    legend.py: creates legend.txt in main directory


    
gather from fastpssm what is needed for pfamscan.





Parameters of PFAMSCAN: pfam_scan_to_profile.py
Parameters of HMMER: jackbigs.py




to do:
-improve comparison of sequences between the two modes
-improve time statistics?!?

ver 0.91
-fixed minor bugs...
-jk
-implemented quick time comparison and widened superposition of hits statistics


SP+coll.
