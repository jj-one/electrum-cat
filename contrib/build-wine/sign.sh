#!/bin/bash

here=$(dirname "$0")
if [ -z "$WIN_SIGNING_PASSWORD" ]; then
    echo "password missing"
    exit 1
fi

test -n "$here" -a -d "$here" || exit
cd $here

CERT_FILE=${CERT_FILE:-~/codesigning/cert.pem}
KEY_FILE=${KEY_FILE:-~/codesigning/key.pem}
if [[ ! -f "$CERT_FILE" ]]; then
    ls "$CERT_FILE"
    echo "Make sure that $CERT_FILE and $KEY_FILE exist"
fi

if ! which osslsigncode > /dev/null 2>&1; then
    echo "Please install osslsigncode"
fi

rm -rf signed
mkdir -p signed >/dev/null 2>&1

cd dist
echo "Found $(ls *.exe | wc -w) files to sign."

for f in $(ls *.exe); do
    echo "Signing $f..."
    osslsigncode sign \
        -pass "$WIN_SIGNING_PASSWORD" \
        -h sha256 \
        -certs "$CERT_FILE" \
        -key "$KEY_FILE" \
        -n "Electrum-CAT" \
        -i "https://electrum-cat.org/" \
        -t "http://timestamp.digicert.com/" \
        -in "$f" \
        -out "../signed/$f"
    ls "../signed/$f" -lah
done
