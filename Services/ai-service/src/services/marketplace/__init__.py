import logging
from .marketplace_service import MarketplaceService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MarketplaceService
marketplace_service = MarketplaceService()

def initialize_marketplace():
    """
    Initialize the marketplace service and perform any necessary setup.
    """
    try:
        logger.info("Initializing the marketplace service...")
        marketplace_service.setup()
        logger.info("Marketplace service initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize the marketplace service: {e}")
        raise

# Perform the initialization when the module is imported
initialize_marketplace()