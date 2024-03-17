import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.absolute()

ABIDIR = os.path.join(ROOT_DIR, "abies")
WALLETSDIR = os.path.join(ROOT_DIR, "data")

ETHER_WALLETS = os.path.join(WALLETSDIR, "private_keys.txt")
PROXY_LIST = os.path.join(WALLETSDIR, "proxy.txt")
WITHDRAW_LIST = os.path.join(WALLETSDIR, "withdrawal_address.txt")



TOKEN_ABI_JSON = os.path.join(ABIDIR, "evm_token.json")
WRAP_ETH_ABI_JSON = os.path.join(ABIDIR, "wrapeth.json")
BASESWAP_ABI_JSON = os.path.join(ABIDIR, "baseswap.json")
AAVE_ABI_JSON = os.path.join(ABIDIR, "aave.json")
WOOFI_ABI_JSON = os.path.join(ABIDIR, "woofi.json")
PANCAKE_ABI_JSON = os.path.join(ABIDIR, "pancake.json")
CAKEPOOL_ABI_JSON = os.path.join(ABIDIR, "cakepool.json")
CAKEAMOUNT_ABI_JSON = os.path.join(ABIDIR, "cakeamount.json")
ZKSTARS_ABI_JSON = os.path.join(ABIDIR, "zkstars.json")
BRIDGEWITHDRAWAL_ABI_JSON = os.path.join(ABIDIR, "bridgewithdraw.json")
UNISWAP_ABI_JSON = os.path.join(ABIDIR, "uniswap.json")
UNIPOOL_ABI_JSON = os.path.join(ABIDIR, "unipool.json")
UNIAMOUNT_ABI_JSON = os.path.join(ABIDIR, "uniamount.json")
MAVERICK_ABI_JSON = os.path.join(ABIDIR, "maverick.json")
MAVERICKINFO_ABI_JSON = os.path.join(ABIDIR, "maverickinfo.json")
ALIENSWAP_ABI_JSON = os.path.join(ABIDIR, "alienswap.json")
MINTFUN_ABI_JSON = os.path.join(ABIDIR, "mintfun.json")
DMAIL_ABI_JSON = os.path.join(ABIDIR, "dmail.json")

