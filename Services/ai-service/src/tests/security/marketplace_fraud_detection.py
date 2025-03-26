import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetectionService:
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    def detect_fraud(self, transaction: Dict[str, Any]) -> bool:
        for rule in self.rules:
            if not self._apply_rule(rule, transaction):
                return False
        return True

    def _apply_rule(self, rule: Dict[str, Any], transaction: Dict[str, Any]) -> bool:
        try:
            field = rule['field']
            operation = rule['operation']
            value = rule['value']
            transaction_value = transaction.get(field)

            if operation == 'equals':
                return transaction_value == value
            elif operation == 'greater_than':
                return transaction_value > value
            elif operation == 'less_than':
                return transaction_value < value
            else:
                logger.warning(f"Unknown operation: {operation}")
                return False
        except KeyError as e:
            logger.error(f"Missing key in rule or transaction: {e}")
            return False

def load_rules() -> List[Dict[str, Any]]:
    # Placeholder for loading rules from a database or configuration file
    return [
        {'field': 'amount', 'operation': 'greater_than', 'value': 1000},
        {'field': 'country', 'operation': 'equals', 'value': 'US'},
        # Add more rules as needed
    ]

def main():
    rules = load_rules()
    fraud_detection_service = FraudDetectionService(rules)

    # Example transaction
    transaction = {
        'amount': 1500,
        'country': 'US',
        'currency': 'USD',
        'timestamp': '2023-10-01T12:34:56Z'
    }

    is_fraud = fraud_detection_service.detect_fraud(transaction)
    if is_fraud:
        logger.info("Transaction is fraudulent")
    else:
        logger.info("Transaction is legitimate")

if __name__ == "__main__":
    main()