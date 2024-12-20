# src/clients/alchemy.py
from typing import List, Dict, Any, Optional, Callable
from web3 import Web3
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AlchemyError(Exception):
    """Custom exception for Alchemy API errors"""
    pass

class AlchemyClient:
    def __init__(self, api_key: str, network: str = 'mainnet'):
        if not api_key:
            raise ValueError("Alchemy API key is required")
            
        self.w3 = Web3(Web3.HTTPProvider(
            f"https://eth-{network}.g.alchemy.com/v2/{api_key}"
        ))
        self.last_request_time = 0
        self.min_request_interval = 0.1
        self.batch_size = 1000

    def _throttle(self):
        """Implement rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()

    def _to_checksum_address(self, address: str) -> str:
        """Convert address to checksum format"""
        try:
            return Web3.to_checksum_address(address)
        except ValueError as e:
            logger.error(f"Invalid Ethereum address: {address}")
            raise AlchemyError(f"Invalid Ethereum address: {address}")

    def _format_log(self, log: Dict) -> Dict[str, Any]:
        """Format a single log entry"""
        return {
            'blockNumber': log['blockNumber'],
            'transactionHash': log['transactionHash'].hex(),
            'topics': [t.hex() for t in log['topics']],
            'data': log['data'],
            'logIndex': log['logIndex'],
            'transactionIndex': log['transactionIndex']
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_logs(self, 
                 contract_address: str, 
                 from_block: int,
                 to_block: Optional[int] = None,
                 batch_size: Optional[int] = None,
                 on_batch_complete: Optional[Callable[[List[Dict[str, Any]]], None]] = None) -> List[Dict[str, Any]]:
        """
        Fetch logs for contract with automatic pagination and streaming processing
        Args:
            contract_address: Contract address to get logs for
            from_block: Starting block number
            to_block: Ending block number (optional)
            batch_size: Number of blocks per batch (optional)
            on_batch_complete: Callback function to process each batch of logs
        """
        self._throttle()
        batch_size = batch_size or self.batch_size
        
        try:
            checksum_address = self._to_checksum_address(contract_address)
            
            if not to_block:
                to_block = self.w3.eth.block_number

            if from_block == 0:
                from_block = 12450964
                logger.info(f"Starting from block {from_block} instead of 0")
                
            logger.info(
                f"Fetching logs for {checksum_address} from block {from_block} to {to_block}"
            )
            
            all_logs = []
            current_block = from_block
            total_blocks = to_block - from_block
            last_progress_log = time.time()
            
            while current_block < to_block:
                end_block = min(current_block + batch_size, to_block)
                
                if time.time() - last_progress_log >= 30:
                    progress = (current_block - from_block) / total_blocks * 100
                    logger.info(f"Progress: {progress:.2f}% complete")
                    last_progress_log = time.time()
                
                try:
                    logs = self.w3.eth.get_logs({
                        'fromBlock': current_block,
                        'toBlock': end_block,
                        'address': checksum_address
                    })
                    
                    if logs:
                        formatted_logs = [self._format_log(log) for log in logs]
                        
                        # Process the batch immediately if callback is provided
                        if on_batch_complete and formatted_logs:
                            on_batch_complete(formatted_logs)
                        
                        all_logs.extend(formatted_logs)
                        logger.info(
                            f"Retrieved and processed {len(logs)} logs for blocks {current_block}-{end_block}"
                        )
                    
                except Exception as e:
                    logger.error(
                        f"Error fetching logs for blocks {current_block}-{end_block}: {str(e)}"
                    )
                    raise AlchemyError(f"Failed to fetch logs: {str(e)}")
                    
                current_block = end_block + 1
                
            logger.info(f"Completed fetching logs. Total logs found: {len(all_logs)}")
            return all_logs
            
        except Exception as e:
            logger.error(f"Error in get_logs: {str(e)}")
            raise AlchemyError(f"Failed to get logs: {str(e)}")