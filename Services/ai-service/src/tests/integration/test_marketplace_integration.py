import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.domain.entities.marketplace import Marketplace
from src.domain.entities.product import Product
from src.domain.entities.order import Order
from src.infrastructure.repositories.marketplace_repository import MarketplaceRepository
from src.infrastructure.external.marketplace_api_client import MarketplaceApiClient
from src.application.services.marketplace_service import MarketplaceService
from src.domain.exceptions import MarketplaceError, ValidationError
import asyncio

@pytest.fixture
def marketplace_api_client():
    return Mock(spec=MarketplaceApiClient)

@pytest.fixture
def marketplace_repository():
    return Mock(spec=MarketplaceRepository)

@pytest.fixture
def marketplace_service(marketplace_api_client, marketplace_repository):
    return MarketplaceService(
        api_client=marketplace_api_client,
        repository=marketplace_repository
    )

class TestMarketplaceIntegration:
    @pytest.mark.integration
    async def test_marketplace_product_sync(self, marketplace_service):
        # Arrange
        test_products = [
            Product(
                id="123",
                name="Test Product",
                price=99.99,
                stock=10,
                created_at=datetime.now()
            )
        ]
        marketplace_service.api_client.get_products.return_value = test_products
        
        # Act
        result = await marketplace_service.sync_products()
        
        # Assert
        assert result.success is True
        marketplace_service.repository.save_products.assert_called_once_with(test_products)

    @pytest.mark.integration
    async def test_marketplace_order_processing(self, marketplace_service):
        # Arrange
        test_order = Order(
            id="order123",
            customer_id="cust456",
            products=[{"product_id": "123", "quantity": 2}],
            total_amount=199.98,
            status="pending",
            created_at=datetime.now()
        )
        marketplace_service.api_client.create_order.return_value = test_order
        
        # Act
        result = await marketplace_service.process_order(test_order)
        
        # Assert
        assert result.success is True
        assert result.order.status == "processed"
        marketplace_service.repository.update_order.assert_called_once()

    @pytest.mark.integration
    async def test_marketplace_inventory_update(self, marketplace_service):
        # Arrange
        product_updates = [
            {"product_id": "123", "stock": 15},
            {"product_id": "456", "stock": 8}
        ]
        marketplace_service.api_client.update_inventory.return_value = True
        
        # Act
        result = await marketplace_service.update_inventory(product_updates)
        
        # Assert
        assert result.success is True
        marketplace_service.repository.update_inventory.assert_called_once_with(product_updates)

    @pytest.mark.integration
    async def test_marketplace_error_handling(self, marketplace_service):
        # Arrange
        marketplace_service.api_client.get_products.side_effect = MarketplaceError("API Error")
        
        # Act & Assert
        with pytest.raises(MarketplaceError):
            await marketplace_service.sync_products()

    @pytest.mark.integration
    async def test_marketplace_validation(self, marketplace_service):
        # Arrange
        invalid_order = Order(
            id="order123",
            customer_id="",  # Invalid empty customer_id
            products=[],     # Invalid empty products
            total_amount=0,
            status="invalid_status",
            created_at=datetime.now()
        )
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await marketplace_service.process_order(invalid_order)

    @pytest.mark.integration
    async def test_marketplace_concurrent_operations(self, marketplace_service):
        # Arrange
        test_orders = [
            Order(
                id=f"order{i}",
                customer_id=f"cust{i}",
                products=[{"product_id": "123", "quantity": 1}],
                total_amount=99.99,
                status="pending",
                created_at=datetime.now()
            ) for i in range(5)
        ]
        
        # Act
        results = await asyncio.gather(
            *[marketplace_service.process_order(order) for order in test_orders]
        )
        
        # Assert
        assert all(result.success for result in results)
        assert marketplace_service.repository.update_order.call_count == len(test_orders)

    def test_marketplace_configuration(self):
        # Test marketplace configuration and environment settings
        with patch.dict('os.environ', {
            'MARKETPLACE_API_KEY': 'test_key',
            'MARKETPLACE_API_URL': 'http://test.api.com'
        }):
            marketplace = Marketplace.from_environment()
            assert marketplace.api_key == 'test_key'
            assert marketplace.api_url == 'http://test.api.com'