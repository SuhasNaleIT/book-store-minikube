import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },    // ramp up to 50 users
    { duration: '2m', target: 200 },   // ramp to 200 users
    { duration: '2m', target: 500 },   // spike to 500 users
    { duration: '2m', target: 200 },   // scale back down
    { duration: '1m', target: 0 },     // ramp to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed:   ['rate<0.1'],
  },
};

export default function () {
  const res = http.get('http://127.0.0.1/books');
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}