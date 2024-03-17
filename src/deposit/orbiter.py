import httpx

from client import EtherClient
from utils import script_exceptions, abi_read, logger
from models import Network, BRIDGEWITHDRAWAL_ABI_JSON
from config import VALUE_TO_WITHDRAWAL


class Orbiter(EtherClient):
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        super().__init__(index, network, private, proxy)
        
    @script_exceptions
    async def get_bridge_amount(self, value: float):
        self.session = httpx.AsyncClient(headers={"Content-Type": "application/json"})
        
        json_data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "orbiter_calculatedAmount",
            "params": [
                f"{self.network.chain_id}-8453:ETH-ETH", 
                float(value)
            ]
        }

        r = await self.session.post(
            url="https://openapi.orbiter.finance/explore/v3/yj6toqvwh1177e1sexfy0u1pxx5j8o47",
            json=json_data,
        )

        tx_data = r.json()

        if tx_data["result"].get("error") is None:
            await self.session.aclose()
            return int(tx_data["result"]["_sendValue"])

            
    @script_exceptions
    async def bridge_orbiter(self):
        value = await self.get_bridge_amount(self.random_float(VALUE_TO_WITHDRAWAL))
        await self.send_native_token(self.network.orbiter_address, value)
    