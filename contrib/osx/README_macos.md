# Running Electrum-GRS from source on macOS (development version)

## Prerequisites

- [brew](https://brew.sh/)
- python3
- git

## Main steps

### 1. Check out the code from GitHub:
```
$ git clone https://github.com/Groestlcoin/electrum-grs.git
$ cd electrum-grs
$ git submodule update --init
```

### 2. Prepare for compiling libsecp256k1

To be able to build the `electrum-ecc` package from source
(which is pulled in when installing Electrum in the next step),
you need:
```
$ brew install autoconf automake libtool coreutils
```

### 3. Install Electrum-GRS

Run install (this should install the dependencies):
```
$ python3 -m pip install --user -e ".[gui,crypto]"
```

### 4. Run electrum-grs:
```
$ ./run_electrum_grs
```
