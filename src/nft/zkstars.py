import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import Network, ZKSTARS_ABI_JSON
from config import ZKSTARS_CONTRACTS, MINT_COUNT_ZK


class ZkStars(EtherClient):
    CONTRACT_ADDRESS = random.choice(ZKSTARS_CONTRACTS)
    ZKSTARS_ABI = abi_read(ZKSTARS_ABI_JSON)
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
    @script_exceptions
    async def mint(self):
        self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.ZKSTARS_ABI
        )
        
        value = await self.contract_instance.functions.getPrice().call()
        mint_count = self.random_int(MINT_COUNT_ZK)
        
        for _ in range(mint_count):
            logger.info(f"Acc.{self.index} | Starting ZkStars module.")
            
            logger.info(f"Acc.{self.index} | Minting #{await self.contract_instance.functions.name().call()} NFT.")
            tx = await self.contract_instance.functions.safeMint(
                self.w3.to_checksum_address("0x6b44f3c60a39d70fd1a168ae1a61363d259c50f0")
            ).build_transaction({
                'chainId': self.network.chain_id,
                "from": self.address,
                "nonce": await self.w3.eth.get_transaction_count(self.address),
                "value": value,
                'gasPrice': await self.wait_for_gas(),
            })

            await self.send_transaction(tx)
        
        return value * mint_count