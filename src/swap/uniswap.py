import time
import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import UNISWAP_ABI_JSON, UNIAMOUNT_ABI_JSON, UNIPOOL_ABI_JSON, Token, Network, ETH
from config import PERCENT_FOR_UNI, SLIPPAGE, STABLES_LIST


class Uniswap(EtherClient):
    UNISWAP_ABI = abi_read(UNISWAP_ABI_JSON)
    UNIPOOL_ABI = abi_read(UNIPOOL_ABI_JSON)
    UNIAMOUNT_ABI = abi_read(UNIAMOUNT_ABI_JSON)
    
    CONTRACT_ADDRESS = "0x2626664c2603336E57B271c5C0b26F421741e481"
    POOL_CONTRACT = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
    AMOUNT_CONTRACT = "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.UNISWAP_ABI
        )
        self.pool_contract = self.w3.eth.contract(
            address=self.POOL_CONTRACT,
            abi=self.UNIPOOL_ABI
        )
        self.amount_contract = self.w3.eth.contract(
            address=self.AMOUNT_CONTRACT,
            abi=self.UNIAMOUNT_ABI
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
        quoter_data = await self.amount_contract.functions.quoteExactInputSingle((
            self.w3.to_checksum_address(from_token.token_address),
            self.w3.to_checksum_address(to_token.token_address),
            value,
            500,
            0
        )).call()

        return int(quoter_data[0] * (100 - SLIPPAGE) / 100)
    
    @script_exceptions
    async def swap_from_eth(self, from_token: Token, to_token: Token, value: int):
        deadline = int(time.time()) + 1000000

        tx_data = self.contract_instance.encodeABI(
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
            deadline, 
            [tx_data]
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value,
            'gasPrice': await self.wait_for_gas(),
        })

        return await self.send_transaction(tx)
    
    @script_exceptions
    async def swap_to_eth(self, from_token: Token, to_token: Token, value: int):
        deadline = int(time.time()) + 1000000
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
            args=[
                value_out,
                self.address
            ]

        )

        tx = await self.contract_instance.functions.multicall(
            deadline,
            [transaction_data, unwrap_weth]
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })

        return await self.send_transaction(tx)
    
    async def start_uniswap(self):
        logger.info(f"Acc.{self.index} | Starting Uniswap module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_UNI) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap_from_eth(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to Uniswap swap")
        await self.approve_token(token.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap_to_eth(token, ETH, await self.token_balance(token.token_address))
        
        return 2 * value