# FastPSSM

Before running:

There are three pathes in pfam_scan_to_profile.py that need to be adjusted:

+ pfam_Dir: pfam database for pfam_scan
+ pfamseqdb: database containing the full length sequences for each family
+ pfamScan: location of pfam_scan


Running the workflow:

./pfam_workflow.py inFile outDir blastDir

inFile can contain one or many sequences in fasta format.

# Full sequence (uniprot sequence) database for Pfam-27.0 and CDD domain families (version 3.12)
1.  For Pfam27.0 (sequence redundancy reduced at <90% sequence identity within each
    family by CD-HIT)

    Location: triolith.nsc.liu.se
    path: /proj/bioinfo/users/x_nansh/data/uniprot/2014-11-05/pfammap_from_pfamscan/pfamseqdb_nr90/
    size: about 25 GB

    Method description:

        1). Search uniref100 (downloaded on 2014-11-05) sequences in Pfam-27.0
           (both Pfam-A and Pfam-B) by pfam_scan.pl
           Script to call pfam_scan.pl is "src/run_pfam_scan.sh" with the
           following arguments
           $ src/run_pfam_scan.sh $fafile -outpath $outpath -r "-pfamb"
           Scripts that has been used to submit jobs to clusters
           "src/submit_run_pfam_scan_triolith.sh"
           "src/submit_run_pfam_scan_uppmax.sh"


        2). Get UniprotID to PfamID mapping table for any hit with e-value <=
           1e-3. Repeated domain hits are counted only once.
           script: "src/build_seqid2pfamid_from_hmmscan.py"

        3). Get PfamID to UniprotID mapping table from the UniprotID to PfamID
           mapping table.
           script "src/build_pfamid2seqid_fromseqid2pfamid.py"

        4). Generate FASTA seuqnece files for each family 
           script "src/buildFamSeqDB_from_famid2seqidmap.py"

        5). Run CD-HIT to reduence the sequence redundancy to <90%.

        6). Create the database by "src/my_formatdb.py"

    Usage of the database: by the class MyDB defined in the script
    "src/myfunc.py"
    e.g
        pfamidList = ["PB019523", "PB017294"]
        print "numfam to read = ", len(pfamidList)
        pfamseqdb = "path_to_database/pfamseqdb_nr90/uniref100.pfam27.pfamseq.nr90"

        hdl = myfunc.MyDB(pfamseqdb)

        if hdl.failure:
            return 1

        outpath = "tmp"
        if not os.path.exists(outpath):
            os.system("mkdir -p %s"%(outpath))

        for pfamid in pfamidList:
            record = hdl.GetRecord(pfamid)
            if record:
                fpout = open("%s/%s.fa"%(outpath, pfamid), "w")
                fpout.write("%s"% record)
                fpout.close()
        hdl.close()

    see also an example script for the usage at 
    /proj/bioinfo/users/x_nansh/data/uniprot/2014-11-05/hmmscan_cdd/test_use_cddfamseqdb_nr90.py on triolith.nsc.liu.se
    also located at "src/test_use_cddfamseqdb_nr90.py" at this repository


2.  For CDD families (sequence redundancy reduced at <90% sequence identity within each
    family by CD-HIT)

    Location: triolith.nsc.liu.se
    path: /proj/bioinfo/users/x_nansh/data/uniprot/2014-11-05/hmmscan_cdd/cddfamseqdb_nr90/ 
    size: about 300 GB

    Method description:

        1). Create hmm database for CDD by the script
           "src/make_hmmdb_for_cdd.sh" in the repository.

        2). Search uniref100 (downloaded on 2014-11-05) sequences in database
           created in the first step, called cddhmm by hmmscan
           Argument for hmmscan is as follows:
           $ hmmscan -E 0.1 --domtblout $tmpoutfile --acc --noali --notextw \
             $target_cdd_hmm_dir/cdd.hmm $seqfile 1> /dev/null 2> $logfile

           scripts that have been used to submit jobs to tintin or triolith are 
           "src/divide_node_job_hmmscan.sh"
           "src/submit_hmmscan_cdd_uppmax.sh"

        3). Get UniprotID to CDDfam mapping table for any hit with e-value <=
           1e-3. Repeated domain hits are counted only once.
           script: "src/build_seqid2pfamid_from_hmmscan.py"

        4). Get PfamID to UniprotID mapping table from the UniprotID to PfamID
           mapping table.
           script "src/build_pfamid2seqid_fromseqid2pfamid.py"

        5). Generate FASTA seuqnece files for each family 

        6). Run CD-HIT to reduence the sequence redundancy to <90%.

        7). Create the database by "src/my_formatdb.py"
