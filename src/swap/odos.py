import random

import httpx

from client import EtherClient
from utils import script_exceptions, logger
from models import Token, Network, ETH
from config import PERCENT_FOR_ODOS, SLIPPAGE, STABLES_LIST


class Odos(EtherClient):
    CONTRACT_ADDRESS = "0x19ceead7105607cd444f5ad10dd51356436095a1"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.proxies = {
            "http://": f"http://{self.proxy}",
            "https://": f"http://{self.proxy}",
        } 
        self.proxies = {
            "http://": f"http://rwltazzw:ux0bsr4ik4sj@216.158.205.50:6278",
            "https://": f"http://rwltazzw:ux0bsr4ik4sj@216.158.205.50:6278",
        } 
        
        
        self.headers = {"Content-Type": "application/json"}
        self.session = httpx.AsyncClient(proxies=self.proxies, headers=self.headers)
        
    @script_exceptions
    async def build_tx(self, from_token: str, to_token: str, value: int):
        quote_request_body = {
            "chainId": self.network.chain_id, 
            "inputTokens": [
                {
                    "tokenAddress": self.w3.to_checksum_address(from_token),
                    "amount": str(value),
                }
            ],
            "outputTokens": [
                {
                    "tokenAddress": self.w3.to_checksum_address(to_token),
                    "proportion": 1
                }
            ],
            "slippageLimitPercent": SLIPPAGE,
            "userAddr": self.address, 
            "referralCode": 3000000003, 
            "compact": True,
        }
        
        
        r = await self.session.post(
            "https://api.odos.xyz/sor/quote/v2",
            json=quote_request_body, 
        )
        
        return r.json()

    @script_exceptions
    async def get_tx_data(self, pool_addr: str):
        data = {
            "userAddr": self.address,
            "pathId": pool_addr,
            "simulate": False,
        }

        r = await self.session.post(
            url="https://api.odos.xyz/sor/assemble",
            json=data
        )

        return r.json()
        
    @script_exceptions
    async def swap(self, from_token: Token, to_token: Token, value: int):
        tx_params = await self.build_tx(
            from_token.token_address if from_token.symbol != "ETH" else from_token.zeroaddr,
            to_token.token_address if to_token.symbol != "ETH" else to_token.zeroaddr, 
            value)
        
        tx_data = await self.get_tx_data(tx_params["pathId"])

        tx = {
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": int(await self.native_balance() * 0.98),
            'gasPrice': await self.wait_for_gas(),
            "to": self.w3.to_checksum_address(tx_data["transaction"]["to"]),
            "data": tx_data["transaction"]["data"],
            "value": int(tx_data["transaction"]["value"]),
            "gas": int(tx_params["gasEstimate"])
        }

        await self.send_transaction(tx)
        
    async def start_odos(self):
        logger.info(f"Acc.{self.index} | Starting Odos module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_ODOS) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to Odos swap")
        await self.approve_token(token.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap(token, ETH, await self.token_balance(token.token_address))
        await self.session.aclose()

        return 2 * value
        