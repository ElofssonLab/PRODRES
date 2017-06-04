import os
import re
from subprocess import call
import sys
import logging
import json
import sqlite3
import datetime

def COMMON_DOMAINS_REDUCTION(args, inp):

    # verbosity
    if args.verbosity != 0:
        def vprint(*args):
            for arg in args:
               print arg,
            print
    else:   
        vprint = lambda *a: None
    # end verbosity

    input_length = len(inp)
    counter = 1
    name = ""
    # one output directory every fasta seq
    for entry in inp:

        # time output stuff
        s_time = datetime.datetime.today()
        db_used = "pfam"
        
        #basic name handling
        if entry.id == "":
            name = "seq"+str(counter)
        elif entry.id == name:
            name= name+"+"
        else:
            try:
                regexp = re.search(r"\|([^\|]+)\|",entry.id) 
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
        vprint("\t>Beginning CDR for sequence number "+str(counter)+"/"+str(input_length)+": "+name[:8])
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

        if args.pfamscan_clan_overlap:
            pfamscan_args += ["-clan_overlap"]
        if args.pfamscan_e_val:
            pfamscan_args += ["-e_seq", args.pfamscan_e_val]
        elif args.pfamscan_bitscore:
            pfamscan_args += ["-b_seq", args.pfamscan_bitscore]
        pfamscan_args += ["-fasta", input_file]
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
        pfam_seq_db = args.pfam_dir +"/prodres_db.nr100.sqlite3"

        # handling the Pfam DB
        createHitDB(list(set(pfamList)), tempdir, pfam_seq_db)

        #  PERFORMING JACKHMMER
        if args.second_search == "jackhmmer":
            outfile = outputdir + "/tableOut.txt"
            dbfile = tempdir + "/QUERY.hits.db"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if (os.path.getsize(dbfile) == 0 and args.paramK) or args.force_fallback:
                vprint("WARNING! CDR database is empty, performing search in full DB")
                logging.warning("\t\t\t>CDR database found empty, searching in full DB")
                dbfile = args.fallback_db_fasta
                db_used = "uniref"
            aligfile = outputdir + "/Alignment.txt"
            fullout = outputdir + "/fullOut.txt"
            hmmfile = tempdir + "hmmOut"

            jackhmmer_args = []
            jackhmmer_args += ["-N", str(args.jackhmmer_max_iter)]
            jackhmmer_args += ["-o", fullout]

            if (args.jackhmmer_threshold_type == "bit-score"):
                jackhmmer_args += ["--incT", str(args.jackhmmer_bit_score)]
            elif (args.jackhmmer_threshold_type == "e-value"):
                jackhmmer_args += ["--incE", str(args.jackhmmer_e_val)]
            else:
                raise RuntimeError("Programming error. Unknown --jackhmmer-threshold-type value")

            jackhmmer_args += ["--tblout", outfile]
            jackhmmer_args += ["-A", aligfile]
            jackhmmer_args += ["-Z", str(args.pfam_database_dimension)]
            jackhmmer_args += ["--chkhmm", hmmfile]
            if args.threads:
                jackhmmer_args += ["--cpu", args.threads]
            jackhmmer_args += [input_file]
            jackhmmer_args += [dbfile]

            jackhmmer_cmd = ["jackhmmer"] + jackhmmer_args
            logging.info("\t\t\t> running jackhmmer search: {}".format(" ".join(jackhmmer_cmd)))
            # JACKHMMER CALL
            call(jackhmmer_cmd)
            # JACKHMMER OUTPUT TEST
            if os.path.exists(hmmfile + "-{}.hmm".format(args.jackhmmer_max_iter)):
                os.system("cp " + hmmfile + "-{}.hmm ".format(args.jackhmmer_max_iter) + outputdir+"hmmOut.txt")
            # JACKHMMER SECOND FALLBACK FULL RUN
            elif args.paramK and jackhmmer_args[-1] != args.fallback_db_fasta:
                logging.info("\t\t\t> Warning, no output found... proceeding with search on full DB")
                db_used = "uniref"
                del(jackhmmer_args[-1])
                jackhmmer_args += [args.fallback_db_fasta]
                jackhmmer_cmd = ["jackhmmer"] + jackhmmer_args
                call(jackhmmer_cmd)
            vprint("\t\t>end")

        # PERFORMING PSIBLAST
        elif args.second_search == "psiblast":
            # prepare db
            dbfile = tempdir + "/QUERY.hits.db"
            # TEST FOR EXISTANCE OF A DB, IF FALSE, SEARCH ON FULL DB
            if (os.path.getsize(dbfile) == 0 and args.paramK) or args.force_fallback:
                dbfile = args.fallback_db_fasta
                vprint("WARNING! CDR database is empty or Pfamscan is not working, performing search in full DB")
                logging.warning("\t\t\t>CDR database found empty, searching in full DB")
                db_used = "uniref"
            else:
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
            if args.psiblast_outfmt != None:
                psiblast_args += ["-outfmt", args.psiblast_outfmt]
            if args.threads:
                psiblast_args += ["-num_threads", args.threads]

            psiblast_cmd = ["psiblast"] + psiblast_args
            psiblast_cmd_str = " ".join(psiblast_cmd)
            vprint("\t>performing>>"+ psiblast_cmd_str)
            logging.info("\t\t\t> running psiblast search: {}".format(psiblast_cmd_str))
            # PSIBLAST CALL
            call(psiblast_cmd)
            # PSIBLAST OUTPUT TEST
            if "***** No hits found *****" in "".join(open(outfile).readlines()) and args.paramK:
                logging.info("\t\t\t> Warning, no output found... proceeding with search on full DB")
                db_used = "uniref"
                indb = psiblast_cmd.index("-db")
                dbfile = args.fallback_db_fasta
                psiblast_cmd[indb+1] = dbfile
                call(psiblast_cmd)
            vprint("\t\t>end")
        else:
            raise RuntimeError("unknown option value of --second-search")
        # time output
        e_time = datetime.datetime.today()
        with open(namedir + "time.txt","w") as timefile:
            timefile.write("0;{};{}".format((e_time-s_time).total_seconds(),db_used))

def createHitDB(pfamList, work_dir,pfamseqdb):
    logging.info("\t\t\t> constructing CDR database")
    try:
        prodres_db = pfamseqdb
        pfamidlist = pfamList
    except IndexError:
        print "usage: %s prodresdb pfamid [pfamid ...] "%(sys.argv[0])
        sys.exit(1)

    with open(work_dir + "QUERY.hits.db", "w") as fpout:
        tablename = "db"
        con = sqlite3.connect(prodres_db)
        with con:
            cur = con.cursor()
            seqidset = set([])
            for pfamid in pfamidlist:
                cmd = "SELECT Seq FROM %s WHERE AC = \"%s\""%(tablename, pfamid)
                cur.execute(cmd)
                rows = cur.fetchall()
                for row in rows:
                    seqdict = json.loads(row[0])
                    for seqid in seqdict:
                        if not seqid in seqidset:
                            seqidset.add(seqid)
                            fpout.write(">%s\n%s\n"%(seqdict[seqid][0],seqdict[seqid][1]))
