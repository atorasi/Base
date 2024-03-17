import asyncio
import random

from client import EtherClient
from models import ETHER_WALLETS, PROXY_LIST, Base, WITHDRAW_LIST
from config import USE_PROXY, TELEGRAM_ALERTS, NEED_DEPOSIT, USE_OKX, NUM_THREADS, TEXT, ORBITER_CHAINS, PERCENT_TO_W
from utils import logger, send_tg_message, random_pattern
from src import *


with open(ETHER_WALLETS, 'r') as file:
    evm_keys = [key.strip() for key in file]
    
list_proxy = [None] * len(evm_keys)
if USE_PROXY:
    with open(PROXY_LIST, 'r') as file:
        list_proxy = [proxy.strip() for proxy in file]
    

with open(WITHDRAW_LIST, 'r') as file:
    w_addr = [key.strip() for key in file]

async def run_script(index: int, evm_private: str, proxy: str) -> None:
    logger.info(f'~~~~~~~~~~~~~~~~~~~ Account - {index} ~~~~~~~~~~~~~~~~~~~')
        
    data = index, Base, evm_private, proxy    
    client = EtherClient(*data)
    
    if TELEGRAM_ALERTS:
        await send_tg_message(f'<code>Account {index} | Starting the script.</code>')
        
    balance_start = await client.native_balance()
    
    if NEED_DEPOSIT:
        if USE_OKX:
            logger.info(f'Acc.{index} | Preparing Funds to OKX Withdraw')
            await OkxWithdraw().okx_withdraw(client.address)
        else:
            logger.info(f'Acc.{index} | Preparing Funds to Orbiter')
            await Orbiter(index, random.choice(ORBITER_CHAINS), evm_private, proxy).bridge_orbiter()

        while await client.native_balance() == balance_start:
            await asyncio.sleep(13)
            
        logger.success(f"Acc.{index} | Funds have been credited to the wallet balance.")
    
    modules_dict = {
        'dmail': (Dmail, 'send_dmail'),
        'aave': (Aave, 'star_aave'),
        'mintfun': (MintFun, 'mint'),
        'zkstars': (ZkStars, 'mint'),
        'aero': (WrapModule, 'wrap_module_start'),
        'baseswap': (BaseSwap, 'start_baseswap'),
        'maverick': (Maverick, 'start_maverick'),
        'odos': (Odos, 'start_odos'),
        'inch': (OneInch, 'start_inch'),
        'pancake': (Pancake, 'start_pancake'),
        'uniswap': (Uniswap, 'start_uniswap'),
        'woofi': (WooFi, 'start_woofi'),
        'self_trans': (SelfTrans, 'start_self_module')
    }
    
    logger.info(f"Acc.{index} | Beginning to perform actions on Base.")
    route, volume = random_pattern(), 0
    
    for module in route:
        module_class, method_name = modules_dict[module]
        method = getattr(module_class(*data), method_name)
        
        volume += await method()
        
    await client.send_native_token(w_addr[index-1], int(await client.native_balance() * client.random_int(PERCENT_TO_W) / 100))
    await Stats(*data).save_stats(volume)
    

async def main():
    tasks = []
    for index, (evm_private, proxy) in enumerate(zip(evm_keys, list_proxy), start=1):
        task = run_script(index, evm_private, proxy)
        tasks.append(task)

        if len(tasks) == NUM_THREADS:
            await asyncio.gather(*tasks)
            tasks.clear()

    if tasks:
        await asyncio.gather(*tasks)
        
        
if __name__ == '__main__':
    print(f'{TEXT}\n\n')
    
    asyncio.run(main())
    
    print('\n\nThank you for using the software. </3')
    input('\nPress "ENTER" To Exit..')
