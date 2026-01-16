from abc import ABC, abstractmethod

class AbstractTokenProvider(ABC):
    
    @abstractmethod
    def create(self, user_id: int) -> str:
        pass
    
    @abstractmethod  
    def verify(self, token: str) -> dict:
        pass
