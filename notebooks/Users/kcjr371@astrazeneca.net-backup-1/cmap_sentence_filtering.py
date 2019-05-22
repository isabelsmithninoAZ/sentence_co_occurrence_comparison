# Databricks notebook source
# MAGIC %md
# MAGIC # CMAP - sentence co-occurrence comparison pre-processing:
# MAGIC 
# MAGIC 0. Load the CMAP matrix - this is the "truth". Call this matrix T with elements t_{ij}, where i=gene and j=disease
# MAGIC 1. Load a parquet file from the blob (the whole co-occurrence matrix is split into many chunks). Call this matrix P with elements p_{ij}
# MAGIC 2. Create two filtered dataframes, each one with the common rows and columns
# MAGIC 3. Export both to csv files for analysis in pandas locally (quicker)
# MAGIC 
# MAGIC   -Recall = number of correctly estimated relationships/total number of correct relationships

# COMMAND ----------

# packages I need (check if I need all of them)
from pyspark.sql.functions import when, lit
from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
import itertools
import copy
from pyspark.sql.functions import array, udf
from pyspark.sql.types import ArrayType, StringType, IntegerType

storage_account_name = "zenegraph"
storage_account_access_key = dbutils.secrets.get(scope = "zenegraph", key = "zenegraph-storage")

spark.conf.set("fs.azure.account.key."+storage_account_name+".blob.core.windows.net",storage_account_access_key)

# needed to use pandas
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading the data and filtering

# COMMAND ----------

# Load the cmap data
filename_cmap = "wasbs://cmap@zenegraph.blob.core.windows.net/target_indication_matrix_clean.csv"
cmap = spark.read.format("csv").option("header", "true").load(filename_cmap)
cmap_target = cmap.select("target") # for further merging

# Load the co-occurrence data    
filename_parquet= "wasbs://termite-co-occurrences@zenegraph.blob.core.windows.net/gene_indication_co_occurrences_summary.parquet"
parquetFile = spark.read.parquet(filename_parquet)
parquet_file = parquetFile.withColumnRenamed('gene','target') # renaming the gene column so I can do an inner join with cmap
parquet_file_target = parquet_file.select("target")

# common columns between both, for filtering later on
common_cols = list(set(cmap.columns) & set(parquet_file.columns))

# Co-occurrence filtering - by gene and indication
parquet_file_row = parquet_file.join(cmap_target, on=['target'], how='inner')
parquet_filtered = parquet_file_row.select(common_cols)

# CMAP filtering - by gene and indication
cmap_row = cmap.join(parquet_file_target, on=['target'], how='inner')
cmap_filtered = cmap_row.select(common_cols)

# COMMAND ----------

display(cmap_filtered)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Export to csv for analysis in Jupyter notebook

# COMMAND ----------

def write_to_azure_blob(df,filename):
  write_location = "wasbs://cmap@zenegraph.blob.core.windows.net/"+filename+".csv"
  df.coalesce(1).write.format("com.databricks.spark.csv").option("header", "true").save(write_location)

write_to_azure_blob(cmap_filtered,'cmap_filtered')
write_to_azure_blob(parquet_filtered,'co_occurrence_cmap_filtered')

# COMMAND ----------

