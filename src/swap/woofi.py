import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import WOOFI_ABI_JSON, Token, Network, ETH
from config import PERCENT_FOR_WOOFI, SLIPPAGE, STABLES_LIST


class WooFi(EtherClient):
    WOOFI_ABI = abi_read(WOOFI_ABI_JSON)
    CONTRACT_ADDRESS = "0x27425e9FB6A9A625E8484CFD9620851D1Fa322E5"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.WOOFI_ABI
        )
        
    @script_exceptions
    async def get_value(self, from_token: Token, to_token: Token, value: int):
        min_amount_out = await self.contract_instance.functions.querySwap(
            self.w3.to_checksum_address(from_token.woofi),
            self.w3.to_checksum_address(to_token.woofi),
            value
        ).call()

        return int(min_amount_out / 100 * (100 - SLIPPAGE))
    
    @script_exceptions
    async def swap(self, from_token: Token, to_token: Token, value: int):
        tx = await self.contract_instance.functions.swap(
            self.w3.to_checksum_address(from_token.woofi),
            self.w3.to_checksum_address(to_token.woofi),
            value,
            await self.get_value(from_token, to_token, value),
            self.address,
            self.address
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value if from_token.symbol == "ETH" else 0,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    async def start_woofi(self):
        logger.info(f"Acc.{self.index} | Starting WooFi module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_WOOFI) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to WooFi swap")
        await self.approve_token(token.woofi, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap(token, ETH, await self.token_balance(token.woofi))
        
        return 2 * value