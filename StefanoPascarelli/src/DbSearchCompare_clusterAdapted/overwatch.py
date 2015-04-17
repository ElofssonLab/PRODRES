#!/bin/python

import os


 for i in range(11): #divide n of seq by 11

  for j in range(5): #4 diff param and slow
   if j==0:
    os.system("sbatch slowtrigger.sh tm_part"+str(i)+".seq")
   else:
    os.system("sbatch squaretrigger.sh tm_part"+str(i)+".seq "+str(j))
