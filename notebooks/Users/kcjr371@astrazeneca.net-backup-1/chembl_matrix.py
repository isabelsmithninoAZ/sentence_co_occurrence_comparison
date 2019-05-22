# Databricks notebook source
from pyspark.sql import *
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
import itertools
import copy
from pyspark.sql.functions import array, udf
from pyspark.sql.types import ArrayType, StringType

# use only a small subset
use_test_set=False

storage_account_name = "zenegraph"
storage_account_access_key = dbutils.secrets.get(scope = "zenegraph", key = "zenegraph-storage")

spark.conf.set("fs.azure.account.key."+storage_account_name+".blob.core.windows.net",storage_account_access_key)

# needed to use pandas
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

# COMMAND ----------

file_location = "wasbs://chembl@zenegraph.blob.core.windows.net/chembl.json"

# STEP 0: Create small subsample
df = spark.read.json(file_location)
if use_test_set:
  df = df.limit(1000)
display(df)


# COMMAND ----------

# STEP 1: Only keep chembl results
df_chembl = df.filter(df.sourceID == 'chembl')
display(df_chembl)

# COMMAND ----------

# STEP 2.1: Create new column where I extract value of the association. In the next step I will keep only those where this value is 'true'

def associated_entry(row):
  if row.evidence['target2drug']['is_associated'] is not None:
    assoc = row.evidence['target2drug']['is_associated']
    return assoc

associated_entry_udf = udf(associated_entry, StringType())
df_association = df_chembl.withColumn("association", associated_entry_udf(struct([df_chembl[x] for x in df_chembl.columns])))
display(df_association)
  

# COMMAND ----------

# STEP 2.1: Keep if association == true
df_true = df_association.filter(df_association.association == 'true')
display(df_true)


# COMMAND ----------

# STEP 3: Extract disease and target

# DISEASE ID 
def extract_disease_id(row):
  if row.disease is not None:
    disease_id = row.disease['id'].replace('_',':')
    return disease_id

# TARGET
def extract_target(row):
   if row.target is not None:
      target_name = row.target['gene_info']['symbol']
      return target_name 

  
extract_disease_id_udf = udf(extract_disease_id, StringType())
df_clean1 = df_true.withColumn("disease_id", extract_disease_id_udf(struct([df_true[x] for x in df_true.columns]))) 
   
extract_target_udf = udf(extract_target, StringType())
df_clean2 = df_clean1.withColumn("gene_symbol", extract_target_udf(struct([df_clean1[x] for x in df_clean1.columns])))

display(df_clean2)

# COMMAND ----------

# STEP 4: Get MeSH id 

import requests
import json
 
def efo_to_mesh(row):
    url = 'https://www.ebi.ac.uk/spot/oxo/api/search'
    id_value = row.disease_id
    params = {"ids":id_value,"inputSource":'EFO',"mappingTarget":'mesh',"mappingSource":'EFO',"distance":1}
    resp = requests.get(url=url, params=params)
    data = resp.json() 
    
    # if it doesn't have a mesh id, in which case it throws an error, pass
    try:
      return data['_embedded']['searchResults'][0]['mappingResponseList'][0]['curie'].split(':')[1] # return only code, and not the 'mesh' part
    except:
      pass
    
efo_to_mesh_udf = udf(efo_to_mesh, StringType())
df_mesh = df_clean2.withColumn("mesh_id", efo_to_mesh_udf(struct([df_clean2[x] for x in df_clean2.columns])))  
display(df_mesh)


# COMMAND ----------

# STEP 5: Final cleaning, eliminate duplicates and null mesh id rows

from pyspark.sql import Row

df_final_clean = df_mesh.filter(df_mesh.mesh_id != 'null')

df_final_clean2 = df_final_clean.dropDuplicates(['gene_symbol','mesh_id'])
display(df_final_clean2)

# COMMAND ----------

# FINAL STEP: Pivoting
df_final = df_final_clean2.groupBy('gene_symbol').pivot('mesh_id').agg(count('association'))
display(df_final)

# COMMAND ----------

def write_to_azure_blob(df,filename):
  write_location = "wasbs://chembl@zenegraph.blob.core.windows.net/"+filename+".csv"
  df.coalesce(1).write.format("com.databricks.spark.csv").option("header", "true").save(write_location)

if use_test_set:
  write_to_azure_blob(df_final,'chembl_1000_ISN')
else:
  write_to_azure_blob(df_final,'chembl_ISN')

# COMMAND ----------

