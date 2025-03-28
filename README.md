# Readme
## AWS Data Engineering Toolkit (Meta Repo)

This is a curated **meta-repo** that links to a suite of modular tools and reusable components designed for **cloud-native data engineering on AWS**.

Each sub-repo serves a focused purpose — from infrastructure-as-code and admin automation to ETL support, reusable algorithms, and real-world deployment patterns. Together, they form a practical and extensible **AWS Data Engineering Toolkit**.
- **Patterns**: Implementation of 10 cloud-native architecture patterns using AWS services and Python.
- **CLI Tool**: Automates common admin tasks (monitoring, observability, cost-management).
- **Scripts and Algorithms**: Common algorithmic problems, basic problems, and ETL scripts with PySpark and Pandas.
- **CloudFormation Templates**: Reusable IaC resources for common setups in data and analytics pipelines.

This project is actively maintained as a living portfolio to explore cloud-native data engineering practices.

---

## Included Repositories

### [AWS Data Engineer CLI](https://github.com/jmcconne100/AWS-CLI-Tool) - [https://github.com/jmcconne100/AWS-CLI-Tool](https://github.com/jmcconne100/AWS-CLI-Tool)
A CloudShell-ready command-line tool for AWS data engineers.  
Includes common admin tasks like:
- Monitoring EC2, EBS, Security Groups, VPC's, Tags
- Managing S3 Data Lakes
- Starting ETL Glue Jobs
- Triggering Lambda functions

---

### [AWS SA Patterns – CloudFormation](https://github.com/jmcconne100/SA-Patterns) - [https://github.com/jmcconne100/SA-Patterns](https://github.com/jmcconne100/SA-Patterns)
A collection of deployable **Solutions Architecture patterns** in CloudFormation.  
Includes modular, production-aware templates for:
- Durable-Event-Buffer.yml
- Event-State-Upsert-Pattern.yml
- Eventbridge Replay.yml
- Fan-In-Pattern.yml
- Fan-Out-Pattern.yml
- Lakehouse-Fanout-Pattern.yml
- Load-Leveler-DLQ-Pattern.yml
- Outbox-Pattern.yml
- Pub-Sub-Pattern.yml
- Saga-Pattern.yml

---

### [CloudFormation Resource Template Library](https://github.com/jmcconne100/Cloud-Formation-Resource-Portfolio) - [https://github.com/jmcconne100/Cloud-Formation-Resource-Portfolio](https://github.com/jmcconne100/Cloud-Formation-Resource-Portfolio)
A reusable library of single-resource or small-scope CloudFormation templates.  
Useful for bootstrapping:
- IAM roles/policies
- S3 buckets
- Lambda functions
- EC2
- Glue
- Redshift
- Databases
- Athena workgroups and saved queries
- etc.

---

### [Data Engineering Scripts, Algorithms & Wrappers](https://github.com/jmcconne100/Common-Problems-And-DSAs) - [https://github.com/jmcconne100/Common-Problems-And-DSAs](https://github.com/jmcconne100/Common-Problems-And-DSAs)
A collection of useful Python, SQL, and Glue-related scripts including:
- Custom ETL functions for AWS Glue
- Algorithmic utilities (e.g., deduplication, schema comparison)
- SQL snippets for Athena
- Lightweight database wrappers
- Job pre-processing logic

---

## Why This Toolkit?

Modern AWS data engineering involves far more than just writing pipelines — it includes managing infrastructure, automating workflows, deploying at scale, and monitoring behavior across systems.

This toolkit was created to:
- Accelerate new data engineering projects
- Provide production-aware, reusable components
- Showcase real-world AWS data workflows in modular form

---

## Recommended Use Cases

- ✅ Rapidly spin up AWS Glue, Redshift, or Athena environments
- ✅ Trigger and monitor jobs from the command line
- ✅ Automate IAM + resource provisioning using proven patterns
- ✅ Plug reusable ETL logic into new workflows
- ✅ Use patterns as templates for your own IaC deployments

---

## 👤 About the Author

Built by [Jon McConnell](https://www.linkedin.com/in/jon--mcconnell/) – aspiring AWS Cloud Data Engineer focused on automation, infrastructure, and scalable data pipelines.

