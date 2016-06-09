import os
from subprocess import call
import sys
sys.path.append("./database_handling/")
import myfunc   # Nanjiang scripts

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
            name = entry.id

        #specific entry outdir
        outdir= env.output_folder + "/" + entry.id + "/"
        if os.path.exists(outdir) is False:
            os.mkdir(outdir)

        # recursive report
        print("\t>Beginning CDR for sequence number "+str(counter)+"/"+str(input_length)+": "+name[:8])
        counter += 1

        # single query file in output folder
        with open(outdir+"/query.fa","w") as queryfile:
            queryfile.write(">" + str(entry.id) + "\n" + str(entry.seq))
        input_file = outdir+"/query.fa"

        #PFAMSCAN
        pfam_output = outdir + "/" + name + "_pfamscan.txt"

        # DELETE previous calculations
        if os.path.exists(pfam_output):
            os.system("rm "+pfam_output)

        Eval_tr,Clan_overlap = env.param_pfamscan
        pfamscan_cmd = "perl " + env.pfamscan + Clan_overlap + " -e_seq " + Eval_tr + " -fasta " + \
                       input_file + " -dir " + env.pfam + " -outfile " + pfam_output

        os.system(pfamscan_cmd)

        #READ PFAMSCAN OUTPUT
        pfamList = []
        pattern = "# <seq id> <alignment start> <alignment end> <envelope start> <envelope end> <hmm acc> <hmm name> <type> <hmm start> <hmm end> <hmm length> <bit score> <E-value> <significance> <clan>"
        bFoundStart = False
        with open(outdir + name + "_pfamscan.txt") as inFile:
            for line in inFile:
                if line.find(pattern) != -1:
                    bFoundStart = True
                if bFoundStart is True:
                    pos = line.find("PF")
                    if pos != -1:
                        pfamList.append(line[pos:pos + 7])
        pfam_seq_db = env.pfam+"/pfamfull/uniref100.pfam27.pfamseq.nr90"

        # Nanjiang script for handling the Pfam DB
        createHitDB(list(set(pfamList)), outdir,pfam_seq_db)

        os.system("rm " + outdir + "QUERY.hits.db.temp")  # remove this if you want to check temp db, but I remember I did already back in the time when I was young

        #PERFORMING JACKHMMER / PSIBLAST
        if env.jackhmmer:
            outfile = outdir + "/tableOut.txt"
            dbfile = outdir + "/QUERY.hits.db"
            aligfile = outdir + "/Alignment.txt"
            fullout = outdir + "/fullOut.txt "
            NofIter,threshold = env.param_jackhmmer
            #chkhmm = outdir + "/fastHMM/fastHMMiter"   option to have results each iteration

            jackhmmer_cmd = "jackhmmer -N " + NofIter + " --noali -o " + fullout + threshold + "--tblout " + \
                outfile + " -A " + aligfile + " -Z " + env.dbdimension + " " + input_file + " " + dbfile
            #print jackhmmer_cmd
            print("\t\t>details on jackhmmer that I am doing and are topsecret")
            os.system(jackhmmer_cmd)
            print("\t\t>end of details")





def createHitDB(pfamList, work_dir,pfamseqdb):
    hdl = myfunc.MyDB(pfamseqdb)
    if hdl.failure:
        #        print "Error"
        return 1
    with open(work_dir + "QUERY.hits.db.temp", "w") as outFile:
        for pfamid in pfamList:
            record = hdl.GetRecord(pfamid)
            if record:
                outFile.write(record)
        hdl.close()

    os.system("python database_handling/my_uniqueseq.py " + work_dir + "QUERY.hits.db.temp")
