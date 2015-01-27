#!/usr/bin/env python
# Description: 
#   An example of how to use the pfamseqdb using the class MyDB 
#   written by Nanjiang 2014-11-25
import sys
import os
sys.path.append("%s/wk/MPTopo/src"%("/proj/bioinfo/users/x_nansh/"))
import myfunc    

def main(g_params):#{{{

    #pfamidList = ["PF12125", "PF04279"]
    
    strs = " TIGR01059 pfam07744 cd11497 cd08649 KOG0516 pfam14041 KOG2604 cd04859 KOG3790 COG1547 "
    pfamidList = strs.split()
    print "numfam to read = ", len(pfamidList)
    pfamseqdb = "/proj/bioinfo/users/x_nansh/data/uniprot/2014-11-05/hmmscan_cdd/cddfamseqdb_nr90/uniref100.cddfamseq.nr90"

    hdl = myfunc.MyDB(pfamseqdb)

    if hdl.failure:
        return 1

    outpath = "tmp1"
    if not os.path.exists(outpath):
        os.system("mkdir -p %s"%(outpath))

    for pfamid in pfamidList:
        record = hdl.GetRecord(pfamid)
        if record:
            fpout = open("%s/%s.fa"%(outpath, pfamid), "w")
            fpout.write("%s"% record)
            fpout.close()
    hdl.close()

#}}}

def InitGlobalParameter():#{{{
    g_params = {}
    g_params['isQuiet'] = True
    return g_params
#}}}
if __name__ == '__main__' :
    g_params = InitGlobalParameter()
    sys.exit(main(g_params))
