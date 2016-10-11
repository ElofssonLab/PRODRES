import os
import re
from subprocess import call
import sys
sys.path.append("./database_handling/")
import myfunc
import logging

def COMMON_DOMAINS_REDUCTION(env,inp):

    input_length = len(inp)
    counter = 1
    name = ""
    # one output directory every fasta seq
    for entry in inp:
        #basic name handling
        if entry.id == "":
            name = "seq"+str(counter)
        elif entry.id == name:
            name= name+"+"
        else:
            try:
                regexp = re.search(r"\|([^\|]+)\|",entry.id) # for names like tr|Q8XP35|Q8XP35_CLOPE/tr|Q8XP35|Q8XP35_CLOPE
                name = regexp.group(1)
            except AttributeError:
                name = entry.id

        logging.info("\t\t> WORKING ON: {}".format(name))

        #specific entry outdir
        namedir= env.output_folder + "/" + name + "/"
        if not os.path.exists(namedir):
            os.mkdir(namedir)

        # adding temp and output subfolder
        tempdir = namedir+"temp/"
        outputdir = namedir+"outputs/"
        if not os.path.exists(tempdir):
            os.mkdir(tempdir)
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)

        # recursive report
        print("\t>Beginning CDR for sequence number "+str(counter)+"/"+str(input_length)+": "+name[:8])
        counter += 1

        # single query file in output folder
        with open(tempdir+"/query.fa","w") as queryfile:
            queryfile.write(">" + str(name) + "\n" + str(entry.seq))
        input_file = tempdir+"/query.fa"

        #PFAMSCAN
        pfam_output = tempdir + "/" + name + "_pfamscan.txt"

        # DELETE previous calculations
        if os.path.exists(pfam_output):
            os.system("rm "+pfam_output)

        Eval_tr,Clan_overlap = env.param_pfamscan
        pfamscan_cmd = "perl " + env.pfamscan + Clan_overlap + " -e_seq " + Eval_tr + " -fasta " + \
                       input_file + " -dir " + env.pfam + " -outfile " + pfam_output
        logging.info("\t\t\t> running pfamscan.pl: {}".format(pfamscan_cmd))
        os.system(pfamscan_cmd)

        #READ PFAMSCAN OUTPUT
        pfamList = []
        pattern = "# <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>"
        bFoundStart = False
        with open(tempdir + name + "_pfamscan.txt") as inFile:
            for line in inFile:
                if line.find(pattern) != -1:
                    bFoundStart = True
                if bFoundStart is True:
                    pos = line.find("PF")
                    if pos != -1:
                        pfamList.append(line[pos:pos + 7])
        pfam_seq_db = env.pfam+"/pfamfull/uniref100.pfam27.pfamseq.nr90"

        # handling the Pfam DB
        createHitDB(list(set(pfamList)), tempdir, pfam_seq_db)

        os.system("rm " + tempdir + "QUERY.hits.db.temp")  # remove this if you want to check temp db, but I remember I did already back in the time when I was young

        #  PERFORMING JACKHMMER
        if env.jackhmmer:
            outfile = outputdir + "/tableOut.txt"
            dbfile = tempdir + "/QUERY.hits.db"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if os.path.getsize(dbfile) == 0 and env.paramK:
                print("WARNING! CDR database is void, performing search in full DB")
                logging.warning("\t\t\t>CDR database found void, searching in full DB")
                dbfile = env.uniprot
            aligfile = outputdir + "/Alignment.txt"
            fullout = outputdir + "/fullOut.txt "
            hmmfile = tempdir + "hmmOut"
            NofIter,threshold = env.param_jackhmmer

            jackhmmer_cmd = "jackhmmer -N " + NofIter + " --noali -o " + fullout + threshold + "--tblout " + \
                        outfile + " -A " + aligfile + " -Z " + env.dbdimension + " --chkhmm " + hmmfile + " " + \
                        input_file + " " + dbfile
            logging.info("\t\t\t> running jackhmmer search: {}".format(jackhmmer_cmd))
            os.system(jackhmmer_cmd)
            os.system("cp " + hmmfile + "-3.hmm " + outputdir+"hmmOut.txt")
            print("\t\t>end")

        # PERFORMING PSIBLAST
        if env.psiblast:

            # prepare db
            dbfile = tempdir + "/QUERY.hits.db"
            os.system("makeblastdb -in " + dbfile + " -out " + dbfile + ".blastdb -dbtype prot")
            dbfile += ".blastdb"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if os.path.exists(dbfile+".psq") == False and env.paramK:
                dbfile = env.uniprot
                print("WARNING! CDR database is void, performing search in full DB")
                logging.warning("\t\t\t>CDR database found void, searching in full DB")
            # prepare other param
            outfile = outputdir + "/psiOutput.txt "
            pssmfile = outputdir + "/psiPSSM.txt "
            NofIter, threshold, out_type = env.param_psiblast

            psiblast_cmd = "psiblast -num_iterations " + NofIter + " -out " + outfile + threshold +\
                           " -dbsize " + env.dbdimension + " out_ascii_pssm "+pssmfile+" -query " + input_file + " -db " + dbfile
            print("\t>performing>>"+psiblast_cmd)
            logging.info("\t\t\t> running psiblast search: {}".format(psiblast_cmd))
            os.system(psiblast_cmd)
            print("\t\t>end")

def createHitDB(pfamList, work_dir,pfamseqdb):
    logging.info("\t\t\t> constructing CDR database")
    hdl = myfunc.MyDB(pfamseqdb)
    if hdl.failure:
        return 1
    with open(work_dir + "QUERY.hits.db.temp", "w") as outFile:
        for pfamid in pfamList:
            record = hdl.GetRecord(pfamid)
            if record:
                outFile.write(record)
        hdl.close()

    os.system("python database_handling/my_uniqueseq.py " + work_dir + "QUERY.hits.db.temp")