import json
import boto3
from collections import defaultdict

BUCKET = "my-data-pipeline"
DAG_KEY = "dag/dag.json"

s3 = boto3.client('s3')

def fetch_dag_definition():
    obj = s3.get_object(Bucket=BUCKET, Key=DAG_KEY)
    return json.loads(obj['Body'].read().decode())

def build_graph(dag_dict):
    graph = defaultdict(list)
    for task, deps in dag_dict.items():
        for dep in deps:
            graph[dep].append(task)
        if task not in graph:
            graph[task] = []
    return graph

def topological_sort(graph):
    visited = set()
    result = []
    temp_mark = set()

    def dfs(node):
        if node in temp_mark:
            raise Exception(f"Cycle detected at {node}")
        if node not in visited:
            temp_mark.add(node)
            for neighbor in graph[node]:
                dfs(neighbor)
            temp_mark.remove(node)
            visited.add(node)
            result.append(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return result[::-1]  # reverse the list to get correct order

def run_tasks_in_order(task_order):
    print("Executing tasks in order:")
    for task in task_order:
        print(f"→ {task} [done]")

def main():
    dag = fetch_dag_definition()
    graph = build_graph(dag)
    order = topological_sort(graph)
    run_tasks_in_order(order)

if __name__ == "__main__":
    main()
