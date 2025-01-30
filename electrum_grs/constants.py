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


GIT_REPO_URL = "https://github.com/Groestlcoin/electrum-grs"
GIT_REPO_ISSUES_URL = "https://github.com/Groestlcoin/electrum-grs/issues"
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
    WIF_PREFIX = 0x80
    ADDRTYPE_P2PKH = 36
    ADDRTYPE_P2SH = 5
    SEGWIT_HRP = "grs"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "00000ac5927c594d49cc0bdb81759d0da8297eb614683d3acb62f0703b639023"
    DEFAULT_PORTS = {'t': '50001', 's': '50002'}
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers.json'))
    FALLBACK_LN_NODES = create_fallback_node_list(read_json(os.path.join('chains', 'fallback_lnnodes_mainnet.json')))
    CHECKPOINTS = read_json(os.path.join('chains', 'checkpoints.json'))
    BLOCK_HEIGHT_FIRST_LIGHTNING_CHANNELS = 497000

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
    BIP44_COIN_TYPE = 17
    LN_REALM_BYTE = 0
    LN_DNS_SEEDS = [
        'lseed1.groestlcoin.org.',
        'lseed2.groestlcoin.org.',
    ]


class BitcoinTestnet(AbstractNet):

    NET_NAME = "testnet"
    TESTNET = True
    WIF_PREFIX = 0xef
    ADDRTYPE_P2PKH = 111
    ADDRTYPE_P2SH = 196
    SEGWIT_HRP = "tgrs"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "000000ffbb50fc9898cdd36ec163e6ba23230164c0052a28876255b7dcf2cd36"
    DEFAULT_PORTS = {'t': '51001', 's': '51002'}
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers_testnet.json'), {})
    FALLBACK_LN_NODES = create_fallback_node_list(read_json(os.path.join('chains', 'fallback_lnnodes_testnet3.json'), {}))
    CHECKPOINTS = read_json(os.path.join('chains', 'checkpoints_testnet.json'), [])

    XPRV_HEADERS = {
        'standard':    0x04358394,  # tprv
        'p2wpkh-p2sh': 0x044a4e28,  # uprv
        'p2wsh-p2sh':  0x024285b5,  # Uprv
        'p2wpkh':      0x045f18bc,  # vprv
        'p2wsh':       0x02575048,  # Vprv
    }
    XPRV_HEADERS_INV = inv_dict(XPRV_HEADERS)
    XPUB_HEADERS = {
        'standard':    0x043587cf,  # tpub
        'p2wpkh-p2sh': 0x044a5262,  # upub
        'p2wsh-p2sh':  0x024289ef,  # Upub
        'p2wpkh':      0x045f1cf6,  # vpub
        'p2wsh':       0x02575483,  # Vpub
    }
    XPUB_HEADERS_INV = inv_dict(XPUB_HEADERS)
    BIP44_COIN_TYPE = 1
    LN_REALM_BYTE = 1
    LN_DNS_SEEDS = [
        'testnet-lseed1.groestlcoin.org.',
    ]


class BitcoinTestnet4(BitcoinTestnet):

    NET_NAME = "testnet4"
    GENESIS = "000000519399f41322d7a8c24bfdc409aa13a80160b43a57668c2ad62802fa5c"
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers_testnet4.json'), {})
    FALLBACK_LN_NODES = create_fallback_node_list(read_json(os.path.join('chains', 'fallback_lnnodes_testnet4.json'), {}))
    CHECKPOINTS = read_json(os.path.join('chains', 'checkpoints_testnet4.json'), [])
    LN_DNS_SEEDS = []


class BitcoinRegtest(BitcoinTestnet):

    NET_NAME = "regtest"
    SEGWIT_HRP = "grsrt"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "000000ffbb50fc9898cdd36ec163e6ba23230164c0052a28876255b7dcf2cd366"
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers_regtest.json'), {})
    FALLBACK_LN_NODES = []
    CHECKPOINTS = []
    LN_DNS_SEEDS = []


class BitcoinSimnet(BitcoinTestnet):

    NET_NAME = "simnet"
    WIF_PREFIX = 0x64
    ADDRTYPE_P2PKH = 0x3f
    ADDRTYPE_P2SH = 0x7b
    SEGWIT_HRP = "sg"
    BOLT11_HRP = SEGWIT_HRP
    GENESIS = "000000ffbb50fc9898cdd36ec163e6ba23230164c0052a28876255b7dcf2cd36"
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers_regtest.json'), {})
    FALLBACK_LN_NODES = []
    CHECKPOINTS = []
    LN_DNS_SEEDS = []


class BitcoinSignet(BitcoinTestnet):

    NET_NAME = "signet"
    BOLT11_HRP = "tgrss"
    GENESIS = "0000007fcaa2a27993c6cde9e7818c254357af517b876ceba2f23592bb14ab31"
    DEFAULT_SERVERS = read_json(os.path.join('chains', 'servers_signet.json'), {})
    FALLBACK_LN_NODES = create_fallback_node_list(read_json(os.path.join('chains', 'fallback_lnnodes_signet.json'), {}))
    CHECKPOINTS = []
    LN_DNS_SEEDS = []


NETS_LIST = tuple(all_subclasses(AbstractNet))

# don't import net directly, import the module instead (so that net is singleton)
net = BitcoinMainnet  # type: Type[AbstractNet]
