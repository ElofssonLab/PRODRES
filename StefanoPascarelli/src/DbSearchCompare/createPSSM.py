import os,sys
#from Bio import SeqIO





def main(args):

 infile=args[1]
 outdir=args[2]

 print "starting fast PSSM creation"
#fast 
 if os.path.exists(outdir+"/fastHMM/Alig.txt") is True:
  if os.path.exists(outdir+"/fastPSSM.txt")is True:
   os.system("perl reformat.pl sto fas "+outdir+"fastHMM/Alig.txt "+outdir+"fastHMM/fastAlig.txt")
#  SeqIO.convert(outdir+"fastHMM/Alig.txt","stockholm",outdir+"fastHMM/fastAlig.txt","fasta")
   os.system("psiblast -subject "+infile+" -in_msa "+outdir+"/fastHMM/fastAlig.txt -out_ascii_pssm "+outdir+"/fastPSSM.txt -word_size 5")
  else:
   print "fastPSSM.txt already present, skipping  PSSM creation
 else:
  print "Alig.txt not found, skipping PSSM creation"


#slow
 print "starting slow PSSM creation"
 if os.path.exists(outdir+"/slowHMM/Alig.txt") is True:
  if os.path.exists(outdir+"/fastPSSM.txt")is True:
   os.system("perl reformat.pl sto fas "+outdir+"slowHMM/Alig.txt "+outdir+"slowHMM/fastAlig.txt")
#  SeqIO.convert(outdir+"slowHMM/Alig.txt","stockholm",outdir+"slowHMM/fastAlig.txt","fasta")
   os.system("psiblast -subject "+infile+" -in_msa "+outdir+"/slowHMM/fastAlig.txt -out_ascii_pssm "+outdir+"/slowPSSM.txt -word_size 5")
  else:
   print "fastPSSM.txt already present, skipping  PSSM creation
 else:
  print "Alig.txt not found, skipping PSSM creation"







if __name__=="__main__":
    main(sys.argv)


