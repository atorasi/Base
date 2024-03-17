from client import EtherClient
from models import Network

from utils import script_exceptions, abi_read, logger
from models import WRAP_ETH_ABI_JSON
from config import PERCENT_FOR_AERO


class WrapModule(EtherClient):
    WRAP_ETH_ABI = abi_read(WRAP_ETH_ABI_JSON)
    CONTRACT_ADDRESS = "0x4200000000000000000000000000000000000006"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
    
    @script_exceptions  
    async def wrap_eth(self, value: int) -> str:
        contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.WRAP_ETH_ABI
        )
        
        tx = await contract_instance.functions.deposit().build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": value,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    @script_exceptions  
    async def unwrap_eth(self, value: int) -> str:
        
        contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.WRAP_ETH_ABI
        )
        
        tx = await contract_instance.functions.withdraw(value).build_transaction({
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
        })
        
        return await self.send_transaction(tx)
    
    async def wrap_module_start(self):
        logger.info(f"Acc.{self.index} | Starting Aerodrome Wrap|Unwrap ETH module.")
        value = int(await self.native_balance() * self.random_int(PERCENT_FOR_AERO) / 100)
        logger.info(f"Acc.{self.index} | Wrapping ETH")
        wrap_hash = await self.wrap_eth(value)
        logger.info(f"Acc.{self.index} | Unwrapping ETH")
        unwrap_hash = await self.unwrap_eth(value)

        return 2 * value