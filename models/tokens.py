class Token:
    def __init__(self, symbol: str, address: str, decimals: int, woofi: str) -> None:
        self.symbol = symbol
        self.token_address = address
        self.decimals = decimals
        self.woofi = woofi
        self.zeroaddr = '0x0000000000000000000000000000000000000000'
    def __str__(self):
        return f'{self.name.upper()}'
        
ETH = Token(
    symbol='ETH',
    address='0x4200000000000000000000000000000000000006',
    decimals=18,
    woofi='0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',
)

USDBC = Token(
    symbol='USDBC',
    address="0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    decimals=6,
    woofi='0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA'
)

USDC = Token(
    symbol='USDC',
    address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    decimals=6,
    woofi='0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
)

DAI = Token(
    symbol='DAI',
    address="0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    decimals=18,
    woofi='0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
)

WBTC = Token(
    symbol='WBTC',
    address="0x3fe2b97c1fd336e750087d68b9b867997fd64a2661ff3ca5a7c771641e8e7ac",
    decimals=18,
    woofi='',
)

WETH = Token(
    symbol='WETH',
    address="0xD4a0e0b9149BCee3C920d2E00b5dE09138fd8bb7",
    decimals=18,
    woofi='0x4200000000000000000000000000000000000006',
)