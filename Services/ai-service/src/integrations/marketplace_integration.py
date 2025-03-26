import requests
import os

MARKETPLACE_APIS = {
    "amazon": os.getenv("AMAZON_API_URL"),
    "shopee": os.getenv("SHOPEE_API_URL"),
    "mercadolivre": os.getenv("MERCADOLIVRE_API_URL")
}

def sync_inventory(marketplace: str, product_data: dict):
    """ Sincroniza o inventário com os marketplaces """
    if marketplace not in MARKETPLACE_APIS:
        raise ValueError(f"Marketplace '{marketplace}' não suportado")
    
    url = f"{MARKETPLACE_APIS[marketplace]}/inventory/sync"
    response = requests.post(url, json=product_data)
    return response.json()
    class MarketplaceIntegration:
        def __init__(self, timeout=30, max_retries=3):
            self.session = requests.Session()
            self.timeout = timeout
            self.max_retries = max_retries

        def _make_request(self, method, url, **kwargs):
            for attempt in range(self.max_retries):
                try:
                    response = self.session.request(
                        method, 
                        url, 
                        timeout=self.timeout,
                        **kwargs
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException as e:
                    if attempt == self.max_retries - 1:
                        raise Exception(f"Failed after {self.max_retries} attempts: {str(e)}")
                    continue

        def sync_inventory(self, marketplace: str, product_data: dict):
            if not isinstance(product_data, dict):
                raise TypeError("product_data must be a dictionary")

            if marketplace not in MARKETPLACE_APIS:
                raise ValueError(f"Unsupported marketplace: {marketplace}")

            if not MARKETPLACE_APIS[marketplace]:
                raise ValueError(f"API URL not configured for {marketplace}")

            url = f"{MARKETPLACE_APIS[marketplace]}/inventory/sync"
            return self._make_request("POST", url, json=product_data)

        def sync_batch(self, marketplace: str, products: list):
            results = []
            for product in products:
                try:
                    result = self.sync_inventory(marketplace, product)
                    results.append({"success": True, "data": result})
                except Exception as e:
                    results.append({"success": False, "error": str(e)})
            return results