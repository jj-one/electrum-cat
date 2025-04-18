# -*- coding: utf-8 -*-
#
# Electrum - lightweight Bitcoin client
# Copyright (C) 2018 The Electrum developers
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import json
from typing import Sequence, Tuple, Mapping, Type, List

from .lntransport import LNPeerAddr
from .util import inv_dict, all_subclasses
from . import bitcoin


def read_json(filename, default=None):
    path = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(path, 'r') as f:
            r = json.loads(f.read())
    except Exception:
        if default is None:
            # Sometimes it's better to hard-fail: the file might be missing
            # due to a packaging issue, which might otherwise go unnoticed.
            raise
        r = default
    return r


def create_fallback_node_list(fallback_nodes_dict: dict[str, dict]) -> List[LNPeerAddr]:
    """Take a json dict of fallback nodes like: k:node_id, v:{k:'host', k:'port'} and return LNPeerAddr list"""
    fallback_nodes = []
    for node_id, address in fallback_nodes_dict.items():
        fallback_nodes.append(
            LNPeerAddr(host=address['host'], port=int(address['port']), pubkey=bytes.fromhex(node_id)))
    return fallback_nodes


GIT_REPO_URL = "https://github.com/jj-one/electrum-cat"
GIT_REPO_ISSUES_URL = "https://github.com/jj-one/electrum-cat/issues"
BIP39_WALLET_FORMATS = read_json('bip39_wallet_formats.json')


class AbstractNet:

    NET_NAME: str
    TESTNET: bool
    WIF_PREFIX: int
    ADDRTYPE_P2PKH: int
    ADDRTYPE_P2SH: int
    SEGWIT_HRP: str
    BOLT11_HRP: str
    GENESIS: str
    BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS: int = 0
    BIP44_COIN_TYPE: int
    LN_REALM_BYTE: int
    DEFAULT_PORTS: Mapping[str, str]
    DEFAULT_SERVERS: Mapping[str, Mapping[str, str]]
    FALLBACK_LN_NODES: Sequence[LNPeerAddr]
    CHECKPOINTS: Sequence[Tuple[str, int]]
    LN_DNS_SEEDS: Sequence[str]
    XPRV_HEADERS: Mapping[str, int]
    XPRV_HEADERS_INV: Mapping[int, str]
    XPUB_HEADERS: Mapping[str, int]
    XPUB_HEADERS_INV: Mapping[int, str]
    TARGET_DISRUPTION_HEIGHT1: int
    TARGET_DISRUPTION_HEIGHT3: int
    TARGET_DISRUPTION_HEIGHT4: int
    TARGET_DISRUPTION_HEIGHT5: int
    TARGET_DISRUPTION_14_TO_36: Mapping[str, str]
    TARGET_DISRUPTION_14_TO_36_END: int
    POW_TARGET_TIMESPAN_V1: int
    POW_TARGET_TIMESPAN_V2: int
    POW_TARGET_SPACING: int
    LWMA_AVERAGING_WINDOW: int

    @classmethod
    def max_checkpoint(cls) -> int:
        return max(0, len(cls.CHECKPOINTS) * 2016 - 1)

    @classmethod
    def rev_genesis_bytes(cls) -> bytes:
        return bytes.fromhex(cls.GENESIS)[::-1]

    @classmethod
    def set_as_network(cls) -> None:
        global net
        net = cls


class BitcoinMainnet(AbstractNet):

    NET_NAME = "mainnet"
    TESTNET = False
    WIF_PREFIX = 0x95
    ADDRTYPE_P2PKH = 21
    ADDRTYPE_P2SH = 88
    SEGWIT_HRP = "cat"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "bc3b4ec43c4ebb2fef49e6240812549e61ffa623d9418608aa90eaad26c96296"
    DEFAULT_PORTS = {'t': '8105', 's': '8103'}
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers.json'))
    FALLBACK_LN_NODES = create_fallback_node_list(read_json(os.path.join('chains', 'fallback_lnnodes_mainnet.json')))
    CHECKPOINTS = read_json(os.path.join('chains', 'checkpoints.json'))
    BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS = 497000
    TARGET_DISRUPTION_HEIGHT1 = 20289
    TARGET_DISRUPTION_HEIGHT3 = 27260
    TARGET_DISRUPTION_HEIGHT4 = 46331
    TARGET_DISRUPTION_HEIGHT5 = 397000
    POW_TARGET_TIMESPAN_V1 = 14 * 24 * 60 * 60
    POW_TARGET_TIMESPAN_V2 = 6 * 60 * 60
    POW_TARGET_SPACING = 10 * 60
    LWMA_AVERAGING_WINDOW = 45
    TARGET_DISRUPTION_14_TO_36_END = 21346
    TARGET_DISRUPTION_14_TO_36 = {
        '20289': '1c0ffff0', '20303': '1c3fffc0', '20339': '1c0ffff0', '20375': '1c0440a5',
        '20411': '1c05b465', '20447': '1c041076', '20483': '1c0a6691', '20519': '1c0299a4',
        '20555': '1c0993ee', '20591': '1c059d71', '20627': '1c040f15', '20663': '1c0894be',
        '20699': '1c033e15', '20735': '1c0cf854', '20771': '1c044cc7', '20807': '1c058eb4',
        '20843': '1c0fc3ab', '20879': '1c03f0ea', '20915': '1c0dac5f', '20951': '1c03b5a3',
        '20987': '1c0ed68c', '21023': '1c04065b', '21059': '1c10196c', '21095': '1c04065b',
        '21131': '1c10196c', '21167': '1c04065b', '21203': '1c03f352', '21239': '1c02eb40',
        '21275': '1c03f513', '21311': '1c025bab', '21346': '1c02a41b'
    }
    XPRV_HEADERS = {
        'standard':    0x0488ade4,  # xprv
        'p2wpkh-p2sh': 0x049d7878,  # yprv
        'p2wsh-p2sh':  0x0295b005,  # Yprv
        'p2wpkh':      0x04b2430c,  # zprv
        'p2wsh':       0x02aa7a99,  # Zprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x0488b21e,  # xpub
        'p2wpkh-p2sh': 0x049d7cb2,  # ypub
        'p2wsh-p2sh':  0x0295b43f,  # Ypub
        'p2wpkh':      0x04b24746,  # zpub
        'p2wsh':       0x02aa7ed3,  # Zpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 760
    LN_REALM_BYTE = 0
    LN_DNS_SEEDS = []


NETS_LIST = tuple(all_subclasses(AbstractNet))

# don't import net directly, import the module instead (so that net is singleton)
net = BitcoinMainnet  # type: Type[AbstractNet]
