#!/usr/bin/env python
# Description: build the pfam full sequence database
import sys
import re
import os
import shutil
import math
import tempfile
import myfunc
import subprocess
import time
#import yaml
import sqlite3
import gzip
#import cProfile

BLOCK_SIZE = 100000
MIN_FREE_DISK_SPACE_IN_GB = 160
url_pfam_uniprot_alnfile = "ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.full.uniprot.gz"
url_seqdb = "ftp://ftp.ebi.ac.uk/pub/databases/uniprot/previous_releases/"


# Description:
#   the database will be created under path_storage and then after success, a
#   symlink will be pointed to the outpath

# Get the version of Pfam from Pfam.version.gz and then get the version of uniprot
# database for which the Pfam database was created, use that uniprot database
# as sequence database



progname = os.path.basename(sys.argv[0])
usage="""
Usage: %s [OPTIONS] -outpath DIR -cdhit PATH

Description:
    build the database with full-length sequences for Pfam families
    Note that you will need at least %d GB of free storage to build the database,
    if alnfile and seqdb are not supplied

    The tablenames for all databases are \"db\"

    The result will be output to $outpath/pfamfullseqdb.nr${cutoff}.sqlite3

OPTIONS:
  -outpath   DIR     Set the path to output the result.
  -alnfile   FILE    Set the file containing the alignment of all families (gzipped).
                     If not supplied, the program will try to download it from
                     %s
  -seqdbname DBNAME  Set the database name for full-length sequences, if not supplied, 
                     the program will download it from 
                     %s
                     and build it with both uniprot_trembl and uniprot_sprot databases
  -storage   DIR     Path to large storage (with %d GB free space) 
                     if alnfile and seqdb are not supplied
  -cutoff    INT     Sequence identity cutoff (percentages) within the family, (default: 90)
                     cd-hit is used to reduce the sequence redundancy
  -cdhit     PATH    Set the path where it contains cd-hit executable
  -verbose           Show verbose information
  -debug             Run in debug mode
  -h, --help         print this help message and exit

Created 2016-07-07, updated 2016-11-08, Nanjiang Shu

Examples:

    %s -outpath /data/pfamfullseqdb -cdhit ~/bin/cd-hit
"""%(progname, MIN_FREE_DISK_SPACE_IN_GB, url_pfam_uniprot_alnfile, url_seqdb, MIN_FREE_DISK_SPACE_IN_GB, progname)

def PrintHelp():
    print usage

