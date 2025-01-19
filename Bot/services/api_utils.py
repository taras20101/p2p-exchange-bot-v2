import logging
import aiohttp
from typing import Dict, Optional

logger = logging.getLogger(__name__)

async def make_request(url: str, method: str = 'GET', headers: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API помилка {response.status}: {await response.text()}")
                    return None
    except Exception as e:
        logger.error(f"Помилка запиту: {str(e)}")
        return None 