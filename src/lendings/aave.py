from client import EtherClient
from models import Network, WETH

from utils import script_exceptions, abi_read, logger
from models import AAVE_ABI_JSON
from config import PERCENT_FOR_AAVE


class Aave(EtherClient):
    AAVE_ABI = abi_read(AAVE_ABI_JSON)
    
    CONTRACT_ADDRESS = "0x18cd499e3d7ed42feba981ac9236a278e4cdc2ee"
    POOL_ADDRESS = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
        self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.AAVE_ABI
        )
        
    @script_exceptions
    async def deposit_aave(self, value: int):
        tx = await self.contract_instance.functions.depositETH(
            self.w3.to_checksum_address(self.POOL_ADDRESS),
            self.address,
            0
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    @script_exceptions
    async def withdraw_aave(self):
        value = await self.token_balance(WETH.token_address)
        logger.info(f"Acc.{self.index} | Approving {self.w3.from_wei(value, 'ether')} WETH to withdraw")
        await self.approve_token(WETH.token_address, self.CONTRACT_ADDRESS)
        
        logger.info(f"Acc.{self.index} | Withdrawing {self.w3.from_wei(value, 'ether')} ETH.")
        tx = await self.contract_instance.functions.withdrawETH(
            self.w3.to_checksum_address(self.POOL_ADDRESS),
            value,
            self.address
        ).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    async def star_aave(self):
        logger.info(f"Acc.{self.index} | Starting Aave module.")
        
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_AAVE) / 100)
        logger.info(f"Acc.{self.index} | Making a deposit {self.w3.from_wei(value, 'ether')} ETH.")
        await self.deposit_aave(value)
        await self.withdraw_aave()
        
        return 2 * value
