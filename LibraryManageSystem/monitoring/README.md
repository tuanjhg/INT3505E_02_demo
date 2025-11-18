# 📊 Monitoring với Prometheus và Grafana

## Tổng quan

Hệ thống monitoring sử dụng stack Prometheus + Grafana để theo dõi và cảnh báo về hiệu suất và sức khỏe của ứng dụng.

## Các thành phần

### 1. Prometheus (port 9090)
- **Chức năng:** Thu thập, lưu trữ và truy vấn metrics
- **URL:** http://localhost:9090
- **Config:** `monitoring/prometheus.yml`
- **Alert Rules:** `monitoring/alert_rules.yml`

### 2. Grafana (port 3000)
- **Chức năng:** Visualization và dashboard
- **URL:** http://localhost:3000
- **Login mặc định:** `admin` / `admin123`
- **Dashboard:** "Library Management API - Overview"

### 3. Exporters
- **Node Exporter (9100):** System metrics (CPU, memory, disk, network)
- **Postgres Exporter (9187):** Database metrics
- **Redis Exporter (9121):** Cache metrics
- **Nginx Exporter (9113):** Web server metrics

## Metrics Available

### Application Metrics (từ Flask app)

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Tổng số requests theo method, endpoint, status code |
| `http_request_duration_seconds` | Histogram | Phân bố thời gian response |
| `http_requests_in_progress` | Gauge | Số requests đang xử lý |
| `http_errors_total` | Counter | Tổng số lỗi |
| `system_cpu_usage_percent` | Gauge | CPU usage |
| `system_memory_usage_percent` | Gauge | Memory usage |
| `system_disk_usage_percent` | Gauge | Disk usage |
| `app_uptime_seconds` | Gauge | Thời gian app chạy |
| `books_total` | Gauge | Tổng số sách |
| `books_borrowed` | Gauge | Số sách đang mượn |
| `users_total` | Gauge | Tổng số users |

### System Metrics (từ Node Exporter)
- CPU usage per core
- Memory available/used
- Disk I/O
- Network traffic
- Load average

### Database Metrics (từ Postgres Exporter)
- Active connections
- Transaction rate
- Query duration
- Cache hit rate
- Database size

### Cache Metrics (từ Redis Exporter)
- Hit/miss rate
- Memory usage
- Connected clients
- Commands per second

## PromQL Query Examples

### Request Rate
```promql
# Requests per second (tổng)
rate(http_requests_total[5m])

# Requests per second theo endpoint
sum(rate(http_requests_total[1m])) by (endpoint)

# Requests per second theo method
sum(rate(http_requests_total[1m])) by (method)
```

### Error Rate
```promql
# Error rate percentage
sum(rate(http_errors_total[5m])) / sum(rate(http_requests_total[5m])) * 100

# Error rate theo endpoint
sum(rate(http_errors_total[5m])) by (endpoint)
```

### Response Time
```promql
# p50 (median)
histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))

# p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# p99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### System Resources
```promql
# CPU usage
system_cpu_usage_percent

# Memory usage
system_memory_usage_percent

# Disk usage
system_disk_usage_percent
```

### Business Metrics
```promql
# Book availability rate
(books_total - books_borrowed) / books_total * 100

# Books borrowed percentage
books_borrowed / books_total * 100
```

## Alert Rules

### Configured Alerts (13 total)

#### Application Alerts
1. **HighErrorRate** (Warning)
   - Condition: Error rate >5% for 5 minutes
   - Action: Investigate logs, check for bugs

2. **CriticalErrorRate** (Critical)
   - Condition: Error rate >10% for 2 minutes
   - Action: Page on-call engineer, check service health

3. **SlowResponseTime** (Warning)
   - Condition: p95 response time >1s for 10 minutes
   - Action: Check database queries, optimize code

4. **VerySlowResponseTime** (Critical)
   - Condition: p95 response time >3s for 5 minutes
   - Action: Scale resources, investigate bottlenecks

#### Resource Alerts
5. **HighMemoryUsage** (Warning)
   - Condition: Memory usage >80% for 10 minutes
   - Action: Monitor for memory leaks

6. **CriticalMemoryUsage** (Critical)
   - Condition: Memory usage >90% for 5 minutes
   - Action: Add memory or restart service

7. **HighCPUUsage** (Warning)
   - Condition: CPU usage >80% for 15 minutes
   - Action: Check for inefficient code

8. **DiskSpaceWarning** (Warning)
   - Condition: Disk usage >80% for 10 minutes
   - Action: Clean up old logs, backups

9. **CriticalDiskSpace** (Critical)
   - Condition: Disk usage >90% for 5 minutes
   - Action: Immediately free up space

#### Availability Alerts
10. **ApplicationDown** (Critical)
    - Condition: Service down for 1 minute
    - Action: Restart service, check logs

11. **HighDatabaseErrors** (Critical)
    - Condition: DB error rate >1/s for 5 minutes
    - Action: Check database connectivity

12. **NoRequests** (Warning)
    - Condition: Zero requests for 15 minutes
    - Action: Check if service is reachable

13. **RequestSpike** (Info)
    - Condition: Request rate 2x normal average for 5 minutes
    - Action: Monitor for potential issues

## Grafana Dashboard Panels

### Overview Dashboard (Pre-configured)

1. **Error Rate Gauge**
   - Thresholds: Green <3%, Yellow <5%, Red >5%
   - Real-time error rate percentage

2. **Requests Per Second Graph**
   - Line chart grouped by HTTP method
   - Shows mean and max in legend

3. **Response Time Percentiles**
   - Multi-line chart: p50, p95, p99
   - Helps identify latency issues

4. **System Resources**
   - Multi-line chart: CPU, Memory, Disk
   - Alerts at 80% (yellow) and 90% (red)

5. **HTTP Status Codes**
   - Bar chart showing distribution of 2xx, 4xx, 5xx
   - Sum over 5-minute intervals

6. **Top Endpoints Table**
   - Table showing top 10 endpoints by request count
   - Sortable by requests

7. **Business Metrics Stats**
   - Total Books (stat panel)
   - Books Borrowed (stat panel)
   - Total Users (stat panel)
   - Uptime (stat panel)

## Setup Instructions

### 1. Start Monitoring Stack
```bash
# Start all services including monitoring
docker-compose up -d

