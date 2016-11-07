import os
import re
from subprocess import call
import sys
sys.path.append("./database_handling/")
import myfunc
import logging


def COMMON_DOMAINS_REDUCTION(args, inp):

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
        namedir= args.output + "/" + name + "/"
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

        pfamscan_args = []

        if args.pfamscan_clan_overlap == True:
            pfamscan_args += ["-clan_overlap"]
        if args.pfamscan_bitscore:
            pfamscan_args += ["-b_seq", args.pfamscan_bitscore]
        else:
            pfamscan_args += ["-e_seq", args.pfamscan_e_val]
        pfamscan_args += ["-fasta", args.input_file]
        pfamscan_args += ["-dir", args.pfam_dir]

        pfamscan_cmd = [args.pfamscan_script] + pfamscan_args

        logging.info("\t\t\t> running pfamscan.pl: {}".format(" ".join(pfamscan_cmd)))
        with open(pfam_output, "w") as outfile:
            call(pfamscan_cmd, stdout=outfile)

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
        pfam_seq_db = args.pfam_dir +"/pfamfull/uniref100.pfam27.pfamseq.nr90"

        # handling the Pfam DB
        createHitDB(list(set(pfamList)), tempdir, pfam_seq_db)

        os.system("rm " + tempdir + "QUERY.hits.db.temp")  # remove this if you want to check temp db, but I remember I did already back in the time when I was young

        #  PERFORMING JACKHMMER
        if args.second_search == "jackhmmer":
            outfile = outputdir + "/tableOut.txt"
            dbfile = tempdir + "/QUERY.hits.db"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if os.path.getsize(dbfile) == 0 and args.paramK:
                print("WARNING! CDR database is void, performing search in full DB")
                logging.warning("\t\t\t>CDR database found void, searching in full DB")
                dbfile = args.uniprot_db_fasta
            aligfile = outputdir + "/Alignment.txt"
            fullout = outputdir + "/fullOut.txt"
            hmmfile = tempdir + "hmmOut"

            jackhmmer_args = []
            jackhmmer_args += ["-N", str(args.jackhmmer_max_iter)]
            jackhmmer_args += ["-o", fullout]

            if (args.jackhmmer_threshold_type == "bit-score"):
                jackhmmer_args += ["--incT", str(args.jackhmmer_bitscore)]
            elif (args.jackhmmer_threshold_type == "e-value"):
                jackhmmer_args += ["--incE", str(args.jackhmmer_e_val)]
            else:
                raise RuntimeError("Programming error. Unknown --jackhmmer-threshold-type value")

            jackhmmer_args += ["--tblout", outfile]
            jackhmmer_args += ["-A", aligfile]
            jackhmmer_args += ["-Z", str(args.pfam_database_dimension)]
            jackhmmer_args += ["--chkhmm", hmmfile]
            jackhmmer_args += [input_file]
            jackhmmer_args += [dbfile]

            jackhmmer_cmd = ["jackhmmer"] + jackhmmer_args
            logging.info("\t\t\t> running jackhmmer search: {}".format(" ".join(jackhmmer_cmd)))
            # JACKHMMER CALL
            call(jackhmmer_cmd)
            # JACKHMMER OUTPUT TEST
            if os.path.exists(hmmfile + "-3.hmm"):
                os.system("cp " + hmmfile + "-3.hmm " + outputdir+"hmmOut.txt")
            # JACKHMMER SECOND FALLBACK FULL RUN
            elif args.paramK and jackhmmer_args[-1] != args.uniprot_db_fasta:
                logging.info("\t\t\t> Warning, no output found... proceeding with search on full DB")
                del(jackhmmer_args[-1])
                jackhmmer_args += [args.uniprot_db_fasta]
                jackhmmer_cmd = ["jackhmmer"] + jackhmmer_args
                call(jackhmmer_cmd)
            print("\t\t>end")

        # PERFORMING PSIBLAST
        elif args.second_search == "psiblast":
            # prepare db
            dbfile = tempdir + "/QUERY.hits.db"
            os.system("makeblastdb -in " + dbfile + " -out " + dbfile + ".blastdb -dbtype prot")
            dbfile += ".blastdb"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if os.path.exists(dbfile+".psq") == False and args.paramK:
                dbfile = args.uniprot_db_fasta
                print("WARNING! CDR database is void, performing search in full DB")
                logging.warning("\t\t\t>CDR database found void, searching in full DB")
                # PREPARING FALLBACK DATABASE
                if not os.path.exists(dbfile + ".blastdb.psq"):
                    os.system("makeblastdb -in " + dbfile + " -out " + dbfile + ".blastdb -dbtype prot")
                    dbfile += ".blastdb"
            # prepare other param
            outfile = outputdir + "/psiOutput.txt"
            pssmfile = outputdir + "/psiPSSM.txt"

            psiblast_args = []
            psiblast_args += ["-num_iterations", str(args.psiblast_iter)]
            psiblast_args += ["-out", outfile]
            psiblast_args += ["-evalue", args.psiblast_e_val]
            psiblast_args += ["-dbsize", str(args.pfam_database_dimension)]
            psiblast_args += ["-out_ascii_pssm", pssmfile]
            psiblast_args += ["-query", input_file]
            psiblast_args += ["-db", dbfile]
            if (args.psiblast_outfmt != None):
                psiblast_args += ["-outfmt", args.psiblast_outfmt]
            psiblast_cmd = ["psiblast"] + psiblast_args
            psiblast_cmd_str = " ".join(psiblast_cmd)
            print("\t>performing>>"+ psiblast_cmd_str)
            logging.info("\t\t\t> running psiblast search: {}".format(psiblast_cmd_str))
            # PSIBLAST CALL
            call(psiblast_cmd)
            # PSIBLAST OUTPUT TEST
            if "***** No hits found *****" in "".join(open(outfile).readlines()) and paramK:
                logging.info("\t\t\t> Warning, no output found... proceeding with search on full DB")
                indb = psiblast_cmd.index("-db")
                dbfile = args.uniprot_db_fasta
                psiblast_cmd[indb+1] = dbfile+".blastdb"
                if not os.path.exists(dbfile + ".blastdb.psq"):
                    os.system("makeblastdb -in " + dbfile + " -out " + dbfile + ".blastdb -dbtype prot")
                call(psiblast_cmd)
            print("\t\t>end")
        else:
            raise RuntimeError("unknown option value of --second-search")

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
