# main.py
import logging
from src.config import Config
from src.clients.etherscan import EtherscanClient
from src.clients.alchemy import AlchemyClient
from src.utils.file_manager import FileManager
from src.extractors.blockchain import BlockchainExtractor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load configuration
        config = Config()
        daos = config.load_dao_config('config.json')

        # Initialize components
        etherscan = EtherscanClient(config.etherscan_api_key)
        alchemy = AlchemyClient(config.alchemy_api_key)
        file_manager = FileManager(config.output_dir)
        
        # Initialize extractor
        extractor = BlockchainExtractor(etherscan, alchemy, file_manager)

        # Process DAOs
        for dao in daos:
            try:
                extractor.process_dao(dao)
            except Exception as e:
                logger.error(f"Error processing DAO {dao.name}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()