#!/usr/bin/env python3
from json import loads, dumps
from sys import exit, argv
import base64, requests, json


if len(argv) < 5:
    print('Arguments: <rpc_username> <rpc_password> <rpc domain name> <rpc_port>')
    sys.exit(1)

# From electrum-cat.
def bits_to_target(bits: int) -> int:
        # arith_uint256::SetCompact in Bitcoin Core
        if not (0 <= bits < (1 << 32)):
            print(f"bits should be uint32. got {bits!r}")
            sys.exit(1)
        bitsN = (bits >> 24) & 0xff
        bitsBase = bits & 0x7fffff
        if bitsN <= 3:
            target = bitsBase >> (8 * (3-bitsN))
        else:
            target = bitsBase << (8 * (bitsN-3))
        if target != 0 and bits & 0x800000 != 0:
            # Bit number 24 (0x800000) represents the sign of N
            print("target cannot be negative")
            sys.exit(1)
        if (target != 0 and
                (bitsN > 34 or
                (bitsN > 33 and bitsBase > 0xff) or
                (bitsN > 32 and bitsBase > 0xffff))):
            print("target has overflown")
            sys.exit(1)
        return target

def rpc(method, params):
    data = json.dumps({
        "jsonrpc": "1.0",
        "id":"curltest",
        "method": method,
        "params": params
    })

    data_json = dumps(data)
    username = argv[1]
    password = argv[2]
    https_domain_or_ip = argv[3]
    port = argv[4]
    url = f"http://{https_domain_or_ip}:{port}"

    headers = {
        'content-type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=data, auth=(username, password))
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Call to rpc ({url}) for block {params} didn't produce expected result. HTTP status code {response.status_code}")

# Electrum-CAT checkpoints are blocks 2015, 2015 + 2016, 2015 + 2016*2, ...
i = 2015
INTERVAL = 2016

checkpoints = []
block_count = int(rpc('getblockcount', [])['result'])
print(('Blocks: {}'.format(block_count)))
while True:
    h = rpc('getblockhash', [i])['result']
    block = rpc('getblock', [h])['result']

    # Electrum-CAT includes timestamp in the checkpoint json
    checkpoints.append([
        block['hash'],
        bits_to_target(int(block['bits'], 16)),
        block['time']
    ])

    print(f"At block {i}")
    i += INTERVAL
    if i > block_count:
        print('Done.')
        break

with open('checkpoints_output.json', 'w+') as f:
    f.write(dumps(checkpoints, indent=4, separators=(',', ':')))
