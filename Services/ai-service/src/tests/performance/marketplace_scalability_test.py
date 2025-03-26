import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

from marketplace import Marketplace  # Adjust the import path according to your project structure

class MarketplaceScalabilityTest(unittest.TestCase):

    def setUp(self):
        self.marketplace = Marketplace()
        self.num_users = 1000
        self.num_products = 500
        self.num_threads = 10

    def simulate_user_activity(self, user_id):
        for _ in range(100):
            product_id = user_id % self.num_products
            self.marketplace.add_to_cart(user_id, product_id)
            self.marketplace.checkout(user_id)

    def test_scalability(self):
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.simulate_user_activity, user_id) for user_id in range(self.num_users)]
            for future in as_completed(futures):
                future.result()  # Raise exceptions if any

        end_time = time.time()
        duration = end_time - start_time
        print(f"Scalability test completed in {duration:.2f} seconds")

        # Add assertions to verify the state of the marketplace
        self.assertTrue(self.marketplace.is_consistent())
        self.assertEqual(self.marketplace.total_users(), self.num_users)
        self.assertEqual(self.marketplace.total_products(), self.num_products)

if __name__ == "__main__":
    unittest.main()