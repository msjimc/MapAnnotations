# MapAnnotations

When working on a none model organism there are many ways in which to identify the location of coding sequences in a de novo genome assembly. These typically depend on either purely theoretical approaches to the more practical method of mapping RNA sequence to the de novo assemble and then using the mapped reads to identify the location of the transcripts' exons. However, once the coding sequences have been deduced, it can be very difficult to identify the genes and giving them a function and linking them to KEGG pathways and Gene Ontology phrases. 

Fortunately, the number of well annotated genomes is increasing through the efforts of large genome centers such as the NCBI, which can be used as the starting point for annotation of related species. For example the dog (Canis lupus familiaris) is a reasonably well studied animal and so could be used to infer the annotation of a poorly studied animal such as the evolutionarily related grey seal (Halichoerus grypus). 

To do this we must first get the dog's reference genome and the gtf annotation file. These can easily obtained from the Genome Browser's [Genome Data page](https://hgdownload.soe.ucsc.edu/downloads.html?_gl=1*11ug8p7*_ga*MTMzMDM3MzY1Ny4xNjMyOTIwNTkx*_ga_P5EV0BL192*MTcxOTQzOTk2Mi4yNy4wLjE3MTk0Mzk5NjIuMC4wLjA.) > [Canine data](https://hgdownload.soe.ucsc.edu/goldenPath/canFam6/bigZips/) and [Table Browser](https://genome.ucsc.edu/cgi-bin/hgTables) and selected the required data files (Figure 1)

<hr />

![Figire 1](images/figure1.jpg)

Figure 1: Obtaining the annotation file. First select the correct reference file and gene set (blue box) and select the whole genome (pink box). Then select the correct data set (red box) and enter the file's name and gzip compression (green box) before pressing the ***get output*** button (black box). 

Once downloaded move the genome (fa.gz) and annotation (gtf.gz) files to a Linux server (only the mapping step has to be performed a Linux machine), leave the files as gzip compressed files. Next use the [p_getSequencesFromGTFAndFasta.py](scripts/p_getSequencesFromGTFAndFasta.py) to identify the sequences in the Dog's reference genome of the transcripts annotated in the gtf file, saving them to a fasta file using a command similar to this:

> python p_getSequencesFromGTFAndFasta.py canFam6.fa.gz canFam6.gtf.gz canFam6.fa.gz

***Description*** 

|Parameter|Purpose|
|-|-|
|python|Indicates the script is a python script|
|p_getSequencesFromGTFAndFasta.py|The name of the script file|
|canFam6.fa.gz|Name of the reference genome|
|canFam6.gtf.gz|Name of the gtf annotation file|
|canFam6_mRNA.fa|Name of the file to save the transcript sequences too|

***Note***: You may need to include the location of the files as well as their names.

When the __p_getSequencesFromGTFAndFasta.py__ runs it reads the gtf file and collects the positions of the exons in each transcript (Figure 2a). It then reads the reference fasta files one chromosome/contig at a time and then identifies the sequences for each exon in that chromosome/contig and saves them to the export file (Figure 2b). Each transcripts sequence is save in the fasta file using the transcripts ID value as an identifier. If the forward strand is as a __+__ appended to the name, while a __-__ indicates its on the reverse strand. 

<hr />

![Figure 2a](images/figure2a.jpg)

Figure 2a: Collecting the locations of the exons in the gtf file

<hr />

![Figure 2b](images/figure2b.jpg)

Figure 2b: Read the reference fasta file and saving the mRNA/cDNA sequences to file

<hr />

![Figure cb](images/figure2c.jpg)

Figure 2c: Transcript sequence in the exported file

<hr />

Once the transcript sequence fasta file has been created, align the sequences in this transcript file to the non-model organism's genome reference sequence using [minimap2](https://github.com/lh3/minimap2). minimap2 is a long read sequences that is designed to map genomic or RNA  long read data from a PacBio or ONT sequence to a genome. L since, long read data can be very noisy, the fact that there may be significant sequence divergence between the transcripts and genome should not be a fatal issue. 

The command below uses minimap2 to both make a genome reference and map sequences to the index in one step.  

> minimap2 -ax splice -t 8 grey_seal_a.fna canFam6mRNA.fa \> GreySealCanine6.sam

|Parameter|Purpose|
|-|-|
|minimap2|name of program to run|
|-ax|Instructs minimap2 to first create an index and the align the transcripts to it|
|splice|Indicates that the sequences to be aligned have been spliced and so the alignment may not be contiguous|
|-t 8|Instructs minimap2 to use 8 processors|
|grey_seal_a.fna|Name of file containing the reference sequence to align data too|
|canFam6mRNA.fa|Name of the transcripts to be aligned to the genome|
|GreySealCanine6.sam|Name of file to save the aligned data too|

***Note***: You may need to include the location of the files as well as their names.

Once the dog transcripts have been aligned, use the [p_SAMPacBioToGTF.py](scripts/p_SAMPacBioToGTF.py) to extract the regions of homology between the dog exons and the grey seal genome using a command like:

> python p_SAMPacBioToGTF.py grey_seal.sam grey_seal.gtf 20

|Parameter|Purpose|
|-|-|
|python|Indicates the script is a python script|
|p_SAMPacBioToGTF.py|The name of the script file|
|grey_seal.sam|Name of the alignment created by minimap2|
|grey_seal.gtf|Name of the gtf file created by p_SAMPacBioToGTF.py that contains the exons for each transcript|
|20|This filters the alignments based on how many indels are in the alignment that are not caused by the lack of introns in the transcript sequences. While some small insertions and deletions are to be expected, a large number suggests that the alignment is wrong or is aligned to a pseudo gene for example.|

***Note***: You may need to include the location of the files as well as their names.

p_SAMPacBioToGTF.py also creates a 2nd file called grey_seal.gtf.txt that contains all the alignments rejected by p_SAMPacBioToGTF.py either because it has to many indels or it was not mapped at all.

As p_SAMPacBioToGTF.py runs it indicates the number of exons identified and alignments rejected (Figure 3a and 3b).

<hr />

![Figure 3a](images/figure3a.jpg)

Figure 3a

<hr />

![Figure 3b](images/figure3b.jpg)

Figure 3b: The number of exons and ignored alignments at the end of an analysis

<hr />

The exported gtf file as the standard format with on transcript ID given (Figure 4). The sam file indicates whether the aligned sequence was aligned to the reference sequences forward or reverse strand. Similarly, the data in the transcript mRNA fasta file indicates whether the sequences was present on the model organism's forward and reverse strand. This information is then used to determine if the gene is on the reference sequences forward ot reverse strand as indicated in the table below Figure 4.


<hr />

![Figure 4](images/figure4.jpg)

Figure 4

<hr />

|Status|On model organism's forward strand (+)|On model organism's reverse strand (-)|
|-|-|-|
|Aligned to forward strand (+)|Gene on forward strand (+)| Gene on reverse strand (-)|
|Aligned to reverse strand (-)|Gene on reverse strand (-)|Gene on forward strand (+)|