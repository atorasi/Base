import asyncio
import random

from web3 import AsyncWeb3

from utils import script_exceptions, abi_read, logger, send_tg_message
from models import Network, TOKEN_ABI_JSON, Ethereum
from config import NEED_DELAY_ACT, DELAY_ACT, USE_PROXY, TELEGRAM_ALERTS


class EtherClient:
    TOKEN_ABI: str = abi_read(TOKEN_ABI_JSON)
    
    def __init__(self, index: int, network: Network, private: str, proxy: str = None) -> None:
        self.index = index
        self.network = network
        self.rpc = network.rpc
        self.proxy = proxy
        self.request_kwargs = None
        if USE_PROXY:
            self.request_kwargs = {"proxy": f"http://{self.proxy}"}
            
            self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(
                endpoint_uri=self.rpc,
                request_kwargs=self.request_kwargs,
            )
        )

        else:
            self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc))
        
        self.private_key = private
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.address = self.account.address

    @staticmethod
    def random_int(lst: list) -> int:
        return random.randint(lst[0], lst[1])
    
    @staticmethod
    def random_float(lst: list) -> int:
        return random.uniform(lst[0], lst[1])
    
    @script_exceptions
    async def wait_for_gas(self) -> int:
        while True:
            gas = await self.w3.eth.gas_price
            if gas / 1_000_000_000 > Ethereum.need_gas:
                await asyncio.sleep(10)
            return gas
        
    @script_exceptions
    async def native_balance(self) -> int:
        balance = await self.w3.eth.get_balance(self.address)
        
        return balance

    @script_exceptions
    async def token_balance(self, token_address: str) -> float:
        contract_instance = self.w3.eth.contract(
            address=self.w3.to_checksum_address(token_address), 
            abi=EtherClient.TOKEN_ABI
        )
        
        return await contract_instance.functions.balanceOf(self.address).call()

    @script_exceptions
    async def send_transaction(self, transaction: dict) -> str:
        if self.network.name == "base":
            del transaction['gasPrice']
            
            gas = int(await self.w3.eth.estimate_gas(transaction) * 1.3)
            max_fee_per_gas = await self.wait_for_gas()
            max_priority_fee_per_gas = self.w3.to_wei(self.network.need_gas, "gwei") 
            
            transaction.update(
                {
                    "gas": gas,
                    "maxFeePerGas": max_fee_per_gas,
                    "maxPriorityFeePerGas": max_priority_fee_per_gas,
                }
            )
        
        sign_tx = self.account.sign_transaction(transaction)
        tx_hash = self.w3.to_hex(await self.w3.eth.send_raw_transaction(sign_tx.rawTransaction))
        await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if NEED_DELAY_ACT:
            delay_ = self.random_int(DELAY_ACT)
            logger.debug(f"Acc.{self.index} | Sleep {delay_} sec before next activity")
            await asyncio.sleep(delay_)
        
        logger.success(f"Acc.{self.index} | Transaction Hash: {self.network.scan}tx/{tx_hash}")
        if TELEGRAM_ALERTS:
            await send_tg_message(
                f"<code>Account {self.index} | {self.network.symbol} | NEW TRANSACTION | {str(self.address)[:6]}...{str(self.address)[-4:]}</code> \n"
                f"https://basescan.org/tx/{tx_hash}"
            )
            
        return tx_hash
        
    @script_exceptions
    async def send_native_token(self, to_address: str, value: int | float) -> str:
        tx = {
            'from': self.address,
            'to': self.w3.to_checksum_address(to_address),
            'gasPrice': await self.wait_for_gas(),
            'nonce': await self.w3.eth.get_transaction_count(self.address),
            'value': value,
            'chainId': self.network.chain_id,
        }
        gas = int(await self.w3.eth.estimate_gas(tx) * 1.1)
        tx.update({"gas": gas})
        return await self.send_transaction(tx)
    
    @script_exceptions
    async def send_token(self, to_address: str, value: int | float, token_address: str) -> str:
        token_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(token_address), abi=self.TOKEN_ABI)
        
        tx = token_contract.functions.transfer(to_address, value).buildTransaction({
            'from': self.address,
            'to': to_address,
            'gasPrice': await self.wait_for_gas(),
            'nonce': await self.w3.eth.get_transaction_count(self.address),
            'value': self.w3.to_wei(value, 'ether'),
            'gas': 21000,
            'chainId': self.network.chain_id,
        })
        
        return await self.send_transaction(tx)
        
    @script_exceptions
    async def approve_token(self, token: str, contract_address: str) -> str: 
        contract_instance = self.w3.eth.contract(address=self.w3.to_checksum_address(token), abi=self.TOKEN_ABI)
        value = await self.token_balance(token)
        
        tx = await contract_instance.functions.approve(self.w3.to_checksum_address(contract_address), value).build_transaction({
            "gasPrice": await self.wait_for_gas(),
            "from": self.address,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "value": 0,
        })
        
        return await self.send_transaction(tx)
    