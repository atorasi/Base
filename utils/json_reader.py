import json


def abi_read(file: object) -> str:
    abi = json.loads(open(file).read())
    return abi
