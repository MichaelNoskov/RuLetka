from sentence_transformers import SentenceTransformer

model = SentenceTransformer('cointegrated/rubert-tiny2')
model.save('./rubert-tiny2')
