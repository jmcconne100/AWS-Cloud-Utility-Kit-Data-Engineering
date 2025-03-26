from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, avg
from pyspark.sql.window import Window

# CONFIG
INPUT_PATH = "s3://my-data-pipeline/fact/events.csv"
OUTPUT_PATH = "s3://my-data-pipeline/analytics/rolling_avg/"
ENTITY_COL = "user_id"
METRIC_COL = "value"
TIMESTAMP_COL = "timestamp"

spark = SparkSession.builder.appName("rolling_avg").getOrCreate()

# 1. Load event data
df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)

# 2. Convert timestamp to date
df = df.withColumn("event_date", to_date(col(TIMESTAMP_COL)))

# 3. Define window: 7-day rolling per user
window_spec = Window.partitionBy(ENTITY_COL).orderBy("event_date").rowsBetween(-6, 0)

# 4. Compute rolling average
df = df.withColumn("rolling_avg_7d", avg(METRIC_COL).over(window_spec))

# 5. Write result to S3
df.write.mode("overwrite").parquet(OUTPUT_PATH)

print(f"✅ Rolling average written to: {OUTPUT_PATH}")
