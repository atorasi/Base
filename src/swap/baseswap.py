import time
import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import BASESWAP_ABI_JSON, Token, Network, ETH
from config import PERCENT_FOR_BS, SLIPPAGE, STABLES_LIST


class BaseSwap(EtherClient):
    BASESWAP_ABI = abi_read(BASESWAP_ABI_JSON)
    CONTRACT_ADDRESS = "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.BASESWAP_ABI
        )
        
    @script_exceptions
    async def get_out_value(self, from_token: Token, to_token: Token, amount: int):
        min_amount_out = await self.contract_instance.functions.getAmountsOut(
            amount,
            [
                self.w3.to_checksum_address(from_token.token_address),
                self.w3.to_checksum_address(to_token.token_address)
            ]
        ).call()
        
        return int(min_amount_out[1] / 100 * (100 - SLIPPAGE))
    
    @script_exceptions
    async def swap_from_eth(self, from_token: Token, to_token: Token, value: int):
        deadline = int(time.time() + 1000000)
        amount_out = await self.get_out_value(from_token, to_token, value)
        
        tx = await self.contract_instance.functions.swapExactETHForTokens(
            amount_out,
            [
                self.w3.to_checksum_address(from_token.token_address),
                self.w3.to_checksum_address(to_token.token_address)
            ],
            self.address,
            deadline
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    @script_exceptions
    async def swap_to_eth(self, from_token: Token, to_token: Token):
        value = await self.token_balance(from_token.token_address)
        deadline = int(time.time() + 1000000)
        amount_out = await self.get_out_value(from_token, to_token, value)
        
        tx = await self.contract_instance.functions.swapExactTokensForETH(
            value,
            amount_out,
            [
                self.w3.to_checksum_address(from_token.token_address),
                self.w3.to_checksum_address(to_token.token_address)
            ],
            self.address,
            deadline
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
        
    async def start_baseswap(self):
        logger.info(f"Acc.{self.index} | Starting Baseswap module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_BS) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap_from_eth(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to BaseSwap swap")
        await self.approve_token(token.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap_to_eth(token, ETH)
        
        return 2 * value