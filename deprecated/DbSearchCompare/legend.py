#!/usr/bin/python

import sys





def main(argv):



 with open(argv[1]+"Legend.txt","w") as legend:
  out=tuple(argv[2:])

  legtext="""run performed on %s sequences, pscan eval= %s, clan overlap = %s


                    #####################################################
                          Slow-Fast DB scan comparison Output Legend

                                         ver 0.9
                    #####################################################

./					*description*

entry_collection/					Collection of folders, one each entry 

   standard_entry/					Collection of entry stats

	{fast/slow}HMM/					Collection of HMM outputs of fast/slow version
		Alig.txt		Stockholm alignment of HMM result
		HMMout.txt		Standard HMM output
		tableOut.txt		HMM table output


	Graphs/						Collection of graphs
		{0/50/../400}.png	Graphics for number of sequences with score > x
		fast{0/50/../200}.png	Graphic representation of fast method (domain) coverage %% 
						in respect to slow method hits with bitscore > x

	{fast/slow}time.txt		Output of "time" unix command for later time elaboration

	ParsedDic.txt			List of slow jackhmmer results for debugging reasons

	ParsedPfamscanDomains.txt	List of fast pfamscan results for debugging reasons

	query.fa			FASTA sequence of query

	query.hits.db			Shrinked database for fast jackhmmer

	query.hits.db			Temporary database before removal of identical sequences

	query.txt			Pfamscan output

	Score.txt			Percentage overlap function output in human readable form

	Pscantime.txt			Output of "time" unix command for later time elaboration

	Comparison.txt			Comparison between fast and slow sequences results (to be widened)


statistics/						Collection of dataset statistics

	{0/50/../400}.png		Overall distribution of results score
	Overall%%.png			Average percentage overlap within dataset with standard deviation
	hell.txt			A collection of very low scoring entries mainly for "debug" reasons (contrappasso)
	CPUtime...png			Graphical comparison of CPU running time for all sequences in groups of 24
	efctime...png			Graphical comparison of effective running time for all sequences in groups of 24

"""%out
  legend.write(legtext)



if __name__=="__main__":
 main(sys.argv)
