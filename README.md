# Evaluating sentence co-occurrence as a method of determining relationships between genes and diseases
The following are a collection of Databricks and Jupyter notebooks for comparing gene/disease relationships between sentence co-occurrence extracted from literature, and the "truth" via Chembl and CMAP.

To do this comparison we need to put the data in the correct format. The sentence co-occurrence data will be represented
by a matrix where the rows represent genes and the columns represent diseases. There is a 1 in each row/column if there is a link between the gene and disease, and 0 otherwise. The CMAP and Chembl data are represented in the same way. 

To do the final comparison, we need to filter each of the CMAP and Chembl matrices so that they both have the same columns and
rows. This is to make the comparison fair, as we want to evaluate how many of the true CMAP/Chembl relationships
the co-occurence was able to identify.

## Data
__Raw data for Chembl and CMAP__: /zenegraph/co-occurrence-validation-raw

__Sentence co-occurrence data__: /zenegraph/termite-co-occurrences/gene_indication_co_occurences_summary.parquet

__Processed data for Chembl, CMAP and the sentence co-occurrence__: /zenegraph/co-occurrence-validation-processed

## Steps in the procedure:

Each step is a notebook.

1. cmap_cleaning (Jupyter): Clean the original CMAP data so that it is in the format specified previously (incidence matrix).
* Output data: /zenegraph/co-occurrence-validation-processed/cmap_cleaned.csv

2. chembl_cleaning (Databricks): Clean the original Chembl data so that is is in the format specified previously (incidence matrix).
* Output data: /zenegraph/co-occurrence-validation-processed/chembl_cleaned.csv

3. cmap_co_occurrence_filtering (Databricks): Filter the co-occurrence and cmap matrices so they both have the same rows and columns. The data for the co-occurrence matrix comes from the blob storage container zenegraph/
* Output data: /zenegraph/co-occurrence-validation-processed/cmap_filtered.csv, /zenegraph/co-occurrence-validation-processed/co_occurrence_cmap_filtered.csv  

4. chembl_co_occurrence_filtering (Databricks): Filter the co-occurrence and Chembl matrices so they have the same rows and columns
* Output data: /zenegraph/co-occurrence-validation-processed/chembl_filtered.csv, /zenegraph/co-occurrence-validation-processed/co_occurrence_chembl_filtered.csv 
    
5. dataframe_comparison (Jupyter): For each of the sets (co-occurrence vs. chembl and co-occurrence vs. cmap), calculate the recall, specificity and precision.

