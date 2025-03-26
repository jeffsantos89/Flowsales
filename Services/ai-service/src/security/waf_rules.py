import re
from typing import Dict, Any
import logging

WAF_RULES = [
    {"rule": "block_sql_injection", "pattern": r"(\b(SELECT|INSERT|DELETE|UPDATE|DROP|ALTER)\b)", "action": "block"},
    {"rule": "block_xss", "pattern": r"(<script>|</script>)", "action": "block"},
]

def check_request(request):
    for rule in WAF_RULES:
        if rule["pattern"] in request:
            return {"status": "blocked", "rule": rule["rule"]}
    return {"status": "allowed"}
    def check_request_enhanced(request_data):
        """
        Enhanced WAF check that handles multiple request components and provides detailed logging
        """

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        def check_component(content: str) -> Dict[str, Any]:
            for rule in WAF_RULES:
                pattern = re.compile(rule["pattern"], re.IGNORECASE)
                if pattern.search(str(content)):
                    logger.warning(f"WAF rule {rule['rule']} triggered by content: {content[:50]}...")
                    return {"status": "blocked", "rule": rule["rule"], "matched_pattern": rule["pattern"]}
            return {"status": "allowed"}

        try:
            # Check URL
            url_check = check_component(request_data.get("url", ""))
            if url_check["status"] == "blocked":
                return {**url_check, "location": "url"}

            # Check headers
            headers = request_data.get("headers", {})
            for header, value in headers.items():
                header_check = check_component(value)
                if header_check["status"] == "blocked":
                    return {**header_check, "location": f"header_{header}"}

            # Check body
            body_check = check_component(request_data.get("body", ""))
            if body_check["status"] == "blocked":
                return {**body_check, "location": "body"}

            logger.info("Request passed all WAF checks")
            return {"status": "allowed", "message": "All checks passed"}

        except Exception as e:
            logger.error(f"WAF check error: {str(e)}")
            return {"status": "error", "message": str(e)}