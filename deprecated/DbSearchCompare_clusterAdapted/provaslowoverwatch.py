#!/bin/python
#import subprocess
import time
import os
import sys
#./provaslow/
print "PROVASLOWOVERWATCH.PY"

input="./input/partsx1/"
paramfile="./input/param4.txt"

tmpdir=sys.argv[1]



#dbpath=tmpdir+"/pfam/"
dbpath="../pfam"
outfolder=tmpdir+"/NODE_E001dataoutDBsc/"
paramfile=""
#max_processes=8

print "mkdir ",outfolder
if os.path.exists(outfolder)is False:
 os.system("mkdir "+outfolder)
if os.path.exists(outfolder+"/entry_collection") is False:
 os.system("mkdir "+outfolder+"/entry_collection")



realout="../outdir/NODE_E001c2outDBsc/"
print "mkdir ",realout
if os.path.exists(realout)is False:
 os.system("mkdir "+realout)
if os.path.exists(realout+"/entry_collection") is False:
 os.system("mkdir "+realout+"/entry_collection")

realout=realout+"entry_collection/"

#fileid=[]
#fileparam=[]
#with open("../outDBsc/failist.txt") as chkfile:
# for entry in next(os.walk("./input/partsx3/"))[2]:
#  fileid.append(entry[7:])
  


os.system("mkdir "+tmpdir+"/input")
os.system("cp -r "+input+" "+tmpdir+"/"+input[1:])
input=tmpdir+"/"+input[1:]

print "input loc:",input

print "commandlist performance"

#commandlist=[]



for inp in next(os.walk(input))[2]: 
  with open(input+inp) as infile:
   for line in infile.readlines()[::2]:
    os.system("mkdir "+outfolder+"/entry_collection/"+line[1:-1])
  flag='0'
  command="./Trigger "+realout+" "+dbpath+" "+flag+" "+input+inp+" "+outfolder
  print command
  os.system(command)
  flag='1'
  command="./Trigger "+realout+" "+dbpath+" "+flag+" "+input+inp+" "+outfolder+paramfile
  print command
  os.system(command)


#workers

#xx=open("../findfail.txt","w")

#print "process calls"

#processes=set()
#for command in commandlist:
# xx.write(command+"\n")
# processes.add(subprocess.Popen(command))
# if len(processes) >= max_processes:
#  os.wait()
#  processes.difference_update([p for p in processes if p.poll() is not None])

# print "command: ",command
# os.system(command)

#copying results back to place