def IsProgExist(cmd):#{{{
    return subprocess.call("type " + cmd, shell=True, 
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0#}}}

def GetCDHitWordSize(cutoff):#{{{
    if cutoff >=0.7:
        return 5
    elif cutoff >= 0.6:
        return 4
    elif cutoff >= 0.5:
        return 3
    elif cutoff >= 0.4:
        return 2
    else:
        return 2
#}}}
def Download_alnfile(path_storage):#{{{
# download the uniprot alignment database for pfam from
# ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.full.uniprot.gz
# when download the alnfile, get also the release information
    name_alnfile_zip = g_params['pfam_uniprot_alnfile']
    name_versionfile_zip = g_params['pfam_versionfile']
    name_relnote_zip = g_params['pfam_relnotefile']
    objAlnDB = {}
    objAlnDB['uniprot_version'] = ""
    objAlnDB['pfam_version'] = ""
    objAlnDB['alnfile'] = ""

    is_download_success = True
    for fname in [name_versionfile_zip, name_relnote_zip, name_alnfile_zip]:
        url_file = "%s/%s"%(g_params['pfam_ftp_url'], fname )
        outfile = "%s/%s"%(path_storage, fname)

        if os.path.exists(outfile) and g_params['nooverwrite']:
            continue

        if os.path.exists(outfile):
            try:
                os.remove(outfile)
            except:
                print >> sys.stderr, "Failed to delete the old file %s"%(outfile)
                return None

        cmd = ["wget", url_file, "-O", outfile]
        cmdline = " ".join(cmd)
        try:
            if g_params['verbose']:
                print "cmdline: %s"%(cmdline)
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            print >> sys.stderr, e
            print "cmdline: %s"%(cmdline)
            is_download_success = False

    if is_download_success:
        # get pfam version
        pfam_version = ""
        path_versionfile = "%s%s%s"%(path_storage, os.sep, name_versionfile_zip)
        try:
            fpin = gzip.open(path_versionfile, 'rb')
            line = fpin.readline()
            while line:
                if line.find("Pfam release") != -1:
                    try:
                        pfam_version = line.split(":")[1].strip()
                    except IndexError:
                        pass
                    break
                line = fpin.readline()
            fpin.close()
        except IOError:
            print >> sys.stderr, "Failed to read gzip file %s"%(path_versionfile)
            pass

        # get the uniprotKB version that was used to
        # generate this version of Pfam
        uniprot_version = ""
        path_relnotefile = "%s%s%s"%(path_storage, os.sep, name_relnote_zip)
        try:
            fpin = open(path_relnotefile, 'rb')
            line = fpin.readline()
            while line:
                m = re.search('%s.*Uniprot.*'%(pfam_version), line)
                if m:
                    uniprot_version = m.group(0).split()[-1]
                    break
                line = fpin.readline()
            fpin.close()
        except IOError:
            print >> sys.stderr, "Failed to read gzip file %s"%(path_relnotefile)
            pass


        objAlnDB['uniprot_version'] = uniprot_version
        objAlnDB['pfam_version'] = pfam_version
        objAlnDB['alnfile'] = "%s/%s"%(path_storage, name_alnfile_zip)

    return objAlnDB
#}}}
def Download_seqdb(path_storage, uniprot_version):#{{{
# download the uniprot full sequence database from
# e.g. url
    # ftp://ftp.ebi.ac.uk/pub/databases/uniprot/previous_releases/release-2016_02/knowledgebase/knowledgebase2016_02.tar.gz
    name_uniprot_trembl_datfile_zip = "uniprot_trembl.dat.gz"
    name_uniprot_sprot_datfile_zip = "uniprot_sprot.dat.gz"
    name_uniprotdb_zip = "knowledgebase%s.tar.gz"%(uniprot_version)
    baseurl = "%s/release-%s/knowledgebase"%(g_params['uniprot_ftp_url_old_release'], uniprot_version)
    path_uniprot_trembl_datfile_zip = "%s%s%s"%(path_storage, os.sep, name_uniprot_trembl_datfile_zip)
    path_uniprot_sprot_datfile_zip = "%s%s%s"%(path_storage, os.sep, name_uniprot_sprot_datfile_zip)
    objSeqDB = {}
    objSeqDB['uniprot_trembl_datfile_zip'] = ""
    objSeqDB['uniprot_sprot_datfile_zip'] = ""

    if os.path.exists(path_uniprot_trembl_datfile_zip) and os.path.exists(path_uniprot_sprot_datfile_zip) and g_params['nooverwrite']:
        objSeqDB['uniprot_trembl_datfile_zip'] = path_uniprot_trembl_datfile_zip
        objSeqDB['uniprot_sprot_datfile_zip'] = path_uniprot_sprot_datfile_zip
        return objSeqDB

    is_download_success = True
    for fname in [name_uniprotdb_zip]:
        url_file = "%s/%s"%(baseurl, fname )
        outfile = "%s/%s"%(path_storage, fname)

        if os.path.exists(outfile) and g_params['nooverwrite']:
            if g_params['verbose']:
                print "File %s already exists, skip downloading."%(outfile)
            continue

        if os.path.exists(outfile):
            try:
                os.remove(outfile)
            except:
                print >> sys.stderr, "Failed to delete the old file %s"%(outfile)
                return objSeqDB

        cmd = ["wget", url_file, "-O", outfile]
        cmdline = " ".join(cmd)
        if g_params['verbose']:
            print "cmdline: %s\n"%(cmdline)

        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError, e:
            print >> sys.stderr, e
            print "cmdline: %s"%(cmdline)
            is_download_success = False

    if is_download_success:
        # extract the file
        path_uniprotdb = "%s%s%s"%(path_storage, os.sep, name_uniprotdb_zip)
        for datfile in [path_uniprot_trembl_datfile_zip, path_uniprot_sprot_datfile_zip]:
            if os.path.exists(datfile):
                try:
                    os.remove(datfile)
                except:
                    print >> sys.stderr, "Failed to delete the old file %s"%(datfile)
                    return objSeqDB

        is_run_tar_success = False
        cmd = ["tar", "-xvzf", path_uniprotdb, "-C", path_storage]
        cmdline = " ".join(cmd)
        try:
            subprocess.check_call(cmd)
            if g_params['verbose']:
                print "cmdline: %s"%(cmdline)
            is_run_tar_success = True
        except subprocess.CalledProcessError, e:
            print >> sys.stderr, e
            print "cmdline: %s"%(cmdline)
        if is_run_tar_success and os.path.exists(path_uniprot_trembl_datfile_zip) and os.path.exists(path_uniprot_sprot_datfile_zip):
            objSeqDB['uniprot_trembl_datfile_zip'] = path_uniprot_trembl_datfile_zip
            objSeqDB['uniprot_sprot_datfile_zip'] = path_uniprot_sprot_datfile_zip
    return objSeqDB
#}}}
def CreateSeqDB_sqlite(uniprot_trembl_datfile, uniprot_sprot_datfile, isQuiet=False): #{{{
# create sequence database using sqlite
# return (dbname, tablename) on success
# return ("","") on failure
# note that uniprot_datfile can be in text format or gzip format
# write a file containing all aclist
    rootname_file = os.path.basename(os.path.splitext(uniprot_trembl_datfile)[0])
    rootname_file = rootname_file.rstrip(".dat")
    dirname_file = os.path.dirname(uniprot_trembl_datfile)
    tablename = "db"
    tablename_stat = "stat"
    dbname = "%s%s%s.fasta.sqlite3"%(dirname_file, os.sep, rootname_file)
    out_aclistfile = "%s%s%s.aclist"%(dirname_file, os.sep, rootname_file)


    dbname_journal = "%s-journal" %(dbname)
    if os.path.exists(dbname) and not os.path.exists(dbname_journal) and g_params['nooverwrite']:
        return (dbname, tablename)

    cntseq = 0
    try:
        con = sqlite3.connect(dbname)
    except:
        raise

    with con:
        fpout_aclist = myfunc.myopen(out_aclistfile, None, "w", False)
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS %s
            (
                AC VARCHAR(25),
                Desp VARCHAR(1000),
                Seq VARCHAR(30000),
                PRIMARY KEY (AC)
            )"""%(tablename))

        cur.execute("""
            CREATE TABLE IF NOT EXISTS %s
            (
                Numseq INTEGER,
                AC_longest VARCHAR(100),
                Length_longest INTEGER,
                AC_shortest VARCHAR(100),
                Length_shortest INTEGER,
                PRIMARY KEY (Numseq)
            )"""%(tablename_stat))

        seq_longest = {}
        seq_shortest = {}
        seq_longest['length'] = 0
        seq_longest['ac'] = ""
        seq_shortest['length'] = sys.maxint
        seq_shortest['ac'] = ""


        for datfile in [uniprot_trembl_datfile, uniprot_sprot_datfile]:
            if g_params['verbose']:
                print "Adding %s to %s."%(datfile, dbname)
            hdl = myfunc.ReadUniprotDatByBlock(datfile)
            if hdl.failure:
                return ("","")
            recordList = hdl.readseq()
            while recordList != None:
                for rd in recordList:
# using ignore to avoid duplications
                    if len(rd['aclist']) > 0:
                        cntseq += 1
                        if rd['length'] > seq_longest['length']:
                            seq_longest['length'] = rd['length']
                            seq_longest['ac'] = ";".join(rd['aclist'])
                        if rd['length'] < seq_shortest['length']:
                            seq_shortest['length'] = rd['length']
                            seq_shortest['ac'] = ";".join(rd['aclist'])
                        if fpout_aclist:
                            fpout_aclist.write("%s\n"%(";".join(rd['aclist'])))
                        seqid = rd['aclist'][0]
                        description = rd['sequence_definition']
                        seq = rd['seq']
                        cmd =  "INSERT OR IGNORE INTO %s(AC,  Desp, Seq) VALUES('%s', '%s',  '%s')"%(tablename, seqid.replace("'","''"), description.replace("'","''"), seq.replace("'","''"))

                        cur.execute(cmd)
                        if g_params['verbose']:
                            if cntseq % 5000 == 0:
                                print "\tAdding sequence %d"%(cntseq)

                recordList = hdl.readseq()
            hdl.close()


        myfunc.myclose(fpout_aclist)
        numseq = cntseq

        cmd =  "INSERT OR IGNORE INTO %s(Numseq,  AC_longest, Length_longest, AC_shortest, Length_shortest) VALUES('%s', '%s',  '%d', '%s', '%d')"%(tablename_stat, numseq, seq_longest['ac'].replace("'","''"), seq_longest['length'], seq_shortest['ac'].replace("'","''"), seq_shortest['length'])
        cur.execute(cmd)


        if not isQuiet:
            print "SQLite database \"%s\" with tablename \"%s\" containing %d sequences created"%(dbname, tablename, numseq)

        return (dbname, tablename)

#}}}
def WriteFullSequence_old(cur, tablename, seqidset, out_fullseqfile):#{{{
    fpout = open(out_fullseqfile, "w")
    print "Write file %s"%(out_fullseqfile)
    cnt = 0
    for seqid in seqidset:
        cnt += 1
        if cnt%500==0:
            print "\t%d"%(cnt)
        cmd =  "SELECT AC, Desp, Seq FROM %s WHERE AC =  \"%s\""%(tablename, seqid)
        #print cmd
        cur.execute(cmd)
        rows = cur.fetchall()
        for row in rows:
            fpout.write(">%s\n%s"%(row[1],row[2]))
    fpout.close()
#}}}
def WriteFullSequence_old2(cur, tablename, seqidset, out_fullseqfile):#{{{
    fpout = open(out_fullseqfile, "w")
    print "Write file %s"%(out_fullseqfile)
    cnt = 0
    li = ["\"%s\""%(seqid) for seqid in seqidset]
    cmd =  "SELECT Desp, Seq FROM %s WHERE AC in (%s) "%(tablename, ",".join(li))
    #print cmd
    cur.execute(cmd)
    rows = cur.fetchall()
#     print rows
    nRow = len(rows)
    for i in xrange(nRow):
        (desp, seq) = rows[i]
        fpout.write(">%s\n%s\n"%(desp, seq))
    fpout.close()
#}}}
def WriteFullSequence(cur, tablename, seqidset, out_fullseqfile):#{{{
# the sqlite3 statement should not be too long, therefore, set the maximum
# number of ACs in each select statement
# return the retrieved_seqidset
    maxNumAC = 500
    fpout = open(out_fullseqfile, "w")
    print "Write file %s"%(out_fullseqfile)
    cnt = 0
    li = ["\"%s\""%(seqid) for seqid in seqidset]
    numSeqID = len(li)

    retrieved_seqidset = set([])

    idx = 0
    while idx < numSeqID:
        beg = idx
        end = idx+maxNumAC
        cmd =  "SELECT AC, Desp, Seq FROM %s WHERE AC in (%s) "%(tablename, ",".join(li[beg:end]))
        if g_params['verbose']:
            print "\tSELECT ACs %d:%d"%(beg, end)
        #print cmd
        cur.execute(cmd)
        rows = cur.fetchall()
#     print rows
        nRow = len(rows)
        for i in xrange(nRow):
            (ac, desp, seq) = rows[i]
            fpout.write(">%s\n%s\n"%(desp, seq))
            retrieved_seqidset.add(ac)
        idx += maxNumAC

    fpout.close()

    return retrieved_seqidset
#}}}
def ReadPfamRecord_withoutseq(pfamRecord):#{{{
#Read the PfamRecord but do not read the aligned sequence
    record = {}
    record['seqidset'] = set([]) #seqID e.g.   I6TG11
    record['alnidlist'] = [] #alnID e.g.   I6TG11.1/79-213

    lines = pfamRecord.split("\n")
    for line in lines:
        if not line:
            continue
        if line[0] == "#":
            if line.find("#=GF ID") == 0:
                record['id']=line.split()[2]
            elif line.find("#=GF AC") == 0:
                record['ac']=line.split()[2].split('.')[0]
            elif line.find("#=GF DE") == 0:
                record['def']=line[8:].strip()
            elif line.find("#=GF SQ") == 0:
                record['numseq']=int(line.split()[2])
        elif line != "//": 
            alnID = myfunc.GetFirstWord(line)
            seqID = alnID.split("/")[0].split(".")[0]
            record['alnidlist'].append(alnID)
            record['seqidset'].add(seqID)
    if record['numseq'] != len(record['alnidlist']):
        print >> sys.stderr, "GF SQ=%d != numseq in the record %d for id %s"%(record['numseq'], len(record['alnidlist']), record['id'])
    return record
#}}}

def ReadNextPfamRecord(fpin,oldbuff):#{{{
    pfamRecord = ""
    newbuff = ""
    endpos = oldbuff.find("\n//")
    while endpos < 0:
        tmpbuff = fpin.read(BLOCK_SIZE)
        if not tmpbuff:
            break
        oldbuff += tmpbuff
        endpos = oldbuff.find("\n//")
    pfamRecord = oldbuff[:endpos+4]
    newbuff = oldbuff[endpos+4:]
    return (pfamRecord, newbuff)
#}}}

def CreatePfamFullseqDB(alnfile, seqidt_cutoff, seqdbname, seqtablename, outdb):#{{{

    outpath = os.path.dirname(outdb)
    tmpdir = tempfile.mkdtemp(prefix="tmp_", dir=outpath)

    con_seqdb = sqlite3.connect(seqdbname)
    con_pfamdb = sqlite3.connect(outdb)
    cur_seqdb = con_seqdb.cursor()
    cur_pfamdb = con_pfamdb.cursor()
    pfamdb_tablename = "db"
    pfamdb_tablename_stat = "stat"

# AC is PfamID
# Desp is Definition of the family
# Seq is a dump of fasta sequences
    with con_pfamdb:  # using with con: syntax, the database will be commit() automatically
        # Numseq_aln: number of sequences in the pfam.uniprot.full
        # Numseq_uniqid: number of sequences with uniqid in the pfam.uniprot.full
        # Numseq_get: number of sequences retrieved by the uniprot AC in the alignment
        # Numseq_nr: number of sequences after redundancy removal, that is also
        #            the number of sequences of the Seq column
        cur_pfamdb.execute("""
            CREATE TABLE IF NOT EXISTS %s
            (
                AC VARCHAR(25),
                Desp VARCHAR(1000),
                Numseq_aln INTEGER,
                Numseq_uniqid INTEGER,
                Numseq_get INTEGER,
                Numseq_nr INTEGER,
                Seq VARCHAR(30000),
                PRIMARY KEY (AC)
            )"""%(pfamdb_tablename))
        cur_pfamdb.execute("""
            CREATE TABLE IF NOT EXISTS %s
            (
                Numfam INTEGER,
                Pfamid_biggest VARCHAR(100),
                Numseq_biggest INTEGER,
                Pfamid_smallest VARCHAR(100),
                Numseq_smallest INTEGER,
                PRIMARY KEY (Numfam)
            )"""%(pfamdb_tablename_stat))

        cntFam = 0
        fpin = None
        try:
            fpin = gzip.open(alnfile, "rb")
        except IOError:
            fpin = None
            print >> sys.stderr, "Failed to read gzip file %s."%(alnfile)
            return 1

        fam_biggest = {}
        fam_smallest = {}
        fam_biggest['numseq'] = 0
        fam_biggest['pfamid'] = ""
        fam_smallest['numseq'] = sys.maxint
        fam_smallest['pfamid'] = ""

        buff = ""
        (pfamRecord, buff) = ReadNextPfamRecord(fpin, buff)
        while pfamRecord:
            rd = ReadPfamRecord_withoutseq(pfamRecord)
            cntFam += 1

            if g_params['verbose']:
                print "No. %d: Building family: %s | numSeq = %d | len(seqidset) = %d"%(cntFam, rd['ac'], rd['numseq'], len(rd['seqidset']))

            out_fullseqfile = "%s%s%s.fasta"%(tmpdir, os.sep, rd['ac'])
            retrieved_seqidset = WriteFullSequence(cur_seqdb, seqtablename, rd['seqidset'], out_fullseqfile)
            numseq_retrieved = len(retrieved_seqidset)

            out_missingseqidfile = "%s%s%s.missing.seqidlist"%(tmpdir, os.sep, rd['ac'])
            missing_seqidset = rd['seqidset'] - retrieved_seqidset
            if g_params['debug']:
                myfunc.WriteFile("\n".join(list(missing_seqidset)), out_missingseqidfile, "w", True)

            if seqidt_cutoff <= 100:
# run sequence identity cutoff
                out_nrfullseqfile = "%s%s%s.nr%d.fasta"%(tmpdir, os.sep, rd['ac'], seqidt_cutoff)
                wordsize = GetCDHitWordSize(seqidt_cutoff/100.0)
# -T -0 using all CPUs
                cmd = [g_params['exec_cdhit'], "-i", out_fullseqfile, "-o", out_nrfullseqfile, "-c", str(seqidt_cutoff/100.0), "-n", str(wordsize), "-T", "0"]
                cmdline = " ".join(cmd)
                is_run_cdhit_success = False
                try:
                    subprocess.check_call(cmd)
                    is_run_cdhit_success = True
                except subprocess.CalledProcessError, e:
                    print >> sys.stderr, e
                    print "cmdline: %s"%(cmdline)
                if is_run_cdhit_success and os.path.exists(out_nrfullseqfile):
                    if g_params['verbose']:
                        numseq_nr = myfunc.CountFastaSeq(out_nrfullseqfile)
                        print "%d: family %s | numseq = %d | num_uniq_id = %d | num_missing_id = %d | num_get_seq = %d | num_nr_seq = %d" %(cntFam, rd['ac'], rd['numseq'], len(rd['seqidset']), len(missing_seqidset), numseq_retrieved, numseq_nr)
                        print "Family %s, missing idlist: %s " %(rd['ac'], " ".join(list(missing_seqidset)))

                    seqcontent = myfunc.ReadFile(out_nrfullseqfile)
                    cmd =  "INSERT OR IGNORE INTO %s(AC,  Desp, Numseq_aln, Numseq_uniqid, Numseq_get, Numseq_nr, Seq) VALUES('%s', '%s',  %d, %d, %d, %d, '%s') "%(pfamdb_tablename, rd['ac'], rd['def'].replace("'","''"), rd['numseq'], len(rd['seqidset']), numseq_retrieved, numseq_nr, seqcontent.replace("'","''"))
                    #print cmd
                    #print cur_pfamdb
                    cur_pfamdb.execute(cmd)

                    if numseq_nr > fam_biggest['numseq']:
                        fam_biggest['numseq'] = numseq_nr
                        fam_biggest['pfamid'] = rd['ac']
                    if numseq_nr < fam_smallest['numseq']:
                        fam_smallest['numseq'] = numseq_nr
                        fam_smallest['pfamid'] = rd['ac']


            if not g_params['debug']:
                try:
                    os.remove(out_fullseqfile)
                    os.remove(out_nrfullseqfile)
                    os.remove("%s.clstr"%(out_nrfullseqfile))
                    os.remove("%s.bak.clstr"%(out_nrfullseqfile))
                except:
                    pass
#                 if cntFam >= 5:
#                     break
            (pfamRecord, buff) = ReadNextPfamRecord(fpin, buff)

        if fpin != None:
            fpin.close()
        numFam = cntFam

        cmd =  "INSERT OR IGNORE INTO %s(Numfam,  Pfamid_biggest, Numseq_biggest, Pfamid_smallest, Numseq_smallest) VALUES('%s', '%s',  '%d', '%s', '%d')"%(pfamdb_tablename_stat, numFam, fam_biggest['pfamid'].replace("'","''"), fam_biggest['numseq'], fam_smallest['pfamid'].replace("'","''"), fam_smallest['numseq'])
        cur_pfamdb.execute(cmd)

    if not g_params['debug']:
        try:
            shutil.rmtree(tmpdir)
        except:
            pass
    else:
        print "temporary data are kept at %s"%(tmpdir)


    return 0
#}}}
def main(g_params):#{{{
    argv = sys.argv
    numArgv = len(argv)
    if numArgv < 2:
        PrintHelp()
        return 1

    outpath = ""
    alnfile = ""
    path_cdhit = ""
    pfam_version = "" #this version is along with the pfam version
    uniprot_version = ""
    seqdbname = ""
    seqtablename = "db"
    path_storage = ""
    seqidt_cutoff = 90

    i = 1
    isNonOptionArg=False
    while i < numArgv:
        if isNonOptionArg == True:
            fileList.append(argv[i])
            isNonOptionArg = False
            i += 1
        elif argv[i] == "--":
            isNonOptionArg = True
            i += 1
        elif argv[i][0] == "-":
            if argv[i] in ["-h", "--help"]:
                PrintHelp()
                return 1
            elif argv[i] in ["-outpath", "--outpath"]:
                (outpath, i) = myfunc.my_getopt_str(argv, i)
            elif argv[i] in ["-alnfile", "--alnfile"] :
                (alnfile, i) = myfunc.my_getopt_str(argv, i)
            elif argv[i] in ["-seqdbname", "--seqdbname"] :
                (seqdbname, i) = myfunc.my_getopt_str(argv, i)
            elif argv[i] in ["-storage", "--storage"] :
                (path_storage, i) = myfunc.my_getopt_str(argv, i)
            elif argv[i] in ["-cutoff", "--cutoff"] :
                (seqidt_cutoff, i) = myfunc.my_getopt_int(argv, i)
            elif argv[i] in ["-cdhit", "--cdhit"] :
                (path_cdhit, i) = myfunc.my_getopt_str(argv, i)
            elif argv[i] in ["-q", "--q"]:
                g_params['isQuiet'] = True
                i += 1
            elif argv[i] in ["-verbose", "--verbose"]:
                g_params['verbose'] = True
                i += 1
            elif argv[i] in ["-nooverwrite", "--nooverwrite"]:
                g_params['nooverwrite'] = True
                i += 1
            elif argv[i] in ["-debug", "--debug"]:
                g_params['debug'] = True
                i += 1
            else:
                print >> sys.stderr, "Error! Wrong argument:", argv[i]
                return 1
        else:
            print >> sys.stderr, "Error! Wrong argument:", argv[i]
            return 1

    if g_params['verbose']:
        full_cmdline = " ".join(sys.argv[:])
        print "Program starts at: %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        print "command-line: %s\n"%(full_cmdline)
#===============================================================
# check if arguments are properly set
#===============================================================
    if path_storage != "":
        if not os.path.exists(path_storage):
            try:
                os.makedirs(path_storage)
            except OSError:
                print sys.stderr, "Failed to create path_storage %s. Exit"%(path_storage)
                return 1

        # trying to get the free disk space for path_storage
        try:
            os.statvfs(path_storage)
        except OSError:
            print sys.stderr, "Failed to get status of path_storage %s. Exit"%(path_storage)
            return 1
        path_storage = os.path.realpath(path_storage)


    if seqidt_cutoff > 100 or seqidt_cutoff < 50:
        print >> sys.stderr, "Wrong seqidt_cutoff=%d is set. seqidt_cutoff should be in the range [50,100]. Exit!"%(seqidt_cutoff)
        return 1

    if outpath == "":
        print >> sys.stderr, "outpath not set. Exit!"
        return 1

    if path_cdhit == "":
        print >> sys.stderr, "path_cdhit not set. Exit!"
        return 1
    elif not IsProgExist("%s%scd-hit"%(path_cdhit, os.sep)):
        print >> sys.stderr, "path_cdhit is set, but %s does not exist or not executable. Exit!"%("%s/cd-hit"%(path_cdhit))
        return 1
    else:
        g_params['exec_cdhit'] = "%s%scd-hit"%(path_cdhit, os.sep)

#========================================================
# Download the pfam uniprot alignment database if not exists
#========================================================
    objAlnDB = {}
    if alnfile == "":
        if not g_params['isQuiet']:
            print "alnfile not supplied, trying to download from %s"%(url_pfam_uniprot_alnfile)
            print "\nThis takes a while, please be patient\n"
        if path_storage == "":
            print sys.stderr, "path_storage is not set while alnfile needs to be downloaded. Exit."
            return 1
        (b_total, b_used, b_free) = myfunc.disk_usage(path_storage)
        if b_free < 0 or b_free/1024.0/1024.0/1024.0 < MIN_FREE_DISK_SPACE_IN_GB:
            print >> sys.stderr, "There is not enough free disk space at %s. Exit!"%(path_storage)
            return 1
        objAlnDB = Download_alnfile(path_storage)
        if g_params['verbose']:
            print "objAlnDB=",objAlnDB
        if objAlnDB['alnfile'] != "" and objAlnDB['pfam_version'] != "" and objAlnDB['uniprot_version'] != "":
            alnfile = objAlnDB['alnfile']
            pfam_version = objAlnDB['pfam_version']
            uniprot_version = objAlnDB['uniprot_version']
        else:
            print >> sys.stderr, "Failed to download Pfam-A.full.uniprot.gz from %s"%(g_params['pfam_ftp_url'])
            return 1

    elif not os.path.exists(alnfile):
        print sys.stderr, "Error! alnfile %s does not exist. Exit."%(alnfile)
        return 1
    alnfile = os.path.realpath(alnfile)

#========================================================
# Download the uniprot_trembl database if not exists
#========================================================

    if seqdbname == "":
        if not g_params['isQuiet']:
            print "seqdb not supplied, trying to download from %s"%(url_seqdb)
            print "\nThis takes a while, please be patient\n"
        if path_storage == "":
            print sys.stderr, "path_storage is not set while alnfile needs to be downloaded. Exit."
            return 1
        (b_total, b_used, b_free) = myfunc.disk_usage(path_storage)
        if b_free < 0 or b_free/1024.0/1024.0/1024.0 < MIN_FREE_DISK_SPACE_IN_GB:
            print >> sys.stderr, "There is not enough free disk space at %s. Exit"%(path_storage)
            return 1
        objSeqDB = Download_seqdb(path_storage, uniprot_version)
        if objSeqDB['uniprot_trembl_datfile_zip'] and objSeqDB['uniprot_sprot_datfile_zip']:
            (seqdbname, seqtablename) = CreateSeqDB_sqlite(objSeqDB['uniprot_trembl_datfile_zip'], objSeqDB['uniprot_sprot_datfile_zip'], isQuiet=g_params['isQuiet']) 
            if seqdbname == "":
                return 1
        else:
           print >> sys.stderr, "Failed to download %s from %s"%("uniprot_trembl.dat.gz", g_params['uniprot_ftp_url_old_release'])
           return 1


    if not os.path.exists(outpath):
        try:
            os.makedirs(outpath)
        except OSError:
            print >> sys.stderr, "Failed to create outpath %s. Exit"%(outpath)
            return 1
        outpath = os.path.realpath(outpath)

    outdb = "%s%spfamfullseqdb.nr%d.sqlite3"%(outpath, os.sep, seqidt_cutoff)
    versionfile = "%s%spfamfullseqdb.nr%d.version.txt"%(outpath, os.sep, seqidt_cutoff)

    if pfam_version != "" or uniprot_version != "":
        txt = "Pfam_version: %s\nUniprot_version: %s\n"%(pfam_version, uniprot_version)
        myfunc.WriteFile(txt, versionfile, "w", True)

#========================================================
#  now alnfile, seqdbname, seqtablename are prepared, start building the
#  pfamfullseq database
#========================================================
    CreatePfamFullseqDB(alnfile, seqidt_cutoff, seqdbname, seqtablename, outdb)


    return 0
#}}}

def InitGlobalParameter():#{{{
    g_params = {}
    g_params['pfam_ftp_url'] = "ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/"
    g_params['uniprot_ftp_url'] = "ftp://ftp.ebi.ac.uk/pub/databases/uniprot/knowledgebase/"
    g_params['uniprot_ftp_url_old_release'] = "ftp://ftp.ebi.ac.uk/pub/databases/uniprot/previous_releases/"
    g_params['pfam_uniprot_alnfile'] = "Pfam-A.full.uniprot.gz"
    g_params['pfam_versionfile'] = "Pfam.version.gz"
    g_params['pfam_relnotefile'] = "relnotes.txt"
    g_params['uniprot_trembl_fastafile'] = "uniprot_trembl.fasta.gz"
    g_params['uniprot_trembl_versionfile'] = "reldate.txt"

    g_params['isQuiet'] = True
    g_params['verbose'] = False
    g_params['nooverwrite'] = False
    g_params['exec_cdhit'] = ""
    g_params['debug'] = False
    return g_params
#}}}
if __name__ == '__main__' :
    g_params = InitGlobalParameter()

    start_time = time.time()

    rvalue = main(g_params)

    end_time = time.time()
    if g_params['verbose']:
        print "\nProgram ends at: %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        print "Total running time: %s"%(myfunc.second_to_human(end_time - start_time))
    sys.exit(rvalue)
#    cProfile.run("main()")
