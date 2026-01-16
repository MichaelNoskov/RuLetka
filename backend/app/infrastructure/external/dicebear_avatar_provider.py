import aiohttp
import secrets
from typing import Optional
from urllib.parse import quote

from app.domain.ports.avatar_provider import AbstractAvatarProvider


class DiceBearBotttsProvider(AbstractAvatarProvider):
    
    BASE_URL = "https://api.dicebear.com/7.x/bottts/png"
    
    async def get_random(self) -> Optional[bytes]:
        seed = secrets.token_urlsafe(8)
        return await self._fetch_avatar(seed)
    
    async def get_by_name(self, username: str) -> Optional[bytes]:
        safe_username = quote(username, safe='')
        return await self._fetch_avatar(safe_username)
    
    async def _fetch_avatar(self, seed: str) -> Optional[bytes]:
        url = f"{self.BASE_URL}?seed={seed}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception:
            pass
        return None
