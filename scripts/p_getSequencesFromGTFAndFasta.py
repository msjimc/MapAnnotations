#!/usr/bin/python
import os, sys
import gzip
import shutil

fastaName = sys.argv[1] 
gtfName = sys.argv[2] 
mRNAName = sys.argv[3] 

#### Get transcripts
chromosomes = {}
exons = []

transcriptID = ""

counter = 0
chromosome = ""
print("Chromosome: -, Transcript: -\r", end='') 

gtf = gzip.open(gtfName)
while (gtf):
	bit = gtf.readline().decode('ascii')
	if len(bit) == 0:
		break

	items = bit.split("\t")
	chromosome = items[0]
	if  len(items) > 8 and items[2] == "exon":
		index1 = items[8].find("gene_id ") + 9;
		index2 = items[8].find(";", index1)
		if index1 > -1 and index2 > -1:
			geneID = items[8][index1:index2 -1]
		index1 = items[8].find("transcript_id ") + 15
		index2 = items[8].find(";", index1)
		if index1 > -1 and index2 > -1:
			transcriptID = items[8][index1:index2 -1] + items[6]
		
		exon = (items[3]+ ":" + items[4])
		if chromosome in chromosomes:
			transcripts = chromosomes[chromosome]
			if transcriptID in transcripts:
				exons = transcripts[transcriptID]				
			else:
				exons = []
			exons.append(exon)
			transcripts[transcriptID] = exons
			chromosomes[chromosome] = transcripts
		else:
			exons = []
			exons.append(exon)
			transcripts = {}
			transcripts[transcriptID] = exons
			chromosomes[chromosome] = transcripts

		counter += 1
		if counter > 999:
			counter = 0
			print("Chromosome: " + chromosome + ", Transcript: " + transcriptID + "                       \r", end='') 

		

gtf.close();

#### Got transcripts


print("Reading fasta file                                       \r", end='') 

fasta = gzip.open(fastaName, 'r')
mRNA = open(mRNAName, 'w')

name = ""
sequence = ""
lines=[]
geneName = ""

lastTranscriptID = ""

first = 0

counter=0
size = 0

while (fasta):
	line = fasta.readline().decode('ascii')
	if len(line) == 0:
		break
	if line[0:1] == ">":
		if len(lines) > 0:
			print(name + "\t" + f"{size:,}" + " bp\r", end='')
			sequence = [' ', size]
			sequence = "".join(lines)
						
			if name in chromosomes:
				transcripts = chromosomes[name]
				for key in transcripts:
					if len(key) > 0:
						mRNA.write(">" + key + "\n" )
						for exon in transcripts[key]:
							bits = exon.split(":")
							seq = sequence[int(bits[0]):int(bits[1]) + 1]
							mRNA.write(seq)		
						mRNA.write("\n")	
		sequence = ""
		lines=[]
		name = line[1:len(line) - 1]
		indexName = name.find(" ")
		if indexName > -1:
			name = name[0:indexName]
		counter=0
		size=0
		print(name + "                                                             \r", end='')
	else:
		save=line[0:len(line) - 1]
		lines.append(save)
		size += len(save)
		counter += 1
		if counter > 19999:
			counter = 0
			print(name + "\t" + f"{size:,}" + " bp\r", end='')


if len(lines) > 0:
	sequence = ""
	sequence = [' ', size]
	sequence = "".join(lines)

	if name in chromosomes:
		transcripts = chromosomes[name]
		for key in transcripts:
			mRNA.write(">" + key + "\n" )
			for exon in transcripts[key]:
				bits = exon.split(":")
				seq = sequence[int(bits[0]):int(bits[1]) + 1]
				mRNA.write(seq)
			mRNA.write("\n")	

mRNA.close()
fasta.close()
