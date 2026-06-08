import faiss
import numpy as np


def create_index(embeddings):

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(
        np.array(embeddings).astype("float32")
    )

    return index


def search_index(
    question_embedding,
    index,
    chunks,
    k=3
):

    distances, indices = index.search(
        question_embedding.astype("float32"),
        k
    )

    results = []

    for idx in indices[0]:

        results.append(
            chunks[idx]
        )

    return results