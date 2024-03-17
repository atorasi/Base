import csv
import random 
import asyncio

from client import EtherClient
from utils import send_tg_message, get_eth_price, logger
from models import Network
from config import TELEGRAM_ALERTS, NEED_DELAY_ACC, DELAY_ACC


class Stats(EtherClient):
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
    async def save_stats(self, volume: int):
        csv_dict = {
            'address': self.address,
            'volume': round(await get_eth_price("usdt") * volume / 10**18, 5),
            'TxAmount': await self.w3.eth.get_transaction_count(self.address), 
            'Balance': round(await self.native_balance() / 10**18, 5),
        }
        
        logger.success(f"Acc.{self.index} --| Finished the route |-- ")

        with open('statistics.csv', 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=csv_dict.keys())
            writer.writerow(csv_dict)
        
        if TELEGRAM_ALERTS:
            await send_tg_message(
                f'<code>🤖 Account {self.index} | Finished running the wallet.</code> \n'
                f'<code>📖 Addr: {self.address}</code>\n\n'
                f'<code>💰 Volume: {round(await get_eth_price("usdt") * volume / 10**18, 5)} USD</code>\n'
                f'<code>🏦 Balance: {round(await self.native_balance() / 10**18, 5)} Ξ</code>\n'
                f'<code>🔄 TxAmount: {await self.w3.eth.get_transaction_count(self.address)} tx</code>\n'
                f'<code>🦺 Explorer:</code> <a href="https://basescan.org/address/{self.address}">Link</a>'
            )
            
        if NEED_DELAY_ACC:
            timeout = random.randint(DELAY_ACC[0], DELAY_ACC[1])
            logger.success(f"Acc.{self.index} --| Sleeping {timeout}s before next Acc |-- ")
            await asyncio.sleep(timeout)
        
        