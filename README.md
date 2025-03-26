# Readme

This project is a modular sandbox for demonstrating common patterns and practices used in real-world cloud-based data engineering workflows, including architecture patterns, automation scripts, orchestration DAGs, and resource provisioning.
    ---Patterns: Implementation of 10 cloud-native architecture patterns using AWS services and Python.
    ---CLI Tool: Automates common data infrastructure tasks (provisioning, uploads, testing).
    ---ETL Scripts: PySpark, Pandas, and SQL-based workflows for cleaning and transforming data.
    ---Orchestration DAGs: Example Airflow DAGs that connect infrastructure to workflows.
    ---CloudFormation Templates: Reusable IaC resources for common setups in data and analytics pipelines.

This project is actively maintained as a living portfolio to explore cloud-native data engineering practices.

<pre><code>``` 
/cloud-data-architecture-lab 
│ 
├── README.md 
│ 
├── boto-cloudshell-admin-tool/ 
│    ├── wrapper.py 
│    └── scripts/ 
│  
├── cloudformation-resource-templates/ 
│    ├── EC2/ 
│    ├── Glue/ 
│    ├── Database/ 
│    ├── IAM/ 
│    ├── Kinesis/ 
│    ├── Lambda/ 
│    ├── MWAA/ 
│    ├── Redshift/ 
│    ├── S3/ 
│    └── VPC/ 
│    
├── common-patterns-and-problems/ 
│    ├── algorithms/ 
│    ├── common-problems/ 
│    ├── data-transformation/ 
│    └── wrappers/ 
│ 
├── patterns/ 
│    ├── load-leveler-dlq/ 
│    ├── outbox-dynamodb/ 
│    ├── fan-out/ 
│    ├── saga/ 
│    └── pub-sub/ 
│ 
├── common-sql-problems/ 
│ 
└── dags/ 
```
</code></pre>
