from embeddings import get_embeddings
from database import create_index, upsert_vectors
import json

def main():
    # file_path = './psp_static.csv'
    # df_with_embeddings = get_embeddings(file_path)
    # print(df_with_embeddings.head())
    #
    # index_name = "psp-index"
    # dimension = 1536
    # index = create_index(index_name, dimension)
    #
    # if index is None:
    #     print("Failed to create or retrieve index.")
    #     return
    #
    # vectors = [{'embeddings': row['embeddings'], 'metadata': row['metadata']} for _, row in
    #            df_with_embeddings.iterrows()]
    # upsert_vectors(index, vectors)



    with open('psp-static.json', 'r') as file:
        data = json.load(file)

    embeddings = get_embeddings(data)

    # Create or retrieve the index
    index_name = "psp-static-flow"
    dimension = 1536
    index = create_index(index_name, dimension=dimension)

    # Prepare metadata
    metadata = []
    for item in data:
        category = item['category']
        if 'answers' in item:
            for answer in item['answers']:
                if 'text' in answer:
                    text = answer['text']
                    metadata.append({'category': category, 'text': text})

    # Upsert vectors
    upsert_vectors(index, embeddings, metadata)


main()