import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const getBooksDuration = new Trend('get_books_duration');
const createBookDuration = new Trend('create_book_duration');
const borrowBookDuration = new Trend('borrow_book_duration');
const returnBookDuration = new Trend('return_book_duration');
const successfulRequests = new Counter('successful_requests');
const failedRequests = new Counter('failed_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users over 1 minute
    { duration: '3m', target: 100 },  // Ramp up to 100 users over 3 minutes
    { duration: '5m', target: 200 },  // Ramp up to 200 users over 5 minutes
    { duration: '5m', target: 300 },  // Ramp up to 300 users over 5 minutes
    { duration: '3m', target: 500 },  // Ramp up to 500 users over 3 minutes
    { duration: '2m', target: 1000 }, // Spike to 1000 users over 2 minutes
    { duration: '3m', target: 500 },  // Scale back to 500 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'], // Error rate should be less than 10%
    errors: ['rate<0.1'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8081';

// User credentials for testing
const TEST_USERS = [
  { username: 'testuser', password: 'test123' },
  { username: 'user1', password: 'password1' },
  { username: 'user2', password: 'password2' },
  { username: 'admin', password: 'admin123' },
];

function getRandomUser() {
  return TEST_USERS[Math.floor(Math.random() * TEST_USERS.length)];
}

function login() {
  const user = getRandomUser();
  const url = `${BASE_URL}/api/auth/login`;
  const payload = JSON.stringify({
    username: user.username,
    password: user.password,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { name: 'UserLogin' },
  };

  const res = http.post(url, payload, params);
  
  const success = check(res, {
    'login status is 200': (r) => r.status === 200,
    'login has access token': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.data && body.data.access_token;
      } catch (e) {
        return false;
      }
    },
  });

  loginDuration.add(res.timings.duration);
  errorRate.add(!success);
  
  if (success) {
    successfulRequests.add(1);
    const body = JSON.parse(res.body);
    return body.data.access_token;
  } else {
    failedRequests.add(1);
    return null;
  }
}

function getBooks(token) {
  const url = `${BASE_URL}/api/books?page=1&per_page=10`;
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    tags: { name: 'GetBooks' },
  };

  const res = http.get(url, params);
  
  const success = check(res, {
    'get books status is 200': (r) => r.status === 200,
    'get books has data': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.data && body.data.books;
      } catch (e) {
        return false;
      }
    },
  });

  getBooksDuration.add(res.timings.duration);
  errorRate.add(!success);
  
  if (success) {
    successfulRequests.add(1);
  } else {
    failedRequests.add(1);
  }
  
  return success;
}

function createBook(token) {
  const randomId = Math.floor(Math.random() * 1000000);
  const url = `${BASE_URL}/api/books`;
  const payload = JSON.stringify({
    title: `Load Test Book ${randomId}`,
    author: `Test Author ${randomId}`,
    isbn: `ISBN-${randomId}`,
    published_date: '2024-01-01',
    copies: 5,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    tags: { name: 'CreateBook' },
  };

  const res = http.post(url, payload, params);
  
  const success = check(res, {
    'create book status is 201': (r) => r.status === 201,
    'create book has id': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.data && body.data.book && body.data.book.id;
      } catch (e) {
        return false;
      }
    },
  });

  createBookDuration.add(res.timings.duration);
  errorRate.add(!success);
  
  if (success) {
    successfulRequests.add(1);
    const body = JSON.parse(res.body);
    return body.data.book.id;
  } else {
    failedRequests.add(1);
    return null;
  }
}

function borrowBook(token, bookId) {
  const url = `${BASE_URL}/api/borrows`;
  const payload = JSON.stringify({
    book_id: bookId,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    tags: { name: 'BorrowBook' },
  };

  const res = http.post(url, payload, params);
  
  const success = check(res, {
    'borrow book status is 201 or 400': (r) => r.status === 201 || r.status === 400,
  });

  borrowBookDuration.add(res.timings.duration);
  errorRate.add(!success);
  
  if (success && res.status === 201) {
    successfulRequests.add(1);
    const body = JSON.parse(res.body);
    return body.data.borrow.id;
  } else if (res.status === 400) {
    successfulRequests.add(1); // Not an error, just book not available
    return null;
  } else {
    failedRequests.add(1);
    return null;
  }
}

function returnBook(token, borrowId) {
  if (!borrowId) return;
  
  const url = `${BASE_URL}/api/borrows/${borrowId}/return`;
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    tags: { name: 'ReturnBook' },
  };

  const res = http.post(url, '', params);
  
  const success = check(res, {
    'return book status is 200 or 400': (r) => r.status === 200 || r.status === 400,
  });

  returnBookDuration.add(res.timings.duration);
  errorRate.add(!success);
  
  if (success) {
    successfulRequests.add(1);
  } else {
    failedRequests.add(1);
  }
}

export default function () {
  // Login
  const token = login();
  if (!token) {
    sleep(1);
    return;
  }
  
  sleep(0.5);

  // Get books list
  getBooks(token);
  sleep(0.5);

  // Random actions with different probabilities
  const action = Math.random();
  
  if (action < 0.5) {
    // 50% chance: Just browse books
    getBooks(token);
  } else if (action < 0.7) {
    // 20% chance: Create and borrow a book
    const bookId = createBook(token);
    if (bookId) {
      sleep(0.3);
      const borrowId = borrowBook(token, bookId);
      sleep(0.5);
      returnBook(token, borrowId);
    }
  } else {
    // 30% chance: Try to borrow existing book
    const bookId = Math.floor(Math.random() * 10) + 1; // Assume books 1-10 exist
    const borrowId = borrowBook(token, bookId);
    sleep(0.5);
    returnBook(token, borrowId);
  }

  sleep(Math.random() * 2 + 1); // Random sleep between 1-3 seconds
}

export function handleSummary(data) {
  // Generate JSON output for custom HTML report
  return {
    'summary.json': JSON.stringify(data),
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function textSummary(data, options) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;
  
  let summary = '\n' + indent + '█ Test Summary\n\n';
  
  // Overall statistics
  summary += indent + `  Scenarios: ${data.root_group.checks.length} total\n`;
  summary += indent + `  Duration: ${formatDuration(data.state.testRunDurationMs)}\n`;
  summary += indent + `  Requests: ${data.metrics.http_reqs ? data.metrics.http_reqs.values.count : 0}\n`;
  
  if (data.metrics.http_req_failed) {
    const failRate = data.metrics.http_req_failed.values.rate * 100;
    summary += indent + `  Failed Requests: ${failRate.toFixed(2)}%\n`;
  }
  
  if (data.metrics.errors) {
    const errorRate = data.metrics.errors.values.rate * 100;
    summary += indent + `  Error Rate: ${errorRate.toFixed(2)}%\n`;
  }
  
  summary += '\n' + indent + '█ Response Times\n\n';
  
  if (data.metrics.http_req_duration) {
    const duration = data.metrics.http_req_duration.values;
    summary += indent + `  Average: ${duration.avg.toFixed(2)}ms\n`;
    summary += indent + `  Median: ${duration.med.toFixed(2)}ms\n`;
    summary += indent + `  P95: ${duration['p(95)'].toFixed(2)}ms\n`;
    summary += indent + `  P99: ${duration['p(99)'].toFixed(2)}ms\n`;
    summary += indent + `  Max: ${duration.max.toFixed(2)}ms\n`;
  }
  
  return summary;
}

function formatDuration(ms) {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
}