# Check Prometheus is scraping
curl http://localhost:9090/api/v1/targets

# Check Grafana is running
curl http://localhost:3000/api/health
```

### 2. Access Grafana
1. Mở browser: http://localhost:3000
2. Login: `admin` / `admin123`
3. Navigate to Dashboards → "Library Management API - Overview"

### 3. Configure Alert Notifications (Optional)

#### Email Alerts
```yaml
# Add to monitoring/alertmanager.yml
receivers:
  - name: 'email-alerts'
    email_configs:
      - to: 'team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'your-app-password'
```

#### Slack Alerts
```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Library API Alert'
        text: '{{ .CommonAnnotations.description }}'
```

#### PagerDuty
```yaml
receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
        severity: 'critical'
```

### 4. Create Custom Dashboards

1. Click "+" → "Dashboard" trong Grafana
2. Add Panel → Time series
3. Select Prometheus datasource
4. Enter PromQL query
5. Configure visualization options
6. Save dashboard

## Best Practices

### 1. Metrics Collection
- ✅ Use histograms for latency measurements
- ✅ Use counters for cumulative values (requests, errors)
- ✅ Use gauges for current state (memory, connections)
- ✅ Add relevant labels (endpoint, method, status)
- ❌ Don't create too many unique label combinations (high cardinality)

### 2. Alert Configuration
- ✅ Set appropriate thresholds based on baseline
- ✅ Use time windows to avoid flapping
- ✅ Define clear severity levels (info, warning, critical)
- ✅ Include actionable descriptions
- ❌ Don't create alerts for every metric

### 3. Dashboard Design
- ✅ Group related metrics together
- ✅ Use color coding for thresholds
- ✅ Include legends with calculations (mean, max, p95)
- ✅ Set appropriate time ranges (default: last 1 hour)
- ❌ Don't overcrowd dashboards with too many panels

### 4. Performance
- ✅ Use recording rules for expensive queries
- ✅ Set reasonable retention periods (default: 15 days)
- ✅ Use selective scraping intervals (10-30s)
- ❌ Don't scrape too frequently (increases load)

## Troubleshooting

### Prometheus không scrape được metrics
```bash
# Check targets trong Prometheus UI
http://localhost:9090/targets

# Kiểm tra app endpoint
curl http://app:8000/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

### Grafana không hiển thị data
```bash
# Verify datasource connection
curl http://localhost:3000/api/datasources

# Test PromQL query trong Prometheus UI
http://localhost:9090/graph

# Check Grafana logs
docker-compose logs grafana
```

### Alerts không fire
```bash
# Check alert rules đã load
http://localhost:9090/rules

# Xem alert state
http://localhost:9090/alerts

# Test expression trong Prometheus
rate(http_errors_total[5m])
```

### High memory usage
```bash
# Reduce retention period trong prometheus.yml
--storage.tsdb.retention.time=7d

# Reduce scrape intervals
scrape_interval: 30s

# Restart Prometheus
docker-compose restart prometheus
```

## Monitoring Checklist

### Daily
- [ ] Check Grafana dashboard for anomalies
- [ ] Review active alerts
- [ ] Monitor error rate trends

### Weekly
- [ ] Review slow endpoints (p95 > 500ms)
- [ ] Check resource usage trends
- [ ] Verify all exporters are healthy

### Monthly
- [ ] Review and tune alert thresholds
- [ ] Clean up old metrics
- [ ] Update dashboard with new metrics
- [ ] Test alert notification channels

## Resources

### Documentation
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

### Tools
- [Prometheus UI](http://localhost:9090) - Query, alerts, targets
- [Grafana UI](http://localhost:3000) - Dashboards, visualization
- [Alertmanager](http://localhost:9093) - Alert routing (if configured)

### Learning
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards Gallery](https://grafana.com/grafana/dashboards/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**Monitoring Stack Status:** ✅ Ready for Production

**Last Updated:** $(date)
