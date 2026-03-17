import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 100 },   // ramp up to 100 users
    { duration: '3m', target: 500 },   // ramp to 500 users
    { duration: '1m', target: 1000 },  // spike to 1000 users
    { duration: '2m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
  },
};

export default function () {
  http.get('http://k8s-bookstor-bookstor-1f39207299-1608165437.eu-west-2.elb.amazonaws.com/api/books');
  sleep(1);
}
