#!/bin/python
import os
#./provaslow/
outfolder="../SAVE_OldscriptNewdboutDBsc/"
paramfile=""

if os.path.exists(outfolder)is False:
 os.system("mkdir "+outfolder)
if os.path.exists(outfolder+"/entry_collection") is False:
 os.system("mkdir "+outfolder+"/entry_collection")

#fileid=[]
#fileparam=[]
#with open("../outDBsc/failist.txt") as chkfile:
# for entry in next(os.walk("./input/partsx3/"))[2]:
#  fileid.append(entry[7:])
  


input="./input/partsx1/"



for inp in next(os.walk(input))[2]: #divided n of seq by 11
  paramfile=""
  with open(input+inp) as infile:
   for line in infile.readlines()[::2]:
    os.system("mkdir "+outfolder+"/entry_collection/"+line[1:-1])
  j=0
  os.system("sbatch ./SAVE_slowtrigger.sh "+str(j)+" "+input+inp+" "+outfolder)
  for j in range(1,5):
   paramfile=" ./input/param"+str(j)+".txt"
   os.system("sbatch ./SAVE_squaretrigger.sh "+str(j)+" "+input+inp+" "+outfolder+paramfile)

