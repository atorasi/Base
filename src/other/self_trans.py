from client import EtherClient
from models import Network

from utils import script_exceptions, logger
from config import PERCENT_FOR_SELF_TRANS


class SelfTrans(EtherClient):
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
    
    @script_exceptions
    async def self_transactions(self, value):
        await self.send_native_token(self.address, value)
        
    async def start_self_module(self) -> int:
        logger.info(f"Acc.{self.index} | Starting self.Transactions module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_SELF_TRANS) / 100)
        
        logger.info(f"Acc.{self.index} | Sending {self.w3.from_wei(value, 'ether')}ETH .")
        await self.self_transactions(value)
        
        return value
        
        