# src/clients/etherscan.py
from typing import Optional, Dict, Any
import requests
import time
from functools import wraps
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

def rate_limit(min_interval: float = 0.2):
    """Rate limiting decorator for Etherscan API calls"""
    last_call = 0
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call
            now = time.time()
            time_passed = now - last_call
            if time_passed < min_interval:
                time.sleep(min_interval - time_passed)
            last_call = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

class EtherscanError(Exception):
    """Custom exception for Etherscan API errors"""
    pass

class EtherscanClient:
    def __init__(self, api_key: str, network: str = 'mainnet'):
        if not api_key:
            raise ValueError("Etherscan API key is required")
            
        self.api_key = api_key
        self.base_url = self._get_base_url(network)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'dao-data-extractor/1.0'
        })

    def _get_base_url(self, network: str) -> str:
        urls = {
            'mainnet': 'https://api.etherscan.io/api',
            'goerli': 'https://api-goerli.etherscan.io/api',
            'sepolia': 'https://api-sepolia.etherscan.io/api'
        }
        if network not in urls:
            raise ValueError(f"Unsupported network: {network}")
        return urls[network]

    @rate_limit(min_interval=0.2)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: None
    )
    def get_contract_abi(self, address: str) -> Optional[str]:
        """
        Fetch contract ABI from Etherscan
        Returns None if contract is not verified or error occurs
        """
        logger.debug(f"Fetching ABI for contract: {address}")
        
        try:
            response = self.session.get(
                self.base_url,
                params={
                    'module': 'contract',
                    'action': 'getabi',
                    'address': address,
                    'apikey': self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == '1' and data['message'] == 'OK':
                return data['result']
                
            if 'Max rate limit reached' in data.get('result', ''):
                raise EtherscanError("Rate limit reached")
                
            logger.warning(f"Could not get ABI for {address}: {data.get('result')}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching ABI for {address}: {str(e)}")
            raise EtherscanError(f"Network error: {str(e)}")