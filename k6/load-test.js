import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },   // ramp up to 100 users
    { duration: '2m', target: 500 },   // ramp to 500 users
    { duration: '2m', target: 1000 },  // spike to 1000 users
    { duration: '2m', target: 500 },   // scale back down
    { duration: '1m', target: 0 },     // ramp down to 0
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% requests under 2s
    http_req_failed:   ['rate<0.1'],   // less than 10% failures
  },
};

export default function () {
  const res = http.get(
    'http://k8s-bookstor-bookstor-1f39207299-1608165437.eu-west-2.elb.amazonaws.com/api/books'
  );
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
