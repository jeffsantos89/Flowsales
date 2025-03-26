from security.waf_rules import check_request

def analyze_request_traffic(request):
    return check_request(request)
    def analyze_request_batch(requests, batch_size=100):
        """
        Analyzes multiple requests in batches for better performance.
        
        Args:
            requests: List of requests to analyze
            batch_size: Number of requests to process in each batch
        
        Returns:
            List of analysis results
        """
        results = []
        for i in range(0, len(requests), batch_size):
            batch = requests[i:i + batch_size]
            results.extend([analyze_request_traffic(req) for req in batch])
        return results

    async def analyze_request_async(request):
        """
        Asynchronous version of request analysis for better scalability.
        
        Args:
            request: Request to analyze
        
        Returns:
            Analysis result
        """
        return await check_request(request)

    def get_security_metrics():
        """
        Returns security metrics and statistics.
        
        Returns:
            Dict containing security metrics
        """
        return {
            'total_requests_analyzed': 0,
            'threats_detected': 0,
            'average_response_time': 0
        }