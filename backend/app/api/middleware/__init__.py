from fastapi import FastAPI
from .security import SecurityMiddleware

def setup_security_middleware(
    app: FastAPI,
    token_provider,
    public_paths: list[str] = None
):
    app.add_middleware(
        SecurityMiddleware,
        token_provider=token_provider,
        public_paths=public_paths
    )
