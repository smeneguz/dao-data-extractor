# src/extractors/blockchain.py
import logging
from typing import List, Dict, Any, Optional
from ..models.dao import DAO, Contract
from ..clients.etherscan import EtherscanClient
from ..clients.alchemy import AlchemyClient
from ..utils.file_manager import FileManager

logger = logging.getLogger(__name__)

class BlockchainExtractor:
    def __init__(self, etherscan: EtherscanClient, alchemy: AlchemyClient, file_manager: FileManager):
        self.etherscan = etherscan
        self.alchemy = alchemy
        self.file_manager = file_manager

    def process_dao(self, dao: DAO) -> None:
        """
        Process all contracts for a DAO, ensuring proper folder structure and data handling
        """
        logger.info(f"Processing DAO: {dao.name}")
        
        for contract in dao.contracts:
            try:
                # Process each contract individually
                self._process_contract(dao.name, contract)
            except Exception as e:
                logger.error(f"Error processing contract {contract.name}: {str(e)}")
                continue

    def _process_contract(self, dao_name: str, contract: Contract) -> None:
        """
        Process a single contract, handling ABI and events
        """
        logger.info(f"Processing contract: {contract.name} ({contract.address})")

        # Step 1: Create necessary directories
        self.file_manager._ensure_contract_dir(dao_name, contract.name)

        # Step 2: Get and save ABI
        abi = self._get_and_save_abi(dao_name, contract)
        if not abi:
            logger.error(f"Could not retrieve ABI for contract {contract.name}. Skipping event processing.")
            return

        # Step 3: Process Events
        self._process_events(dao_name, contract)

    def _get_and_save_abi(self, dao_name: str, contract: Contract) -> Optional[str]:
        """
        Retrieve and save contract ABI
        Returns the ABI if successful, None otherwise
        """
        try:
            logger.info(f"Retrieving ABI for contract: {contract.name}")
            abi = self.etherscan.get_contract_abi(contract.address)
            
            if not abi:
                logger.warning(f"No ABI found for contract {contract.name}")
                return None

            # Save ABI as both JSON and CSV
            self.file_manager.save_contract_data(
                dao_name=dao_name,
                contract_name=contract.name,
                data_type='abi',
                data=[{'abi': abi}],
                append=False  # ABI should always be overwritten as it's a single entity
            )
            
            logger.info(f"Successfully saved ABI for contract {contract.name}")
            return abi

        except Exception as e:
            logger.error(f"Error retrieving ABI for contract {contract.name}: {str(e)}")
            return None

    def _process_events(self, dao_name: str, contract: Contract) -> None:
        """
        Process and save contract events
        """
        def process_batch(logs: List[Dict[str, Any]]) -> None:
            """Handle each batch of logs as they come in"""
            if logs:
                self.file_manager.save_contract_data(
                    dao_name=dao_name,
                    contract_name=contract.name,
                    data_type='events',
                    data=logs,
                    append=True
                )

        try:
            # Get logs with batch processing
            self.alchemy.get_logs(
                contract_address=contract.address,
                from_block=contract.deployed_at or 0,
                on_batch_complete=process_batch
            )
        except Exception as e:
            logger.error(f"Error processing events for contract {contract.name}: {str(e)}")