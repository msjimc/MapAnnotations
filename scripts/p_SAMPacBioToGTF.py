
#!/usr/bin/python
import os, sys
import gzip
import shutil

samFilename = sys.argv[1]
gtfFileName = sys.argv[2]
ignoredFile = gtfFileName + ".txt"
cutOff = 10
if len(sys.argv) == 4:
    cutOff = int(str(sys.argv[3]))

sam = open(samFilename, 'r')
gtf = open(gtfFileName, "w")
ignored = open(ignoredFile, "w")

ignoredCount = 0
writtenCount = 0
count = 0

def getLegthofHit(cigar, cutoff):
    values = []
    nosOfDAndIs = cigar.count("D") + cigar.count("I")
    if (nosOfDAndIs > cutoff):
        values.append(-1)
        return values

    index1 = 1000000
    letters = {"H", "S", "D", "I", "N", "M" }
    hit = ""

    add = False

    while len(cigar) > 0:
        index1 = 1000000
        for letter in letters:
            index = cigar.find(letter)
            if index > -1 and index < index1:
                index1 = index;
                hit = letter
        if hit == "H" or hit == "S": 
            add = False
            cigar = cigar[index1 + 1:len(cigar)]
        elif hit == "I":
            add = True
            cigar = cigar[index1 + 1:len(cigar)]
        elif hit == "D" or hit == "N": 
            add = False
            value = cigar[0:index1]
            values.append(-int(value))
            cigar = cigar[index1 + 1:len(cigar)] 
        elif hit == "M": 
            value = cigar[0:index1]
            if add == True:
                indexValues = len(values) - 1
                values[indexValues] = values[indexValues] +  int(value)
            else:
                values.append(int(value))
            add = False
            cigar = cigar[index1 + 1:len(cigar)] 

    return values        

def saveTranscriptAndGene(outPuts, gtf, writtenCount):
    minimum = 1000000000
    maximum = -1
    for line in outPuts:
        if int(line[2]) < minimum:
            minimum = int(line[2])
        if int(line[3]) > maximum:
            maximum = int(line[3])

    gt = [ outPuts[0][0], "fromGenome,\tgene", str(minimum), str(maximum), "0.000000", outPuts[0][5], ".",  outPuts[0][7] ]
    gtf.write("\t".join(gt))
    gt[1] = "fromGenome,\ttranscript"
    gtf.write("\t".join(gt))

    for outputWrite in outPuts:
        gtf.write("\t".join(outputWrite))
        outputWrite[1] = "fromGenome,\tCDS"
        gtf.write("\t".join(outputWrite))
        writtenCount +=1

    return writtenCount

def writeToFile (sequences, places, gtf, ignored, cutOff, ignoredCount, writtenCount):
    outPuts = []
    places.sort()
    for place in places:
        seqItems = sequences[place].split("\t")
        positions = getLegthofHit(seqItems[5], cutOff)
        if positions[0] > -1:
            startPoint = place
            combine = False
            extra = 0
            for position in positions:
                if position > 0:
                    if combine == True:
                        indexOutPuts = len(outPuts) - 1
                        output = outPuts[indexOutPuts]
                        newPlace = position + extra + int(output[3])
                        output[3] = str(newPlace)
                    else:
                        strand = ""
                        originalStrand = seqItems[0][len(seqItems[0])-1:len(seqItems[0])]
                        flag = int(seqItems[1])
                        revered = flag & 16
                        if revered == 16:
                            if originalStrand == "+":
                                strand = "-"
                            else:
                                strand = "+"
                        else: 
                            if originalStrand == "+":
                                strand = "+"
                            else:
                                strand = "-"

                        output = [ seqItems[2], "fromGenome\texon", str(startPoint), str(startPoint + position), "0.000000", strand, ".",  "gene_id \"" + seqItems[0][0:len(seqItems[0])-1] + "\"; " "transcript_id \"" + seqItems[0][0:len(seqItems[0])-1] + "\";\n" ]
                        outPuts.append(output)

                    startPoint += position
                    
                elif position < -50:
                    startPoint -= position
                    combine = False
                else:
                    extra = -position
                    combine = True

            writtenCount = saveTranscriptAndGene(outPuts, gtf, writtenCount)
                
            outPuts = []

        else:
            ignored.write(sequences[place])
            ignoredCount += 1

    return writtenCount, ignoredCount      


sequence = ""
sequences = {}
places = []

for line in sam:
    if line.startswith("@") == False:
        count += 1
        if count > 499:
            count = 0
            print("Saved: " + f"{writtenCount:,}" + " exons and ignored: " + f"{ignoredCount:,}" + " alignments                              \r", end='')
        items = line.split("\t")
       #print(items[0] + "\t" + items[2] + "\t" + items[3] + "\t" + items[4] + "\t" + items[5] + "\t" + items[6] )
        if items[2] != "*":
            if sequence != items[0] and len(sequences) > 0: #as data
                writtenCount, ignoredCount = writeToFile(sequences, places, gtf, ignored, cutOff, ignoredCount, writtenCount)
                outPuts = []
                places = []
                sequences = {} 
            
            place = int(items[3])
            sequences[place] = line
            places.append(place)
            sequence = items[0]


if  len(sequences) > 0: #as data from last sequence
        writtenCount, ignoredCount = writeToFile(sequences, places, gtf,ignored,  cutOff, ignoredCount, writtenCount)

print("Saved: " + f"{writtenCount:,}" + " exons and ignored: " + f"{ignoredCount:,}" + " alignments                              ")
sam.close()
gtf.close()
ignored.close()




