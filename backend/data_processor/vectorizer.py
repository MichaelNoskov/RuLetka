from sentence_transformers import SentenceTransformer


class Vectorizer:
    def __init__(self):
        self.model = SentenceTransformer('./models/rubert-tiny2')

    def generate_embedding(self, description: str) -> list[float]:
        embs = self.model.encode(description).tolist()
        return embs

model = Vectorizer()

if __name__ == "__main__":
    print(model.generate_embedding('Жили были дед да баба'))
