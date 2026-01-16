import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
import os

from app.core.ports.services.vectorizer import AbstractVectorizer
from app.infrastructure.config.settings import settings


class SentenceTransformerVectorizer(AbstractVectorizer):
    
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.VECTORIZER_MODEL_PATH
        self._model: Optional[SentenceTransformer] = None
        self._dimension: Optional[int] = None
    
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            if os.path.exists(self.model_path):
                print(f"Загрузка модели из {self.model_path}", flush=True)
                self._model = SentenceTransformer(self.model_path)
            else:
                print(f"Загрузка предобученной модели", flush=True)
                self._model = SentenceTransformer('cointegrated/rubert-tiny2')
            
            test_embedding = self._model.encode("тест")
            self._dimension = len(test_embedding)
            print(f"Размерность эмбеддингов: {self._dimension}", flush=True)
        
        return self._model
    
    def generate_embedding(self, text: str) -> np.ndarray:
        if not text or text.strip() == "":
            return np.zeros(self.get_dimension(), dtype=np.float32)
        
        embedding = self.model.encode(text)
        return embedding.astype(np.float32)
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        if not texts:
            return []
        
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            return [np.zeros(self.get_dimension(), dtype=np.float32)] * len(texts)
        
        embeddings = self.model.encode(valid_texts)
        
        result = []
        text_idx = 0
        for text in texts:
            if text and text.strip():
                result.append(embeddings[text_idx].astype(np.float32))
                text_idx += 1
            else:
                result.append(np.zeros(self.get_dimension(), dtype=np.float32))
        
        return result
    
    def get_dimension(self) -> int:
        if self._dimension is None:
            _ = self.model
        return self._dimension or 312
    
    async def warmup(self):
        _ = self.model
        print("Модель векторного поиска готова", flush=True)
