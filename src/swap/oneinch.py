import random

import httpx

from client import EtherClient
from utils import script_exceptions, logger
from models import Token, Network, ETH
from config import PERCENT_FOR_INCH, SLIPPAGE, STABLES_LIST, INCH_API_KEY


class OneInch(EtherClient):
    CONTRACT_ADDRESS = "0x1111111254eeb25477b68fb85ed929f73a960582"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.headers = {"Authorization": f"Bearer {INCH_API_KEY}", "accept": "application/json"}

    async def build_tx(self, from_token: str, to_token: str, amount: int):
        url = f"https://api.1inch.dev/swap/v5.2/{self.network.chain_id}/swap"

        params = {
            "src": self.w3.to_checksum_address(from_token),
            "dst": self.w3.to_checksum_address(to_token),
            "amount": amount,
            "from": self.address,
            "slippage": SLIPPAGE,
            "referrer": self.w3.to_checksum_address("0x6b44f3c60a39d70fd1a168ae1a61363d259c50f0"),
            "fee": 1
        }

        async with httpx.AsyncClient() as session:
            r = await session.get(url, params=params, headers=self.headers)

            return r.json()

    @script_exceptions
    async def swap(self, from_token: Token, to_token: Token, value: int):
        tx_params = await self.build_tx(
            from_token.token_address if from_token.symbol != "ETH" else from_token.woofi,
            to_token.token_address if to_token.symbol != "ETH" else to_token.woofi,
            value
        )
        
        tx = {
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": int(await self.native_balance() * 0.98),
            'gasPrice': await self.wait_for_gas(),
            "to": self.w3.to_checksum_address(tx_params["tx"]["to"]),
            "data": tx_params["tx"]["data"],
            "value": int(tx_params["tx"]["value"]),
            "gas": tx_params["tx"]["gas"]
        }

        await self.send_transaction(tx)
        
    async def start_inch(self):
        logger.info(f"Acc.{self.index} | Starting 1Inch module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_INCH) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to 1Inch swap")
        await self.approve_token(token.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap(token, ETH, await self.token_balance(token.token_address))
        
        return 2 * value