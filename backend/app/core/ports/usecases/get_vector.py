from dataclasses import dataclass
from typing import Dict, Any, Optional
import json

from app.core.ports.repositories.vector_repository import AbstractVectorRepository
from app.core.ports.usecases.webrtc import GetVectorUseCase


@dataclass
class GetVectorUseCaseImpl(GetVectorUseCase):
    vector_repo: AbstractVectorRepository
    
    async def execute(
        self,
        user_id: str,
        target_user_id: str
    ) -> Dict[str, Any]:
        vector = await self.vector_repo.get_user_vector(target_user_id)
        
        if vector is None:
            return {"error": "Vector not found"}
        
        vector_list = vector.tolist() if hasattr(vector, 'tolist') else vector
        vector_json = json.dumps(vector_list, ensure_ascii=False)
        
        return {
            "user_id": target_user_id,
            "vector": vector_json,
            "vector_dimension": len(vector)
        }
