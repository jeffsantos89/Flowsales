import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

export let errorRate = new Rate('errors');
export let responseTime = new Trend('response_time');

export let options = {
    stages: [
        { duration: '1m', target: 100 }, // ramp up to 100 users
        { duration: '2m', target: 100 }, // stay at 100 users
        { duration: '1m', target: 0 },   // ramp down to 0 users
    ],
    thresholds: {
        errors: ['rate<0.01'], // <1% errors
        response_time: ['p(95)<500'], // 95% of response times must be below 500ms
    },
};

export default function () {
    let res = http.get('https://your-api-endpoint.com/endpoint');
    
    let result = check(res, {
        'status is 200': (r) => r.status === 200,
        'response time is < 500ms': (r) => r.timings.duration < 500,
    });

    errorRate.add(!result);
    responseTime.add(res.timings.duration);

    sleep(1);
}