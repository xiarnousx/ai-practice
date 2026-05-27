# EXAMPLE OF NEURAL RETRIEVAL

import numpy as np
import os
import faiss
from openai import OpenAI

from dotenv import load_dotenv

#Load .env file
load_dotenv()


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

reviews = [
    "I hate stories about backpacking. It's boring.",
    "A moving exploration of racial injustice and moral growth.",
    "Compelling dystopia, but overwhelmingly bleak.",
    "Timeless romance with sharp social commentary.",
    "Timeless romance with sharp social commentary.",
    "Epic sea adventure with philosophical depth.",
    "Mesmerizing magic and romance with rich world-building.",
    "Beautifully descriptive, but predictable plot.",
    "A detailed and emotional journey through loss and art.",
    "Fresh take on Greek mythology, but pacing dragged.",
    "Brilliant exploration of complex relationships and personal growth.",
    "Another bland romantic utopia. This time on a tropical island.",
]

# Retrieve embedding vectors
def get_embedding(text):
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Indexing vector for each review
def index_reviews(reviews):
    # get the embeddings for reviews
    vectors = []

    for review in reviews:
        vectors.append(get_embedding(review))

    # create the index
    d = len(vectors[0]) # dimension of the vectors

    index = faiss.IndexFlatL2(d) # build the index

    # reshape the vectors to be 2D and then add to index
    vectors = np.array(vectors).reshape(len(vectors), -1)
    index.add(vectors)

    return index

# Build retrieval function

def retrieve_reviews(index, query, reviews, k=2):
    # get the embedding for the query
    query_vector = get_embedding(query)

    # reshape vector into 2d array tehn search the index
    query_vector = np.array(query_vector).reshape(1, -1)
    distances, indices = index.search(query_vector, k)

    return [reviews[i] for i in indices[0]]

# let's give it a try

index = index_reviews(reviews)

book = """
The Beach by Alex Garland critiques backpacker culture by exposing the 
selfishness and moral decay behind their pursuit of an untouched paradise.
"""

related_reviews = retrieve_reviews(index, book, reviews)

print(related_reviews)

def predict_rating(book, related_reviews):
    reviews = "\n".join(related_reviews)

    prompt = (
        "Here is a book I might want to read:\n" +
        book + "\n\n" +
        "Here are relevant reviews from the past:\n" +
        reviews + "\n\n" +
        "On a scale of 1(worst) to 5(best)," +
        "How likely am I to enjoy this book?" +
        "Reply with no explanation, just a number"
    )

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        message = [{
            "role": "user",
            "content": prompt
        }],
        max_tokens = 2000,
        temperature = 0.7,
    )

    return response.choices[0].message.content
