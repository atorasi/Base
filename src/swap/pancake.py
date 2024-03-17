import time
import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import PANCAKE_ABI_JSON, CAKEPOOL_ABI_JSON, CAKEAMOUNT_ABI_JSON, Token, Network, ETH
from config import PERCENT_FOR_CAKE, SLIPPAGE, STABLES_LIST


class Pancake(EtherClient):
    PANCAKE_ABI = abi_read(PANCAKE_ABI_JSON)
    CAKEPOOL_ABI = abi_read(CAKEPOOL_ABI_JSON)
    CAKEAMOUNT_ABI = abi_read(CAKEAMOUNT_ABI_JSON)
    
    CONTRACT_ADDRESS = "0x678Aa4bF4E210cf2166753e054d5b7c31cc7fa86"
    POOL_CONTRACT = "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"
    AMOUNT_CONTRACT = "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.PANCAKE_ABI
        )
        self.pool_contract = self.w3.eth.contract(
            address=self.POOL_CONTRACT,
            abi=self.CAKEPOOL_ABI
        )
        self.amount_contract = self.w3.eth.contract(
            address=self.AMOUNT_CONTRACT,
            abi=self.CAKEAMOUNT_ABI
        )
        
    @script_exceptions
    async def get_pool(self, from_token: Token, to_token: Token):
        return await self.pool_contract.functions.getPool(
            self.w3.to_checksum_address(from_token.token_address),
            self.w3.to_checksum_address(to_token.token_address),
            500
        ).call()

    @script_exceptions
    async def get_out_value(self, from_token: Token, to_token: Token, value: int):
        value_min = await self.amount_contract.functions.quoteExactInputSingle((
            self.w3.to_checksum_address(from_token.token_address),
            self.w3.to_checksum_address(to_token.token_address),
            value,
            500,
            0
        )).call()

        return int(value_min[0] / 100 * (100 - SLIPPAGE))
    
    @script_exceptions
    async def swap_from_eth(self, from_token: Token, to_token: Token, value: int):
        transaction_data = self.contract_instance.encodeABI(
            fn_name="exactInputSingle",
            args=[(
                self.w3.to_checksum_address(from_token.token_address),
                self.w3.to_checksum_address(to_token.token_address),
                500,
                self.address,
                value,
                await self.get_out_value(from_token, to_token, value),
                0
            )]
        )

        tx = await self.contract_instance.functions.multicall(
            int(time.time()) + 1000000, 
            [transaction_data]
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
        value_out = await self.get_out_value(from_token, to_token, value)

        transaction_data = self.contract_instance.encodeABI(
            fn_name="exactInputSingle",
            args=[(
                self.w3.to_checksum_address(from_token.token_address),
                self.w3.to_checksum_address(to_token.token_address),
                500,
                "0x0000000000000000000000000000000000000002",
                value,
                value_out,
                0
            )]
        )
        unwrap_weth = self.contract_instance.encodeABI(
            fn_name="unwrapWETH9",
            args=[value_out, self.address]
        )

        tx = await self.contract_instance.functions.multicall(
            int(time.time()) + 1000000,
            [transaction_data, unwrap_weth]
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })

        return await self.send_transaction(tx)
    
    async def start_pancake(self):
        logger.info(f"Acc.{self.index} | Starting Pancake module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_CAKE) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap_from_eth(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to Pancake swap")
        await self.approve_token(token.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap_to_eth(token, ETH)
        
        return 2 * value