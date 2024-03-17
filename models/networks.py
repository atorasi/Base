class Network:
    def __init__(self, 
            name: str, rpc: str, chain_id: int, coin_symbol: str, 
            explorer: str, symbol: str, need_gas: int, orbiter_address: str = None):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.coin_symbol = coin_symbol
        self.scan = explorer
        self.orbiter_address = orbiter_address
        self.need_gas = need_gas
        self.symbol = symbol
        
    def __str__(self):
        return f'{self.name.upper()}'

Ethereum = Network(
    name='ethereum',
    rpc='https://eth.llamarpc.com', 
    chain_id=1,
    coin_symbol='ETH',
    explorer='https://etherscan.io/',
    orbiter_address='',
    need_gas=43,
    symbol="ETHER",
)

Arbitrum = Network(
    name='arbitrum',
    rpc='https://rpc.ankr.com/arbitrum/',
    chain_id=42161,
    coin_symbol='ETH',
    explorer='https://arbiscan.io/',
    orbiter_address='0x80c67432656d59144ceff962e8faf8926599bcf8',
    need_gas=1000,
    symbol="ARBI",
)

Optimism = Network(
    name='optimism',
    rpc='https://rpc.ankr.com/optimism/',
    chain_id=10,
    coin_symbol='ETH',
    explorer='https://optimistic.etherscan.io/',
    orbiter_address='0xe4edb277e41dc89ab076a1f049f4a3efa700bce8',
    need_gas=1000,
    symbol="OPTI",
)

Base = Network(
    name='base',
    rpc='https://endpoints.omniatech.io/v1/base/mainnet/public',
    chain_id=8453,
    coin_symbol='ETH',
    explorer='https://basescan.org/',
    orbiter_address='',
    need_gas=0.001,
    symbol="BASE",
)
