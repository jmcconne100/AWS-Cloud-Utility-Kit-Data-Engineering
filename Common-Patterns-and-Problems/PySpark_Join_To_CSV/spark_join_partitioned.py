from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, to_date

# CONFIG
FACT_PATH = "s3://my-data-pipeline/fact/events.parquet"
DIM_PATH = "s3://my-data-pipeline/dim/users.csv"
OUTPUT_PATH = "s3://my-data-pipeline/curated/joined/"
PARTITION_COL = "year"

spark = SparkSession.builder.appName("join_and_partition").getOrCreate()

# 1. Load fact table (e.g., event log)
fact_df = spark.read.parquet(FACT_PATH)

# 2. Load dimension table (e.g., user info)
dim_df = spark.read.csv(DIM_PATH, header=True, inferSchema=True)

# 3. Optional cleaning
fact_df = fact_df.dropna(subset=["user_id", "timestamp"])
dim_df = dim_df.dropDuplicates(["user_id"])

# 4. Enrich fact data with dimension info
joined_df = fact_df.join(dim_df, on="user_id", how="left")

# 5. Extract partition columns
joined_df = joined_df.withColumn("year", year(to_date(col("timestamp"))))

# 6. Write to S3 in partitioned Parquet format
joined_df.write \
    .mode("overwrite") \
    .partitionBy(PARTITION_COL) \
    .parquet(OUTPUT_PATH)

print(f"✅ Join complete. Output written to: {OUTPUT_PATH}")
