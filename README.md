# sentence_co_occurrence_comparison
Two Jupyter notebooks which aide in the comparison of gene/disease relationships between sentence co-occurrence extracted from literature and the "truth" via Chembl and CMAP

The following notebooks are part of a larger process in evaluating the effectiveness of sentence co-occurrence as a measure of 
a relationship between a gene and disease. We compare this method with "true" relationships via Chembl and CMAP.

To compare these things we need to put the data in the correct format. The sentence co-occurrence data will be represented
by a matrix where the rows represent genes and the columns represent diseases. There is a 1 in each row/column if there is a link
between the gene and disease, and 0 otherwise.

The CMAP and Chembl data are represented in the same way. 

To do the final comparison, we need to filter each of the CMAP and Chembl matrices so that they both have the same columns and
rows. This is to make the comparison fair, as we want to evaluate how many of the true CMAP/Chembl relationships
the co-occurence was able to identify.

The notebooks here do two things:

1. cmap_clean: Clean the original CMAP data so that it is in the format specified previously (incidence matrix).
2. compare_dataframes: compare two dataframes and calculate recall, specificity and precision.

