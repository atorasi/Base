import random
import ccxt.async_support as ccxt

from utils import script_exceptions
from config import OKX_SETTINGS, VALUE_OKX


class OkxWithdraw:
    @staticmethod
    @script_exceptions
    async def okx_withdraw(starknet_hex:  str) -> str:
        okx_options = {
            'apiKey': OKX_SETTINGS['apiKey'],
            'secret': OKX_SETTINGS['secret'],
            'password': OKX_SETTINGS['passwd'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            }
        }
        
        exchange_class = getattr(ccxt, 'okx')
        okx = exchange_class(okx_options)

        value = random.uniform(VALUE_OKX[0], VALUE_OKX[1])
        withdrawal_params = {
            "chainName": 'ETH-Base',
            "fee": 0.0002,
            "pwd": '-',
            "amt": value,
            "network": 'Base',
        }
        
        response = await okx.withdraw('ETH', value, starknet_hex, params=withdrawal_params)
        await okx.close()
        
        return response['txid']
