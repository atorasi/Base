import httpx 

from config import BOT_TOKEN, CHAT_ID
from .logger_file import logger

async def send_tg_message(text : str) -> None:
    try:
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        data = {
            'chat_id': CHAT_ID, 
            'text': text,
            'parse_mode': 'HTML',
            'disable_web_page_preview': True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
    except:
        logger.error(f'Error in request to send stats')
