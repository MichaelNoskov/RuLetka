from abc import ABC, abstractmethod
import numpy as np
from typing import List


class AbstractVectorizer(ABC):
    
    @abstractmethod
    def generate_embedding(self, text: str) -> np.ndarray:
        pass
    
    @abstractmethod
    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        pass
