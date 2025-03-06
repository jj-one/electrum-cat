#!/usr/bin/env bash
export HOME=~
set -eux pipefail
mkdir -p ~/.catcoin
cat > ~/.catcoin/catcoin.conf <<EOF
regtest=1
txindex=1
printtoconsole=1
rpcuser=doggman
rpcpassword=donkey
rpcallowip=127.0.0.1
zmqpubrawblock=tcp://127.0.0.1:21441
zmqpubrawtx=tcp://127.0.0.1:21441
fallbackfee=0.0002
[regtest]
rpcbind=0.0.0.0
rpcport=18554
EOF
rm -rf ~/.catcoin/regtest
screen -S catcoind -X quit || true
screen -S catcoind -m -d catcoind -regtest
sleep 6
catcoin-cli createwallet test_wallet
addr=$(catcoin-cli getnewaddress)
catcoin-cli generatetoaddress 150 $addr > /dev/null
