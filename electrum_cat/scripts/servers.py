#!/usr/bin/env python3
import json
import asyncio

from electrum_cat.simple_config import SimpleConfig
from electrum_cat.network import filter_version, Network
from electrum_cat.util import create_and_start_event_loop, log_exceptions
from electrum_cat import constants

# testnet?
#constants.BitcoinTestnet.set_as_network()
config = SimpleConfig({'testnet': False})

loop, stopping_fut, loop_thread = create_and_start_event_loop()
network = Network(config)
network.start()

@log_exceptions
async def f():
    try:
        peers = await network.get_peers()
        peers = filter_version(peers)
        print(json.dumps(peers, sort_keys=True, indent=4))
    finally:
        stopping_fut.set_result(1)

asyncio.run_coroutine_threadsafe(f(), loop)
