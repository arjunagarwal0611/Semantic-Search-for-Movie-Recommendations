import pymongo
import requests
import openai

client = pymongo.MongoClient("mongodb+srv://arjunagarwal061102:pOmIgpyjZiMfvu4l@cluster0.utl7hy3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.sample_mflix
collection = db.movies

hf_token = "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"
embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:

  response = requests.post(
    embedding_url,
    headers={"Authorization": f"Bearer {hf_token}"},
    json={"inputs": text})

  if response.status_code != 200:
    raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

  return response.json()

for doc in collection.find({'plot':{"$exists": True}}).limit(50):
  doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
  collection.replace_one({'_id': doc['_id']}, doc)

query = "imaginary characters from outer space at war"

results = collection.aggregate([
  {"$vectorSearch": {
    "queryVector": generate_embedding(query),
    "path": "plot_embedding_hf",
    "numCandidates": 100,
    "limit": 4,
    "index": "PlotSemanticSearch",
      }}
]);

for document in results:
    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')

#for creating embeddings using open-ai api key
#openai.api_key = '<open-ai key>'
#
#client = pymongo.MongoClient("+mongodb+srv://arjunagarwal061102:pOmIgpyjZiMfvu4l@cluster0.utl7hy3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
#db = client.sample_mflix
#collection = db.embedded_movies
#
#def generate_embedding(text: str) -> list[float]:
#
#    response = openai.Embedding.create(
#        model="text-embedding-ada-002", 
#        input=text
#    )
#    return response['data'][0]['embedding']
#
#query = "imaginary characters from outer space at war"
#
#results = collection.aggregate([#mongodb+srv://arjunagarwal061102:pOmIgpyjZiMfvu4l@cluster0.utl7hy3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
#  {"$vectorSearch": {
#    "queryVector": generate_embedding(query),
#    "path": "plot_embedding",
#    "numCandidates": 100,
#    "limit": 4,
#    "index": "PlotSemanticSearch",
#      }}
#]);
#
#for document in results:#
#    print(f'Movie Name: {document["title"]},\nMovie Plot: {document["plot"]}\n')