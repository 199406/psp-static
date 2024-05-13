import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load variables from the .env file into the environment
load_dotenv()

# Now you can access the variables using os.getenv()
api_key = os.getenv("OPENAI_API_KEY")

# def get_embeddings(file_path):
#     df = pd.read_csv(file_path)
#
#     # Initialize the OpenAI client with your API key
#     client = OpenAI(api_key="")
#
#     def get_embeddings_helper(client, texts):
#         embeddings = []
#         batch_size = 20
#         for i in range(0, len(texts), batch_size):
#             batch = texts[i:i + batch_size]
#             response = client.embeddings.create(
#                 model="text-embedding-ada-002",
#                 input=batch,
#                 encoding_format="float"
#             )
#             # Access the embedding vectors from the Embedding objects
#             for embedding_obj in response.data:
#                 embedding_vector = embedding_obj.embedding
#                 embeddings.append(embedding_vector)
#         return embeddings
# #
#     # Check if embeddings are already populated
#     if 'embeddings' not in df.columns:
#         # Create a dictionary with metadata and combined text
#         data = []
#         for _, row in df.iterrows():
#             metadata = {
#                 'categories': row['categories'],
#                 'answers': row['answers']
#             }
#             combined_text = ' '.join([row['categories'], row['answers']])
#             data.append({'metadata': metadata, 'combined_text': combined_text})
#
# #         # Retrieve embeddings for each data entry
#         embeddings = get_embeddings_helper(client, [d['combined_text'] for d in data])
# #
# #         # Create df_new with 'sku', 'embeddings', and 'metadata' columns
#         df_new = pd.DataFrame({
#             'embeddings': embeddings,
#             'metadata': [d['metadata'] for d in data]
#         })
#
#     return df_new

def get_embeddings(data):
    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key=api_key)

    def get_embeddings_helper(client, texts):
        embeddings = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=batch,
                encoding_format="float"
            )
            # Access the embedding vectors from the Embedding objects
            for embedding_obj in response.data:
                embedding_vector = embedding_obj.embedding
                embeddings.append(embedding_vector)
        return embeddings

    # Create a list of combined texts
    combined_texts = []
    for item in data:
        category = item['category']
        for answer in item['answers']:
            text = answer['text']
            questions = ' '.join(answer['questions'])
            combined_text = f"{category} {text} {questions}"
            combined_texts.append(combined_text)

    # Retrieve embeddings for each combined text
    embeddings = get_embeddings_helper(client, combined_texts)
    return embeddings