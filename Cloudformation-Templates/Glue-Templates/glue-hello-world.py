import sys
from pyspark.sql import SparkSession
from awsglue.context import GlueContext
from pyspark.sql import Row

# Initialize Spark and Glue Context
spark = SparkSession.builder.appName("GlueHelloWorldJob").getOrCreate()
glueContext = GlueContext(spark.sparkContext)

# Define output path in S3
s3_output_path = "s3://jon-data-pipeline-bucket/hello-world.csv"

# Create a simple DataFrame
data = [Row(message="Hello, World!")]
df = spark.createDataFrame(data)

# Force a single partition (prevents multiple output files)
df = df.coalesce(1)

# Write DataFrame to S3 as a single CSV file
df.write.mode("overwrite").option("header", "true").csv(s3_output_path)

print("Hello, World! written to S3 as a single file")
