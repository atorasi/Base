import random
import string

from client import EtherClient
from models import Network

from utils import script_exceptions, abi_read, logger
from models import DMAIL_ABI_JSON
from config import PERCENT_FOR_AERO


class Dmail(EtherClient):
    DMAIL_ABI = abi_read(DMAIL_ABI_JSON)
    CONTRACT_ADDRESS = "0x47fbe95e981C0Df9737B6971B451fB15fdC989d9"
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
    
        self.contract_instance = self.w3.eth.contract(
            address=self.CONTRACT_ADDRESS,
            abi=self.DMAIL_ABI
        )
        
    @staticmethod
    def get_random_string(digits) -> str:
        letters = string.ascii_lowercase
        result_str = "".join(random.choice(letters) for i in range(digits))
        
        return result_str
    
    def generate_dmail(self) -> list:
        email = f"{self.get_random_string(7)} + gmail.com"
        message = self.get_random_string(random.randint(12, 30))
        
        return email, message
    
    @script_exceptions  
    async def send_dmail(self) -> str:
        logger.info(f"Acc.{self.index} | Starting Dmail module.")
        logger.info(f"Acc.{self.index} | Generating email and message.")
        email, msg = self.generate_dmail()
        data = self.contract_instance.encodeABI("send_mail", args=(email, msg))
        
        tx = {   
            "data": data, 
            "to": self.w3.to_checksum_address(self.CONTRACT_ADDRESS),
            'chainId': self.network.chain_id,
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
            'gasPrice': await self.wait_for_gas(),
            "gas": 30000
        }
        
        await self.send_transaction(tx)

        return 0
    