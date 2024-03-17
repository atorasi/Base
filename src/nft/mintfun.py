import random

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import Network, MINTFUN_ABI_JSON
from config import MINTFUN_CONTRACTS, MINT_COUNT_MF


class MintFun(EtherClient):
    CONTRACT_ADDRESS = random.choice(MINTFUN_CONTRACTS)
    MINTFUN_ABI = abi_read(MINTFUN_ABI_JSON)
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)

    @script_exceptions
    async def mint(self):
        self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.MINTFUN_ABI
        )
        value = await self.contract_instance.functions.getPrice().call()
        mint_count = self.random_int(MINT_COUNT_MF)
        logger.info(f"Acc.{self.index} | Starting MintFun module.")
        for _ in range(mint_count):
            self.contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            abi=self.MINTFUN_ABI
        )
            logger.info(f"Acc.{self.index} | Minting #{await self.contract_instance.functions.name().call()} NFT.")
            
            tx = await self.contract_instance.functions.mint(
                self.address
            ).build_transaction({
                'chainId': self.network.chain_id,
                "from": self.address,
                "nonce": await self.w3.eth.get_transaction_count(self.address),
                "value": value,
                'gasPrice': await self.wait_for_gas(),
            })

            await self.send_transaction(tx)
            
        return value * mint_count