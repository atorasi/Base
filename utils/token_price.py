import httpx

from .logger_file import logger

async def get_eth_price(token: str) -> float:
    token = token.upper()
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f'https://api.binance.com/api/v3/depth?limit=1&symbol=ETH{token}')
                if response.status_code != 200:
                    continue
                
                return float(response.json()['asks'][0][0])
        except Exception:
            logger.debug(f'Error in request to get token price')
    