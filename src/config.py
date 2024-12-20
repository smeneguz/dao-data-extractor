# src/config.py
from dotenv import load_dotenv, find_dotenv
import os
import json
from typing import List
import logging
from .models.dao import DAO, Contract

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Add debugging for .env loading
        env_path = find_dotenv()
        if env_path:
            logger.info(f"Found .env file at: {env_path}")
            load_dotenv(env_path)
        else:
            logger.error("No .env file found!")
            
        # Print current environment variables (masked)
        logger.info(f"ETHERSCAN_API_KEY exists: {'ETHERSCAN_API_KEY' in os.environ}")
        logger.info(f"ALCHEMY_API_KEY exists: {'ALCHEMY_API_KEY' in os.environ}")
        
        self._validate_env()
    
    def _validate_env(self):
        required_vars = ['ETHERSCAN_API_KEY', 'ALCHEMY_API_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    
    @property
    def etherscan_api_key(self) -> str:
        return os.getenv('ETHERSCAN_API_KEY')
    
    @property
    def alchemy_api_key(self) -> str:
        return os.getenv('ALCHEMY_API_KEY')
    
    @property
    def output_dir(self) -> str:
        return os.getenv('OUTPUT_DIR', 'data')

    @staticmethod
    def load_dao_config(file_path: str) -> List[DAO]:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]  # Convert single object to list
            return [
                DAO(
                    name=dao['name'],
                    description=dao['description'],
                    contracts=[
                        Contract(
                            address=c['address'],
                            type=c['type'],
                            name=c['name'],
                            deployed_at=c.get('deployedAt')
                        ) for c in dao['contracts']
                    ],
                    chain_id=dao['chainId']
                ) for dao in data
            ]