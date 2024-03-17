import time
import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import MAVERICK_ABI_JSON, MAVERICKINFO_ABI_JSON, Token, Network, ETH
from config import PERCENT_FOR_MAV, SLIPPAGE, STABLES_LIST


class Maverick(EtherClient):
    MAVERICK_ABI = abi_read(MAVERICK_ABI_JSON)
    MAVERICKINFO_ABI = abi_read(MAVERICKINFO_ABI_JSON)

    CONTRACT_ADDRESS = "0x32AED3Bce901DA12ca8489788F3A99fCe1056e14"
    POOL_CONTRACT = "0x6E230D0e457Ea2398FB3A22FB7f9B7F68F06a14d"
    
    MAV_CONTRACT = "0x06e6736ca9e922766279a22b75a600fe8b8473b6"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.MAVERICK_ABI
        )
        self.pool_contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.POOL_CONTRACT),
            abi=self.MAVERICKINFO_ABI
        )
        
    def get_path(self, from_token: str, to_token: str):
        path_data = [
            self.w3.to_checksum_address(from_token),
            self.w3.to_checksum_address(self.MAV_CONTRACT),
            self.w3.to_checksum_address(to_token),
        ]
        
        return b"".join([bytes.fromhex(address[2:]) for address in path_data])
    
    @script_exceptions
    async def get_out_value(self, value: int, from_token: bool):
        amount = await self.pool_contract.functions.calculateSwap(
            self.w3.to_checksum_address(self.MAV_CONTRACT),
            value,
            from_token,
            True,
            0
        ).call()
        
        return int(amount / 100 * (100 - SLIPPAGE))
    
    @script_exceptions
    async def swap_from_eth(self, from_token: Token, to_token: Token, value: int):
        deadline = int(time.time()) + 1000000
        value_out = await self.get_out_value(value, False)

        transaction_data = self.contract_instance.encodeABI(
            fn_name="exactInput",
            args=[(
                self.get_path(
                    from_token.token_address, 
                    to_token.token_address
                ),
                self.address,
                deadline,
                value,
                value_out
            )]
        )
        refund_eth = self.contract_instance.encodeABI(
            fn_name="refundETH"
        )

        tx = await self.contract_instance.functions.multicall(
            [transaction_data, refund_eth]
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
        value_out = await self.get_out_value(value, True)

        transaction_data = self.contract_instance.encodeABI(
            fn_name="exactInput",
            args=[(
                self.get_path(
                    from_token.woofi, 
                    to_token.token_address
                ),
                self.w3.to_checksum_address(to_token.zeroaddr),
                deadline,
                value,
                value_out
            )]
        )
        unwrap_weth = self.contract_instance.encodeABI(
            fn_name="unwrapWETH9",
            args=[0,self.address]
        )

        tx = await self.contract_instance.functions.multicall(
            [transaction_data, unwrap_weth]
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })

        return await self.send_transaction(tx)
    
    async def start_maverick(self):
        logger.info(f"Acc.{self.index} | Starting Maverick module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_MAV) / 100)
        token = random.choice(STABLES_LIST)
        
        logger.info(f"Acc.{self.index} | Making swap from ETH to {token.symbol}.")
        await self.swap_from_eth(ETH, token, value)
        
        logger.info(f"Acc.{self.index} | Approving {token.symbol} to Maverick swap")
        await self.approve_token(token.woofi, self.CONTRACT_ADDRESS)

        logger.info(f"Acc.{self.index} | Making swap from {token.symbol} to ETH.")
        await self.swap_to_eth(token, ETH, await self.token_balance(token.woofi))
        
        return 2 * value