import boto3
import csv
import os
import tempfile
import heapq
from typing import List, Tuple

# CONFIG
BUCKET_NAME = "my-data-pipeline"  # Replace with your actual bucket
INPUT_KEY = "input/input.csv"
CHUNKS_PREFIX = "chunks/"
OUTPUT_KEY = "output/sorted_output.csv"
CHUNK_SIZE = 1000  # Adjust for simulation

s3 = boto3.client('s3')

def download_s3_file(key: str, local_path: str):
    s3.download_file(BUCKET_NAME, key, local_path)

def upload_s3_file(local_path: str, key: str):
    s3.upload_file(local_path, BUCKET_NAME, key)

def split_and_sort_chunks(local_input: str) -> Tuple[List[str], List[str]]:
    chunk_paths = []
    chunk_keys = []
    with open(local_input, newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        chunk = []
        index = 0

        for row in reader:
            chunk.append(row)
            if len(chunk) >= CHUNK_SIZE:
                chunk.sort(key=lambda x: int(x[0]))
                local_chunk = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
                writer = csv.writer(local_chunk)
                writer.writerow(header)
                writer.writerows(chunk)
                local_chunk.close()

                chunk_key = f"{CHUNKS_PREFIX}chunk_{index}.csv"
                upload_s3_file(local_chunk.name, chunk_key)
                chunk_paths.append(local_chunk.name)
                chunk_keys.append(chunk_key)

                os.remove(local_chunk.name)
                chunk = []
                index += 1

        if chunk:
            chunk.sort(key=lambda x: int(x[0]))
            local_chunk = tempfile.NamedTemporaryFile(delete=False, mode='w', newline='')
            writer = csv.writer(local_chunk)
            writer.writerow(header)
            writer.writerows(chunk)
            local_chunk.close()

            chunk_key = f"{CHUNKS_PREFIX}chunk_{index}.csv"
            upload_s3_file(local_chunk.name, chunk_key)
            chunk_paths.append(local_chunk.name)
            chunk_keys.append(chunk_key)
            os.remove(local_chunk.name)

    return chunk_keys, header

def merge_sorted_chunks(chunk_keys: List[str], header: List[str], local_output: str):
    heap = []
    file_objs = []
    readers = []

    for key in chunk_keys:
        local_chunk = tempfile.NamedTemporaryFile(delete=False, mode='r+', newline='')
        s3.download_file(BUCKET_NAME, key, local_chunk.name)
        local_chunk.seek(0)
        reader = csv.reader(local_chunk)
        next(reader)  # skip header
        file_objs.append(local_chunk)
        readers.append(reader)
        try:
            row = next(reader)
            heapq.heappush(heap, (int(row[0]), len(readers)-1, row))
        except StopIteration:
            pass

    with open(local_output, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)

        while heap:
            _, idx, row = heapq.heappop(heap)
            writer.writerow(row)
            try:
                next_row = next(readers[idx])
                heapq.heappush(heap, (int(next_row[0]), idx, next_row))
            except StopIteration:
                pass

    for f in file_objs:
        f.close()
        os.remove(f.name)

def external_sort_s3():
    # Step 1: Download original CSV
    local_input = tempfile.NamedTemporaryFile(delete=False).name
    download_s3_file(INPUT_KEY, local_input)

    # Step 2: Split into sorted chunks and upload to S3
    chunk_keys, header = split_and_sort_chunks(local_input)
    os.remove(local_input)

    # Step 3: Merge sorted chunks
    local_output = tempfile.NamedTemporaryFile(delete=False).name
    merge_sorted_chunks(chunk_keys, header, local_output)

    # Step 4: Upload final sorted output
    upload_s3_file(local_output, OUTPUT_KEY)
    os.remove(local_output)

if __name__ == "__main__":
    external_sort_s3()
