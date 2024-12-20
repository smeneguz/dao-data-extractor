
DAO Data Extractor

A tool for extracting and analyzing blockchain data from DAOs. This tool retrieves and processes smart contract events and ABIs, creating structured datasets for analysis.

## Features

- Retrieves and decodes smart contract ABIs from Etherscan
- Extracts blockchain events using Alchemy
- Saves data in both JSON and CSV formats
- Handles rate limiting and retry mechanisms
- Supports incremental data collection
- Maintains organized data structure by DAO and contract

## Prerequisites

- Python 3.8+
- Etherscan API key
- Alchemy API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/smeneguz/dao-data-extractor.git
cd dao-data-extractor

Create and activate a virtual environment:

bashCopypython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install requirements:

bashCopypip install -r requirements.txt

Create a .env file with your API keys:

envCopyETHERSCAN_API_KEY=your_etherscan_key_here
ALCHEMY_API_KEY=your_alchemy_key_here
OUTPUT_DIR=data
CACHE_DIR=.cache
NETWORK=mainnet
Usage

Configure your DAO in config.json:

jsonCopy{
    "name": "YourDAO",
    "description": "Description of the DAO",
    "contracts": [
        {
            "address": "0x...",
            "type": "governor",
            "name": "GovernorContract",
            "deployedAt": 12345678
        }
    ],
    "chainId": 1
}

Run the extractor:

bashCopypython main.py
The tool will create a structured output in your specified data directory:
Copydata/
└── YourDAO/
    └── GovernorContract/
        ├── abi.json
        ├── abi.csv
        ├── events.json
        └── events.csv
Project Structure
Copydao-data-extractor/
├── src/
│   ├── clients/        # API clients for Etherscan and Alchemy
│   ├── extractors/     # Data extraction logic
│   ├── models/         # Data models
│   └── utils/          # Utility functions
├── tests/             # Test files
├── .env              # Environment variables
├── config.json       # DAO configuration
└── main.py          # Entry point
Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.