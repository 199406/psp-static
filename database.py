from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

# Load variables from the .env file into the environment
load_dotenv()

# Now you can access the variables using os.getenv()
api_key = os.getenv("PINECONE_API_KEY")

import pinecone
import pandas as pd
from embeddings import get_embeddings

# df = pd.read_csv('psp_static.csv')
#
# pc = Pinecone(api_key=api_key)
#
# # Create or retrieve an index
# index_name = "psp-static"
# index = pinecone.Index(index_name, host='psp-static-s2jdw02.svc.aped-4627-b74a.pinecone.io')
#
# def create_index(index_name, dimension):
#     pc = Pinecone(api_key=api_key)
#     existing_indexes = pc.list_indexes()
#
#     if index_name in existing_indexes:
#         print(f"Index '{index_name}' already exists. Retrieving index.")
#         index = pc.Index(name=index_name)
#     else:
#         print(f"Creating index '{index_name}' with dimension {dimension}...")
#         pc.create_index(
#             name=index_name,
#             dimension=dimension,
#             metric="cosine",  # Ensure the metric is specified if required
#             spec=ServerlessSpec(
#                 cloud='aws',
#                 region='us-east-1'
#             )
#         )
#         index = pc.Index(name=index_name)
#
#     return index
#
#
# def upsert_vectors(index, vectors):
#     batch_size = 10  # Adjust batch_size based on your needs and limitations
#     batches = [vectors[i:i + batch_size] for i in range(0, len(vectors), batch_size)]
#     print(f"Total batches: {len(batches)}")
#
#     for batch_num, batch in enumerate(batches):
#         try:
#             to_upsert = [
#                 {"id": f"vector_{batch_num * batch_size + i}",  # Unique ID for each vector
#                  "values": row['embeddings'],
#                  "metadata": row['metadata']}
#                 for i, row in enumerate(batch)
#             ]
#             response = index.upsert(vectors=to_upsert)
#             print(f"Batch {batch_num + 1} upserted successfully, response: {response}")
#         except Exception as e:
#             print(f"Error upserting batch {batch_num + 1}: {e}")
#
def create_index(index_name, dimension):
    pc = Pinecone(api_key=api_key)
    existing_indexes = pc.list_indexes()
    if index_name in existing_indexes:
        print(f"Index '{index_name}' already exists. Retrieving index.")
        index = pc.Index(name=index_name)
    else:
        print(f"Creating index '{index_name}' with dimension {dimension}...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        index = pc.Index(name=index_name)
    return index

def upsert_vectors(index, vectors, metadata):
    batch_size = 10
    batches = [vectors[i:i + batch_size] for i in range(0, len(vectors), batch_size)]
    print(f"Total batches: {len(batches)}")
    for batch_num, batch in enumerate(batches):
        try:
            to_upsert = [
                {
                    "id": f"vector_{batch_num * batch_size + i}",
                    "values": vector,
                    "metadata": metadata[batch_num * batch_size + i]
                }
                for i, vector in enumerate(batch)
            ]
            response = index.upsert(vectors=to_upsert)
            print(f"Batch {batch_num + 1} upserted successfully, response: {response}")
        except Exception as e:
            print(f"Error upserting batch {batch_num + 1}: {e}")