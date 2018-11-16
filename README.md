[![banner](https://raw.githubusercontent.com/oceanprotocol/art/master/github/repo-banner%402x.png)](https://oceanprotocol.com)

# squid-py

> 💧 Python wrapper, allowing to integrate the basic Ocean/web3.py capabilities
> [oceanprotocol.com](https://oceanprotocol.com)

[![Travis (.com)](https://img.shields.io/travis/com/oceanprotocol/squid-py.svg)](https://travis-ci.com/oceanprotocol/squid-py)
[![Codacy coverage](https://img.shields.io/codacy/coverage/7084fbf528934327904a49d458bc46d1.svg)](https://app.codacy.com/project/ocean-protocol/squid-py/dashboard)
[![PyPI](https://img.shields.io/pypi/v/squid-py.svg)](https://pypi.org/project/squid-py/)
[![GitHub contributors](https://img.shields.io/github/contributors/oceanprotocol/squid-py.svg)](https://github.com/oceanprotocol/squid-py/graphs/contributors)

---

## Table of Contents

  - [Features](#features)
  - [Quick-start](#quick-start)
  - [Configuration](#configuration)
  - [Development](#development)
  - [License](#license)

---

## Features

Squid-py include the methods to make easy the connection with contracts deployed in different networks.
This repository include also the methods to encrypt and decrypt information.

## Prerequisites

Python 3.6

## Quick-start

Install Squid:

```
pip install squid-py
```

The entry point into the Squid functionality is the Ocean class:

```python
from squid_py.ocean import Ocean
ocean = Ocean('config.ini')

assert ocean.get_accounts()
```

## Configuration

`keeper.url` points to an Ethereum RPC client. Note that Squid learns the name of the network to work with from this client.

`keeper.path` points to the folder with keeper contracts definitions. When you install the package, the artifacts are
automatically picked up from the `keeper-contracts` Python dependency.

`storage.path` points to the local database file used for storing temporary information (for instance, pending service agreements).

In addition to the configuration file, you may use the following environment variables (override the corresponding configuration file values):

- KEEPER_PATH
- KEEPER_URL
- GAS_LIMIT
- AQUARIUS_URL

## Development

1. Set up a virtual environment

1. Install requirements

    ```
    pip install -r requirements_dev.txt
    ```

1. Run Docker images. Alternatively, set up and run some or all of the corresponding services locally.

    ```
    docker-compose -f ./docker/docker-compose.yml up
    ```

    It runs an Aquarius node and an Ethereum RPC client. For details, read `docker-compose.yml`.

1. Create local configuration file

    ```
    cp config.ini config_local.ini
    ```

   `config_local.ini` is used by unit tests.

1. Copy keeper artifacts
    
    A bash script is available to copy keeper artifacts into this file directly from a running docker image. This script needs to run in the root of the project.
    The script waits until the keeper contracts are deployed, and then copies the artifacts.

    ```
    ./scripts/wait_for_migration_and_extract_keeper_artifacts.sh
    ```

    The artifacts contain the addresses of all the deployed contracts and their ABI definitions required to interact with them.

1. Run the unit tests

    ```
    python3 setup.py test
    ```

#### Code style

The information about code style in python is documented in this two links [python-developer-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-developer-guide.md)
and [python-style-guide](https://github.com/oceanprotocol/dev-ocean/blob/master/doc/development/python-style-guide.md).
    
#### Testing

Automatic tests are setup via Travis, executing `tox`.
Our test use pytest framework.

#### New Version / New Release

See [RELEASE_PROCESS.md](RELEASE_PROCESS.md)

## License

```
Copyright 2018 Ocean Protocol Foundation Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
