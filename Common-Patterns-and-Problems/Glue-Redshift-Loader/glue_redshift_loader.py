import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions

# Glue Context Setup
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session

# Config (can also be passed in via --args)
REDSHIFT_JDBC_URL = "jdbc:redshift://your-cluster-url:5439/yourdb"
REDSHIFT_TABLE = "public.my_table"
REDSHIFT_USER = "awsuser"
REDSHIFT_PASSWORD = "mypassword"
S3_INPUT_PATH = "s3://my-data-pipeline/processed/output.parquet"

# 1. Read Parquet data from S3
df = spark.read.parquet(S3_INPUT_PATH)

# 2. (Optional) Clean or Rename Columns
df_clean = df.dropDuplicates().na.drop()

# 3. Write to Redshift
df_clean.write \
    .format("jdbc") \
    .option("url", REDSHIFT_JDBC_URL) \
    .option("dbtable", REDSHIFT_TABLE) \
    .option("user", REDSHIFT_USER) \
    .option("password", REDSHIFT_PASSWORD) \
    .option("driver", "com.amazon.redshift.jdbc.Driver") \
    .mode("overwrite") \
    .save()

print("✅ Data written to Redshift.")
