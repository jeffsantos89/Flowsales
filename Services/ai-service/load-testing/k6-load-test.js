import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  let res = http.get('https://api.flowsale.com/ai/predict');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
// Custom thresholds for metrics
export const thresholds = {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.01'],    // Less than 1% can fail
};

// Enhanced test configuration
export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 500 },  // Load test
        { duration: '5m', target: 500 },  // Stress test
        { duration: '2m', target: 100 },  // Ramp down
        { duration: '2m', target: 0 },    // Cool down
    ],
    thresholds,
    noConnectionReuse: true,
    userAgent: 'K6 Load Test',
    maxRedirects: 4,
};

// Error handling and retry logic
const MAX_RETRIES = 3;
const BASE_URL = 'https://api.flowsale.com';

export function handleError(error) {
    console.error(`Request failed: ${error}`);
}

export function makeRequest(retries = 0) {
    const params = {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
    };

    try {
        const res = http.get(`${BASE_URL}/ai/predict`, params);
        check(res, {
            'status is 200': (r) => r.status === 200,
            'response time OK': (r) => r.timings.duration < 2000,
        });
        return res;
    } catch (error) {
        if (retries < MAX_RETRIES) {
            console.log(`Retrying request (${retries + 1}/${MAX_RETRIES})`);
            sleep(1);
            return makeRequest(retries + 1);
        }
        handleError(error);
    }
}