#!/usr/bin/env python3
"""
GitHub API Pattern Analyzer
Phân tích API GitHub để tìm các patterns: CRUD, Webhook, Event-driven, Query, HATEOAS

Patterns được phân tích:
1. CRUD (Create, Read, Update, Delete) - Các thao tác cơ bản
2. Webhook - Cơ chế thông báo real-time
3. Event-driven - Xử lý sự kiện
4. Query - Tham số truy vấn và filtering
5. HATEOAS - Hypermedia as the Engine of Application State
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class GitHubAPIAnalyzer:
    """Phân tích GitHub API để tìm các REST patterns"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Khởi tạo analyzer
        
        Args:
            token: GitHub Personal Access Token (optional, tăng rate limit)
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-API-Pattern-Analyzer"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        self.analysis_results = {
            "crud": [],
            "webhook": [],
            "event_driven": [],
            "query": [],
            "hateoas": []
        }
    
    def make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """Thực hiện API request và trả về response với metadata"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.content else {},
                "url": url,
                "method": method
            }
        except Exception as e:
            return {"error": str(e), "url": url, "method": method}
    
    # ==================== CRUD Pattern Analysis ====================
    
    def analyze_crud_pattern(self, owner: str, repo: str, demo_mode: bool = False) -> Dict:
        """
        Phân tích CRUD pattern qua Repository API
        
        CRUD trong GitHub API:
        - Create: POST /repos/{owner}/{repo}/issues
        - Read: GET /repos/{owner}/{repo}/issues
        - Update: PATCH /repos/{owner}/{repo}/issues/{issue_number}
        - Delete: DELETE /repos/{owner}/{repo}/issues/{issue_number}
        
        Args:
            owner: GitHub username
            repo: Repository name
            demo_mode: Nếu True, sẽ thực sự tạo/update/close issue trên GitHub
        """
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}1. CRUD PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        
        crud_examples = []
        created_issue_number = None
        
        # READ - Get repository info
        print(f"\n{Colors.CYAN}📖 READ Operation:{Colors.END}")
        repo_response = self.make_request(f"/repos/{owner}/{repo}")
        if "error" not in repo_response:
            print(f"   GET /repos/{owner}/{repo}")
            print(f"   Status: {Colors.GREEN}{repo_response['status_code']}{Colors.END}")
            crud_examples.append({
                "operation": "READ",
                "method": "GET",
                "endpoint": f"/repos/{owner}/{repo}",
                "description": "Lấy thông tin repository",
                "response_fields": list(repo_response['data'].keys())[:10]
            })
        
        # READ - List issues (Collection)
        print(f"\n{Colors.CYAN}📖 READ Collection:{Colors.END}")
        issues_response = self.make_request(f"/repos/{owner}/{repo}/issues", params={"per_page": 5})
        if "error" not in issues_response:
            print(f"   GET /repos/{owner}/{repo}/issues")
            print(f"   Status: {Colors.GREEN}{issues_response['status_code']}{Colors.END}")
            print(f"   Items returned: {len(issues_response['data'])}")
            crud_examples.append({
                "operation": "READ (Collection)",
                "method": "GET",
                "endpoint": f"/repos/{owner}/{repo}/issues",
                "description": "Liệt kê issues của repository",
                "pagination": "Link header" in str(issues_response['headers'])
            })
        
        # ========== DEMO MODE: Thực sự tạo issue trên GitHub ==========
        if demo_mode:
            print(f"\n{Colors.BOLD}{Colors.YELLOW}🚀 DEMO MODE: Thực hiện CRUD thật trên GitHub!{Colors.END}")
            
            # CREATE - Tạo issue thật
            print(f"\n{Colors.CYAN}✏️ CREATE Operation (REAL):{Colors.END}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            issue_data = {
                "title": f"[API Demo] CRUD Pattern Test - {timestamp}",
                "body": f"""## 🧪 Demo CRUD Pattern

Đây là issue được tạo tự động bởi **GitHub API Pattern Analyzer** để demo CRUD operations.

### Thông tin:
- **Thời gian tạo:** {timestamp}
- **Pattern:** CRUD (Create, Read, Update, Delete)
- **Method:** POST /repos/{owner}/{repo}/issues

### CRUD Operations sẽ thực hiện:
1. ✅ **CREATE** - Tạo issue này
2. ⏳ **READ** - Đọc lại issue vừa tạo
3. ⏳ **UPDATE** - Cập nhật title và thêm label
4. ⏳ **CLOSE** - Đóng issue (tương tự DELETE concept)

---
*Tự động tạo bởi GitHub API Pattern Analyzer*
""",
                "labels": ["api-demo", "automated"]
            }
            
            print(f"   POST /repos/{owner}/{repo}/issues")
            print(f"   Body: {json.dumps({'title': issue_data['title'][:50] + '...', 'body': '...(truncated)'}, indent=4)}")
            
            create_response = self.make_request(
                f"/repos/{owner}/{repo}/issues",
                method="POST",
                json=issue_data
            )
            
            if "error" not in create_response and create_response["status_code"] == 201:
                created_issue = create_response["data"]
                created_issue_number = created_issue["number"]
                print(f"   Status: {Colors.GREEN}{create_response['status_code']} Created{Colors.END}")
                print(f"   {Colors.GREEN}✅ Issue #{created_issue_number} đã được tạo!{Colors.END}")
                print(f"   URL: {created_issue['html_url']}")
                crud_examples.append({
                    "operation": "CREATE (REAL)",
                    "method": "POST",
                    "endpoint": f"/repos/{owner}/{repo}/issues",
                    "description": "Tạo issue thật trên GitHub",
                    "result": {
                        "issue_number": created_issue_number,
                        "url": created_issue['html_url']
                    }
                })
                
                # READ - Đọc lại issue vừa tạo
                print(f"\n{Colors.CYAN}📖 READ Single Issue (REAL):{Colors.END}")
                print(f"   GET /repos/{owner}/{repo}/issues/{created_issue_number}")
                read_response = self.make_request(f"/repos/{owner}/{repo}/issues/{created_issue_number}")
                if "error" not in read_response:
                    print(f"   Status: {Colors.GREEN}{read_response['status_code']}{Colors.END}")
                    print(f"   Title: {read_response['data']['title'][:50]}...")
                    print(f"   State: {read_response['data']['state']}")
                    crud_examples.append({
                        "operation": "READ (REAL)",
                        "method": "GET",
                        "endpoint": f"/repos/{owner}/{repo}/issues/{created_issue_number}",
                        "description": "Đọc issue vừa tạo"
                    })
                
                # UPDATE - Cập nhật issue
                print(f"\n{Colors.CYAN}🔄 UPDATE Operation (REAL):{Colors.END}")
                update_data = {
                    "title": f"[API Demo] ✅ CRUD Test Completed - {timestamp}",
                    "body": create_response["data"]["body"] + "\n\n---\n### ✅ UPDATE đã thực hiện!\n- Title đã được cập nhật\n- Issue sẽ được đóng sau đó"
                }
                print(f"   PATCH /repos/{owner}/{repo}/issues/{created_issue_number}")
                
                update_response = self.make_request(
                    f"/repos/{owner}/{repo}/issues/{created_issue_number}",
                    method="PATCH",
                    json=update_data
                )
                
                if "error" not in update_response and update_response["status_code"] == 200:
                    print(f"   Status: {Colors.GREEN}{update_response['status_code']} OK{Colors.END}")
                    print(f"   {Colors.GREEN}✅ Issue đã được cập nhật!{Colors.END}")
                    crud_examples.append({
                        "operation": "UPDATE (REAL)",
                        "method": "PATCH",
                        "endpoint": f"/repos/{owner}/{repo}/issues/{created_issue_number}",
                        "description": "Cập nhật title của issue"
                    })
                else:
                    print(f"   Status: {Colors.RED}{update_response.get('status_code', 'Error')}{Colors.END}")
                
                # CLOSE (DELETE equivalent) - Đóng issue
                print(f"\n{Colors.CYAN}🗑️ CLOSE/DELETE Operation (REAL):{Colors.END}")
                print(f"   PATCH /repos/{owner}/{repo}/issues/{created_issue_number}")
                print(f"   Body: {json.dumps({'state': 'closed'}, indent=4)}")
                
                close_response = self.make_request(
                    f"/repos/{owner}/{repo}/issues/{created_issue_number}",
                    method="PATCH",
                    json={"state": "closed", "state_reason": "completed"}
                )
                
                if "error" not in close_response and close_response["status_code"] == 200:
                    print(f"   Status: {Colors.GREEN}{close_response['status_code']} OK{Colors.END}")
                    print(f"   {Colors.GREEN}✅ Issue đã được đóng!{Colors.END}")
                    crud_examples.append({
                        "operation": "CLOSE (DELETE equivalent)",
                        "method": "PATCH",
                        "endpoint": f"/repos/{owner}/{repo}/issues/{created_issue_number}",
                        "description": "Đóng issue (GitHub không cho DELETE issues, chỉ close)",
                        "note": "GitHub issues không thể xóa, chỉ có thể close"
                    })
                else:
                    print(f"   Status: {Colors.RED}{close_response.get('status_code', 'Error')}{Colors.END}")
                    
            else:
                error_msg = create_response.get("data", {}).get("message", "Unknown error")
                print(f"   Status: {Colors.RED}{create_response.get('status_code', 'Error')}{Colors.END}")
                print(f"   {Colors.RED}❌ Không thể tạo issue: {error_msg}{Colors.END}")
                print(f"   {Colors.YELLOW}💡 Cần GitHub Token với quyền 'repo' để tạo issues{Colors.END}")
        
        else:
            # Non-demo mode: Chỉ hiển thị structure
            print(f"\n{Colors.CYAN}✏️ CREATE Operation (Structure):{Colors.END}")
            print(f"   POST /repos/{owner}/{repo}/issues")
            print(f"   Body: {json.dumps({'title': 'Issue title', 'body': 'Issue description'}, indent=4)}")
            crud_examples.append({
                "operation": "CREATE",
                "method": "POST",
                "endpoint": f"/repos/{owner}/{repo}/issues",
                "description": "Tạo issue mới",
                "required_fields": ["title"],
                "optional_fields": ["body", "assignees", "labels", "milestone"]
            })
            
            # UPDATE - Example structure
            print(f"\n{Colors.CYAN}🔄 UPDATE Operation (Structure):{Colors.END}")
            print(f"   PATCH /repos/{owner}/{repo}/issues/{{issue_number}}")
            print(f"   Body: {json.dumps({'title': 'Updated title', 'state': 'closed'}, indent=4)}")
            crud_examples.append({
                "operation": "UPDATE",
                "method": "PATCH",
                "endpoint": f"/repos/{owner}/{repo}/issues/{{issue_number}}",
                "description": "Cập nhật issue",
                "note": "GitHub sử dụng PATCH thay vì PUT cho partial updates"
            })
            
            # DELETE - Example structure
            print(f"\n{Colors.CYAN}🗑️ DELETE/CLOSE Operation (Structure):{Colors.END}")
            print(f"   PATCH /repos/{owner}/{repo}/issues/{{issue_number}}")
            print(f"   Body: {json.dumps({'state': 'closed'}, indent=4)}")
            crud_examples.append({
                "operation": "CLOSE (DELETE equivalent)",
                "method": "PATCH",
                "endpoint": f"/repos/{owner}/{repo}/issues/{{issue_number}}",
                "description": "Đóng issue",
                "note": "GitHub không cho xóa issues, chỉ close. Comments có thể DELETE thật."
            })
            
            print(f"\n{Colors.YELLOW}💡 Tip: Chọn option [1a] từ menu để chạy CRUD demo thật!{Colors.END}")
        
        self.analysis_results["crud"] = crud_examples
        
        # Summary
        print(f"\n{Colors.YELLOW}📊 CRUD Pattern Summary:{Colors.END}")
        print(f"   • CREATE: POST requests để tạo resources mới")
        print(f"   • READ: GET requests để lấy single resource hoặc collection")
        print(f"   • UPDATE: PATCH requests cho partial updates (GitHub style)")
        print(f"   • DELETE: DELETE requests để xóa resources")
        
        return {"crud_examples": crud_examples}
    
    # ==================== Webhook Pattern Analysis ====================
    
    def analyze_webhook_pattern(self, owner: str, repo: str) -> Dict:
        """
        Phân tích Webhook pattern trong GitHub API
        
        Webhooks cho phép nhận thông báo real-time khi events xảy ra
        """
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}2. WEBHOOK PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
        
        webhook_info = []
        
        # List webhooks (requires authentication)
        print(f"\n{Colors.CYAN}📡 Webhook Endpoints:{Colors.END}")
        
        webhook_endpoints = [
            {
                "method": "GET",
                "endpoint": f"/repos/{owner}/{repo}/hooks",
                "description": "Liệt kê tất cả webhooks của repository"
            },
            {
                "method": "POST",
                "endpoint": f"/repos/{owner}/{repo}/hooks",
                "description": "Tạo webhook mới",
                "payload_example": {
                    "name": "web",
                    "active": True,
                    "events": ["push", "pull_request"],
                    "config": {
                        "url": "https://example.com/webhook",
                        "content_type": "json",
                        "secret": "your-secret-key"
                    }
                }
            },
            {
                "method": "GET",
                "endpoint": f"/repos/{owner}/{repo}/hooks/{{hook_id}}",
                "description": "Lấy thông tin webhook cụ thể"
            },
            {
                "method": "PATCH",
                "endpoint": f"/repos/{owner}/{repo}/hooks/{{hook_id}}",
                "description": "Cập nhật webhook"
            },
            {
                "method": "DELETE",
                "endpoint": f"/repos/{owner}/{repo}/hooks/{{hook_id}}",
                "description": "Xóa webhook"
            },
            {
                "method": "POST",
                "endpoint": f"/repos/{owner}/{repo}/hooks/{{hook_id}}/pings",
                "description": "Ping webhook để test"
            }
        ]
        
        for endpoint in webhook_endpoints:
            print(f"   {endpoint['method']:6} {endpoint['endpoint']}")
            print(f"          └─ {endpoint['description']}")
            webhook_info.append(endpoint)
        
        # Webhook Events
        print(f"\n{Colors.CYAN}🎯 Available Webhook Events:{Colors.END}")
        webhook_events = [
            ("push", "Khi code được push lên repository"),
            ("pull_request", "Khi PR được tạo, updated, merged, closed"),
            ("issues", "Khi issue được tạo, edited, closed"),
            ("issue_comment", "Khi comment được thêm vào issue/PR"),
            ("create", "Khi branch hoặc tag được tạo"),
            ("delete", "Khi branch hoặc tag bị xóa"),
            ("fork", "Khi repository được fork"),
            ("star", "Khi repository được starred"),
            ("watch", "Khi user watch repository"),
            ("release", "Khi release được published"),
            ("deployment", "Khi deployment được tạo"),
            ("deployment_status", "Khi deployment status thay đổi"),
            ("workflow_run", "Khi GitHub Actions workflow chạy"),
            ("check_run", "Khi check run được tạo hoặc completed")
        ]
        
        for event, description in webhook_events:
            print(f"   • {Colors.YELLOW}{event:20}{Colors.END} - {description}")
        
        # Webhook Payload Structure
        print(f"\n{Colors.CYAN}📦 Webhook Payload Structure Example (push event):{Colors.END}")
        webhook_payload_example = {
            "ref": "refs/heads/main",
            "before": "abc123...",
            "after": "def456...",
            "repository": {
                "id": 12345,
                "name": "repo-name",
                "full_name": "owner/repo-name"
            },
            "pusher": {
                "name": "username",
                "email": "user@example.com"
            },
            "sender": {
                "login": "username",
                "id": 67890,
                "type": "User"
            },
            "commits": [
                {
                    "id": "commit-sha",
                    "message": "Commit message",
                    "author": {"name": "Author", "email": "author@example.com"}
                }
            ]
        }
        print(json.dumps(webhook_payload_example, indent=4))
        
        # Webhook Security
        print(f"\n{Colors.CYAN}🔐 Webhook Security:{Colors.END}")
        print(f"   • Secret: Dùng HMAC-SHA256 để verify payload")
        print(f"   • Header: X-Hub-Signature-256 chứa signature")
        print(f"   • Verification Code Example:")
        verification_code = '''
    import hmac
    import hashlib
    
    def verify_webhook_signature(payload, signature, secret):
        expected = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    '''
        print(verification_code)
        
        self.analysis_results["webhook"] = {
            "endpoints": webhook_endpoints,
            "events": webhook_events,
            "payload_example": webhook_payload_example
        }
        
        return self.analysis_results["webhook"]
    
    # ==================== Event-Driven Pattern Analysis ====================
    
    def analyze_event_driven_pattern(self, owner: str, repo: str) -> Dict:
        """
        Phân tích Event-driven pattern trong GitHub API
        
        GitHub sử dụng events để track tất cả hoạt động
        """
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}3. EVENT-DRIVEN PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
        
        event_info = []
        
        # Get repository events
        print(f"\n{Colors.CYAN}📅 Repository Events:{Colors.END}")
        events_response = self.make_request(f"/repos/{owner}/{repo}/events", params={"per_page": 5})
        
        if "error" not in events_response and events_response["status_code"] == 200:
            print(f"   GET /repos/{owner}/{repo}/events")
            print(f"   Status: {Colors.GREEN}{events_response['status_code']}{Colors.END}")
            
            if events_response["data"]:
                print(f"\n   {Colors.CYAN}Recent Events:{Colors.END}")
                for event in events_response["data"][:5]:
                    event_type = event.get("type", "Unknown")
                    actor = event.get("actor", {}).get("login", "Unknown")
                    created_at = event.get("created_at", "")
                    print(f"   • {Colors.YELLOW}{event_type:25}{Colors.END} by {actor} at {created_at}")
                    event_info.append({
                        "type": event_type,
                        "actor": actor,
                        "created_at": created_at
                    })
        
        # Event Types
        print(f"\n{Colors.CYAN}🎭 GitHub Event Types:{Colors.END}")
        event_types = [
            ("PushEvent", "Push commits to branch"),
            ("PullRequestEvent", "PR opened, closed, merged"),
            ("IssuesEvent", "Issue opened, closed, edited"),
            ("IssueCommentEvent", "Comment on issue/PR"),
            ("CreateEvent", "Branch/tag created"),
            ("DeleteEvent", "Branch/tag deleted"),
            ("ForkEvent", "Repository forked"),
            ("WatchEvent", "Repository starred"),
            ("ReleaseEvent", "Release published"),
            ("CommitCommentEvent", "Comment on commit"),
            ("GollumEvent", "Wiki page created/updated"),
            ("MemberEvent", "Collaborator added"),
            ("PublicEvent", "Repository made public")
        ]
        
        for event_type, description in event_types:
            print(f"   • {Colors.GREEN}{event_type:25}{Colors.END} - {description}")
        
        # Event API Endpoints
        print(f"\n{Colors.CYAN}📡 Event API Endpoints:{Colors.END}")
        event_endpoints = [
            ("GET", "/events", "Public events across GitHub"),
            ("GET", f"/repos/{owner}/{repo}/events", "Repository events"),
            ("GET", f"/users/{owner}/events", "User's public events"),
            ("GET", f"/users/{owner}/events/public", "User's public events only"),
            ("GET", f"/users/{owner}/received_events", "Events received by user"),
            ("GET", f"/orgs/{{org}}/events", "Organization events"),
            ("GET", f"/networks/{owner}/{repo}/events", "Network events")
        ]
        
        for method, endpoint, description in event_endpoints:
            print(f"   {method:4} {endpoint}")
            print(f"        └─ {description}")
        
        # Event Payload Structure
        print(f"\n{Colors.CYAN}📦 Event Payload Structure:{Colors.END}")
        event_payload_example = {
            "id": "12345678901",
            "type": "PushEvent",
            "actor": {
                "id": 123,
                "login": "username",
                "avatar_url": "https://avatars.githubusercontent.com/u/123"
            },
            "repo": {
                "id": 456,
                "name": "owner/repo",
                "url": "https://api.github.com/repos/owner/repo"
            },
            "payload": {
                "push_id": 789,
                "size": 1,
                "commits": [{"sha": "abc123", "message": "Commit message"}]
            },
            "public": True,
            "created_at": "2025-11-24T12:00:00Z"
        }
        print(json.dumps(event_payload_example, indent=4))
        
        # Event-driven Architecture Benefits
        print(f"\n{Colors.CYAN}✅ Event-driven Benefits in GitHub API:{Colors.END}")
        print(f"   • Audit Trail: Theo dõi tất cả hoạt động")
        print(f"   • Real-time Updates: Kết hợp với webhooks")
        print(f"   • Activity Feeds: Hiển thị hoạt động cho users")
        print(f"   • Analytics: Phân tích patterns sử dụng")
        print(f"   • Decoupling: Services có thể react độc lập với events")
        
        self.analysis_results["event_driven"] = {
            "recent_events": event_info,
            "event_types": event_types,
            "endpoints": event_endpoints
        }
        
        return self.analysis_results["event_driven"]
    
    # ==================== Query Pattern Analysis ====================
    
    def analyze_query_pattern(self, owner: str, repo: str) -> Dict:
        """
        Phân tích Query pattern trong GitHub API
        
        GitHub cung cấp powerful query parameters cho filtering, pagination, sorting
        """
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}4. QUERY PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
        
        query_info = []
        
        # Pagination
        print(f"\n{Colors.CYAN}📄 Pagination Parameters:{Colors.END}")
        pagination_params = [
            ("per_page", "Số items mỗi trang (max 100)", "?per_page=50"),
            ("page", "Số trang hiện tại", "?page=2"),
            ("cursor", "Cursor-based pagination (GraphQL)", "after: cursor")
        ]
        for param, description, example in pagination_params:
            print(f"   • {Colors.YELLOW}{param:15}{Colors.END} - {description}")
            print(f"                      Example: {example}")
        
        # Demo pagination with Link header
        print(f"\n{Colors.CYAN}🔗 Link Header Pagination:{Colors.END}")
        issues_response = self.make_request(f"/repos/{owner}/{repo}/issues", params={"per_page": 2})
        if "error" not in issues_response:
            link_header = issues_response["headers"].get("Link", "")
            if link_header:
                print(f"   Link Header: {link_header[:100]}...")
                print(f"\n   Parsed Links:")
                links = self._parse_link_header(link_header)
                for rel, url in links.items():
                    print(f"   • {rel}: {url[:60]}...")
        
        # Filtering
        print(f"\n{Colors.CYAN}🔍 Filtering Parameters:{Colors.END}")
        filter_examples = [
            {
                "endpoint": "/repos/{owner}/{repo}/issues",
                "params": {
                    "state": "open|closed|all",
                    "labels": "bug,enhancement",
                    "assignee": "username",
                    "creator": "username",
                    "mentioned": "username",
                    "milestone": "1 or none or *",
                    "since": "2025-01-01T00:00:00Z"
                }
            },
            {
                "endpoint": "/repos/{owner}/{repo}/pulls",
                "params": {
                    "state": "open|closed|all",
                    "head": "user:branch",
                    "base": "main",
                    "sort": "created|updated|popularity",
                    "direction": "asc|desc"
                }
            },
            {
                "endpoint": "/repos/{owner}/{repo}/commits",
                "params": {
                    "sha": "branch or commit SHA",
                    "path": "path/to/file",
                    "author": "username or email",
                    "since": "2025-01-01T00:00:00Z",
                    "until": "2025-12-31T23:59:59Z"
                }
            }
        ]
        
        for example in filter_examples:
            print(f"\n   Endpoint: {Colors.GREEN}{example['endpoint']}{Colors.END}")
            for param, values in example["params"].items():
                print(f"      • {param}: {values}")
        
        # Search API
        print(f"\n{Colors.CYAN}🔎 Search API (Advanced Query):{Colors.END}")
        search_examples = [
            {
                "endpoint": "/search/repositories",
                "query": "language:python stars:>1000",
                "description": "Tìm Python repos với >1000 stars"
            },
            {
                "endpoint": "/search/issues",
                "query": "repo:owner/repo is:open label:bug",
                "description": "Tìm open bugs trong repo"
            },
            {
                "endpoint": "/search/code",
                "query": "filename:requirements.txt flask",
                "description": "Tìm files requirements.txt chứa flask"
            },
            {
                "endpoint": "/search/users",
                "query": "location:vietnam language:python",
                "description": "Tìm Python developers ở Vietnam"
            }
        ]
        
        for example in search_examples:
            print(f"\n   {Colors.GREEN}{example['endpoint']}{Colors.END}")
            print(f"      Query: {example['query']}")
            print(f"      └─ {example['description']}")
        
        # Demo search
        print(f"\n{Colors.CYAN}📊 Search Demo:{Colors.END}")
        search_response = self.make_request("/search/repositories", params={
            "q": f"repo:{owner}/{repo}",
            "per_page": 1
        })
        if "error" not in search_response and search_response["status_code"] == 200:
            print(f"   Search: repo:{owner}/{repo}")
            data = search_response["data"]
            print(f"   Total Count: {data.get('total_count', 0)}")
            if data.get("items"):
                repo_data = data["items"][0]
                print(f"   Result: {repo_data.get('full_name')}")
                print(f"   Stars: {repo_data.get('stargazers_count')}")
        
        # Sorting
        print(f"\n{Colors.CYAN}📈 Sorting Parameters:{Colors.END}")
        sort_examples = [
            ("Issues", "sort=created|updated|comments", "direction=asc|desc"),
            ("PRs", "sort=created|updated|popularity|long-running", "direction=asc|desc"),
            ("Repos", "sort=created|updated|pushed|full_name", "direction=asc|desc"),
            ("Search", "sort=stars|forks|help-wanted-issues|updated", "order=asc|desc")
        ]
        for resource, sort_values, direction in sort_examples:
            print(f"   • {Colors.YELLOW}{resource:10}{Colors.END} {sort_values} | {direction}")
        
        self.analysis_results["query"] = {
            "pagination": pagination_params,
            "filtering": filter_examples,
            "search": search_examples,
            "sorting": sort_examples
        }
        
        return self.analysis_results["query"]
    
    def _parse_link_header(self, link_header: str) -> Dict[str, str]:
        """Parse Link header để extract pagination URLs"""
        links = {}
        for part in link_header.split(","):
            match = re.match(r'<([^>]+)>;\s*rel="([^"]+)"', part.strip())
            if match:
                links[match.group(2)] = match.group(1)
        return links
    
    # ==================== HATEOAS Pattern Analysis ====================
    
    def analyze_hateoas_pattern(self, owner: str, repo: str) -> Dict:
        """
        Phân tích HATEOAS pattern trong GitHub API
        
        HATEOAS = Hypermedia as the Engine of Application State
        API trả về links để navigate đến related resources
        """
        print(f"\n{Colors.BOLD}{Colors.RED}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}5. HATEOAS PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.RED}{'='*70}{Colors.END}")
        
        hateoas_info = []
        
        # Get repository to show HATEOAS links
        print(f"\n{Colors.CYAN}🔗 HATEOAS in Repository Response:{Colors.END}")
        repo_response = self.make_request(f"/repos/{owner}/{repo}")
        
        if "error" not in repo_response and repo_response["status_code"] == 200:
            data = repo_response["data"]
            
            # Extract all _url fields (HATEOAS links)
            print(f"\n   {Colors.GREEN}Hypermedia Links trong response:{Colors.END}")
            url_fields = {k: v for k, v in data.items() if k.endswith("_url") and v}
            
            for key, url in list(url_fields.items())[:15]:
                print(f"   • {Colors.YELLOW}{key:30}{Colors.END}")
                print(f"     {url[:70]}...")
                hateoas_info.append({"field": key, "url": url})
        
        # Show HATEOAS structure
        print(f"\n{Colors.CYAN}📋 HATEOAS Response Structure:{Colors.END}")
        hateoas_example = {
            "id": 12345,
            "name": "repository-name",
            "full_name": "owner/repository-name",
            "html_url": "https://github.com/owner/repository-name",
            "url": "https://api.github.com/repos/owner/repository-name",
            "# HATEOAS Links": "---",
            "forks_url": "https://api.github.com/repos/owner/repo/forks",
            "keys_url": "https://api.github.com/repos/owner/repo/keys{/key_id}",
            "collaborators_url": "https://api.github.com/repos/owner/repo/collaborators{/collaborator}",
            "teams_url": "https://api.github.com/repos/owner/repo/teams",
            "hooks_url": "https://api.github.com/repos/owner/repo/hooks",
            "issues_url": "https://api.github.com/repos/owner/repo/issues{/number}",
            "pulls_url": "https://api.github.com/repos/owner/repo/pulls{/number}",
            "branches_url": "https://api.github.com/repos/owner/repo/branches{/branch}",
            "commits_url": "https://api.github.com/repos/owner/repo/commits{/sha}",
            "# Related Resources": "---",
            "owner": {
                "login": "owner",
                "url": "https://api.github.com/users/owner",
                "html_url": "https://github.com/owner",
                "repos_url": "https://api.github.com/users/owner/repos"
            }
        }
        print(json.dumps(hateoas_example, indent=4))
        
        # URI Templates
        print(f"\n{Colors.CYAN}📝 URI Templates (RFC 6570):{Colors.END}")
        uri_templates = [
            ("issues_url", "https://api.github.com/repos/owner/repo/issues{/number}"),
            ("pulls_url", "https://api.github.com/repos/owner/repo/pulls{/number}"),
            ("branches_url", "https://api.github.com/repos/owner/repo/branches{/branch}"),
            ("commits_url", "https://api.github.com/repos/owner/repo/commits{/sha}"),
            ("keys_url", "https://api.github.com/repos/owner/repo/keys{/key_id}")
        ]
        
        print(f"\n   GitHub sử dụng URI Templates theo RFC 6570:")
        for name, template in uri_templates:
            print(f"   • {Colors.YELLOW}{name}{Colors.END}")
            print(f"     Template: {template}")
            # Show how to expand
            if "{/number}" in template:
                expanded = template.replace("{/number}", "/42")
                print(f"     Expanded: {expanded}")
        
        # HATEOAS Navigation
        print(f"\n{Colors.CYAN}🧭 HATEOAS Navigation Example:{Colors.END}")
        navigation_example = """
    # Client không cần hardcode URLs, follow links từ response
    
    # 1. Bắt đầu từ root
    response = GET("https://api.github.com")
    
    # 2. Follow link đến user
    user_url = response["current_user_url"]
    user = GET(user_url)
    
    # 3. Follow link đến repos
    repos_url = user["repos_url"]
    repos = GET(repos_url)
    
    # 4. Follow link đến specific repo
    repo = repos[0]
    issues_url = repo["issues_url"].replace("{/number}", "")
    issues = GET(issues_url)
    
    # 5. Follow link đến specific issue
    issue = issues[0]
    comments_url = issue["comments_url"]
    comments = GET(comments_url)
    """
        print(navigation_example)
        
        # Benefits
        print(f"\n{Colors.CYAN}✅ HATEOAS Benefits:{Colors.END}")
        print(f"   • Self-documenting: API response chứa tất cả available actions")
        print(f"   • Loose coupling: Client không cần biết URL structure")
        print(f"   • Evolvability: Server có thể thay đổi URLs mà không break clients")
        print(f"   • Discoverability: Client có thể khám phá API bằng following links")
        print(f"   • State Transitions: Links cho biết actions available ở current state")
        
        # Root API endpoint
        print(f"\n{Colors.CYAN}🌐 Root API Endpoint (Entry Point):{Colors.END}")
        root_response = self.make_request("")
        if "error" not in root_response and root_response["status_code"] == 200:
            print(f"   GET https://api.github.com/")
            print(f"\n   Available endpoints (HATEOAS links):")
            for key, url in list(root_response["data"].items())[:10]:
                print(f"   • {Colors.YELLOW}{key:30}{Colors.END} → {url[:50]}...")
        
        self.analysis_results["hateoas"] = {
            "url_fields": hateoas_info,
            "uri_templates": uri_templates,
            "navigation_example": navigation_example
        }
        
        return self.analysis_results["hateoas"]
    
    # ==================== Full Analysis ====================
    
    def run_full_analysis(self, owner: str = "octocat", repo: str = "Hello-World") -> Dict:
        """
        Chạy phân tích đầy đủ tất cả patterns
        
        Args:
            owner: GitHub username/organization
            repo: Repository name
            
        Returns:
            Dictionary chứa tất cả analysis results
        """
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}   GITHUB API PATTERN ANALYSIS{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}   Repository: {owner}/{repo}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        
        # Check rate limit
        rate_limit = self.make_request("/rate_limit")
        if "error" not in rate_limit:
            core = rate_limit["data"].get("resources", {}).get("core", {})
            print(f"\n{Colors.CYAN}📊 Rate Limit:{Colors.END}")
            print(f"   Remaining: {core.get('remaining', 'N/A')}/{core.get('limit', 'N/A')}")
        
        # Run all analyses
        self.analyze_crud_pattern(owner, repo)
        self.analyze_webhook_pattern(owner, repo)
        self.analyze_event_driven_pattern(owner, repo)
        self.analyze_query_pattern(owner, repo)
        self.analyze_hateoas_pattern(owner, repo)
        
        # Summary
        self.print_summary()
        
        return self.analysis_results
    
    def print_summary(self):
        """In tổng kết các patterns tìm được"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}   ANALYSIS SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        
        summary = f"""
{Colors.BOLD}1. CRUD Pattern:{Colors.END}
   ✅ CREATE: POST requests để tạo resources (issues, PRs, comments)
   ✅ READ: GET requests cho single resource và collections
   ✅ UPDATE: PATCH requests cho partial updates
   ✅ DELETE: DELETE requests để remove resources

{Colors.BOLD}2. Webhook Pattern:{Colors.END}
   ✅ Real-time notifications qua HTTP POST
   ✅ 40+ event types (push, PR, issues, etc.)
   ✅ HMAC signature verification
   ✅ Configurable per repository

{Colors.BOLD}3. Event-driven Pattern:{Colors.END}
   ✅ Centralized event logging
   ✅ Activity feeds và timelines
   ✅ Event types cho mọi action
   ✅ Audit trail cho compliance

{Colors.BOLD}4. Query Pattern:{Colors.END}
   ✅ Pagination (per_page, page, Link header)
   ✅ Filtering (state, labels, assignee, etc.)
   ✅ Sorting (sort, direction)
   ✅ Search API với query syntax

{Colors.BOLD}5. HATEOAS Pattern:{Colors.END}
   ✅ Self-describing responses với *_url fields
   ✅ URI Templates (RFC 6570)
   ✅ Navigable API structure
   ✅ Root endpoint là entry point

{Colors.BOLD}Conclusion:{Colors.END}
   GitHub API là một ví dụ tuyệt vời về RESTful API design,
   implementing đầy đủ các REST constraints và patterns.
   API cho phép clients navigate bằng following links (HATEOAS),
   query data linh hoạt, nhận real-time updates qua webhooks,
   và thực hiện CRUD operations trên resources.
"""
        print(summary)


def print_menu():
    """Hiển thị menu chọn pattern"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}   GITHUB API PATTERN ANALYZER - MENU{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"""
{Colors.BOLD}Chọn pattern để phân tích:{Colors.END}

   {Colors.BLUE}[1]{Colors.END}  CRUD Pattern        - Create, Read, Update, Delete (chỉ xem)
   {Colors.BLUE}[1a]{Colors.END} CRUD Pattern DEMO   - 🚀 Tạo issue THẬT trên GitHub!
   {Colors.GREEN}[2]{Colors.END}  Webhook Pattern     - Real-time notifications
   {Colors.YELLOW}[3]{Colors.END}  Event-driven Pattern - Activity events và tracking
   {Colors.CYAN}[4]{Colors.END}  Query Pattern       - Filtering, Pagination, Sorting, Search
   {Colors.RED}[5]{Colors.END}  HATEOAS Pattern     - Hypermedia links và navigation

   {Colors.BOLD}[6]{Colors.END}  Chạy TẤT CẢ patterns
   {Colors.BOLD}[7]{Colors.END}  Xem Rate Limit
   {Colors.BOLD}[8]{Colors.END}  Thay đổi Repository
   {Colors.BOLD}[9]{Colors.END}  Lưu kết quả vào JSON
   {Colors.BOLD}[0]{Colors.END}  Thoát

{'='*70}
    """)


def main():
    """Main function với interactive menu"""
    import sys
    import os
    
    # Get GitHub token from environment (optional)
    token = os.environ.get("GITHUB_TOKEN")
    
    # Create analyzer
    analyzer = GitHubAPIAnalyzer(token=token)
    
    # Default repository - YOUR REPO
    owner = "tuanjhg"
    repo = "INT3505E_02_demo"
    
    # Allow command line arguments để override
    if len(sys.argv) >= 3:
        owner = sys.argv[1]
        repo = sys.argv[2]
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}   GITHUB API PATTERN ANALYZER{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"\n{Colors.CYAN}Repository hiện tại:{Colors.END} {Colors.GREEN}{owner}/{repo}{Colors.END}")
    
    if token:
        print(f"{Colors.GREEN}✅ GitHub Token đã được cấu hình{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  Không có GitHub Token - Rate limit thấp hơn (60 req/hour){Colors.END}")
        print(f"   Set GITHUB_TOKEN environment variable để tăng limit")
    
    # Main loop
    while True:
        print_menu()
        choice = input(f"{Colors.BOLD}Nhập lựa chọn (0-9, 1a): {Colors.END}").strip().lower()
        
        if choice == "1":
            print(f"\n{Colors.BLUE}Đang phân tích CRUD Pattern (chỉ xem)...{Colors.END}")
            analyzer.analyze_crud_pattern(owner, repo, demo_mode=False)
            
        elif choice == "1a":
            print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.YELLOW}   🚀 CRUD DEMO MODE{Colors.END}")
            print(f"{Colors.BOLD}{Colors.YELLOW}{'='*70}{Colors.END}")
            print(f"\n{Colors.YELLOW}⚠️  CẢNH BÁO: Chế độ này sẽ:{Colors.END}")
            print(f"   1. Tạo một issue MỚI trên repo {owner}/{repo}")
            print(f"   2. Cập nhật issue đó")
            print(f"   3. Đóng issue đó")
            print(f"\n{Colors.CYAN}Yêu cầu: GitHub Token với quyền 'repo'{Colors.END}")
            
            if not token:
                print(f"\n{Colors.RED}❌ Không tìm thấy GITHUB_TOKEN!{Colors.END}")
                print(f"   Hãy set environment variable: ")
                print(f"   Windows:  $env:GITHUB_TOKEN='your-token-here'")
                print(f"   Linux:    export GITHUB_TOKEN='your-token-here'")
            else:
                confirm = input(f"\n{Colors.BOLD}Tiếp tục? (y/n): {Colors.END}").strip().lower()
                if confirm == 'y':
                    print(f"\n{Colors.BLUE}Đang thực hiện CRUD operations thật...{Colors.END}")
                    analyzer.analyze_crud_pattern(owner, repo, demo_mode=True)
                else:
                    print(f"{Colors.YELLOW}Đã hủy.{Colors.END}")
            
        elif choice == "2":
            print(f"\n{Colors.GREEN}Đang phân tích Webhook Pattern...{Colors.END}")
            analyzer.analyze_webhook_pattern(owner, repo)
            
        elif choice == "3":
            print(f"\n{Colors.YELLOW}Đang phân tích Event-driven Pattern...{Colors.END}")
            analyzer.analyze_event_driven_pattern(owner, repo)
            
        elif choice == "4":
            print(f"\n{Colors.CYAN}Đang phân tích Query Pattern...{Colors.END}")
            analyzer.analyze_query_pattern(owner, repo)
            
        elif choice == "5":
            print(f"\n{Colors.RED}Đang phân tích HATEOAS Pattern...{Colors.END}")
            analyzer.analyze_hateoas_pattern(owner, repo)
            
        elif choice == "6":
            print(f"\n{Colors.BOLD}Đang chạy phân tích TẤT CẢ patterns...{Colors.END}")
            analyzer.run_full_analysis(owner, repo)
            
        elif choice == "7":
            # Check rate limit
            print(f"\n{Colors.CYAN}Đang kiểm tra Rate Limit...{Colors.END}")
            rate_limit = analyzer.make_request("/rate_limit")
            if "error" not in rate_limit:
                core = rate_limit["data"].get("resources", {}).get("core", {})
                search = rate_limit["data"].get("resources", {}).get("search", {})
                print(f"\n{Colors.BOLD}Rate Limit Status:{Colors.END}")
                print(f"   Core API:   {core.get('remaining', 'N/A')}/{core.get('limit', 'N/A')} requests")
                print(f"   Search API: {search.get('remaining', 'N/A')}/{search.get('limit', 'N/A')} requests")
                reset_time = core.get('reset')
                if reset_time:
                    from datetime import datetime
                    reset_dt = datetime.fromtimestamp(reset_time)
                    print(f"   Reset time: {reset_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"{Colors.RED}Lỗi khi kiểm tra rate limit{Colors.END}")
                
        elif choice == "8":
            # Change repository
            print(f"\n{Colors.CYAN}Thay đổi Repository:{Colors.END}")
            new_owner = input(f"   Nhập owner (hiện tại: {owner}): ").strip()
            new_repo = input(f"   Nhập repo name (hiện tại: {repo}): ").strip()
            
            if new_owner:
                owner = new_owner
            if new_repo:
                repo = new_repo
            
            print(f"\n{Colors.GREEN}✅ Đã chuyển sang repository: {owner}/{repo}{Colors.END}")
            
            # Verify repository exists
            verify = analyzer.make_request(f"/repos/{owner}/{repo}")
            if "error" in verify or verify.get("status_code") != 200:
                print(f"{Colors.YELLOW}⚠️  Không thể truy cập repository. Có thể repo private hoặc không tồn tại.{Colors.END}")
            else:
                repo_data = verify["data"]
                print(f"   Repository: {repo_data.get('full_name')}")
                print(f"   Description: {repo_data.get('description', 'N/A')}")
                print(f"   Stars: {repo_data.get('stargazers_count', 0)}")
                print(f"   Forks: {repo_data.get('forks_count', 0)}")
                
        elif choice == "9":
            # Save results
            if not any(analyzer.analysis_results.values()):
                print(f"\n{Colors.YELLOW}⚠️  Chưa có kết quả nào để lưu. Hãy chạy phân tích trước!{Colors.END}")
            else:
                filename = f"github_api_analysis_{owner}_{repo}.json"
                filename = input(f"   Nhập tên file (mặc định: {filename}): ").strip() or filename
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(analyzer.analysis_results, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n{Colors.GREEN}✅ Đã lưu kết quả vào {filename}{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}Lỗi khi lưu file: {e}{Colors.END}")
                    
        elif choice == "0":
            print(f"\n{Colors.GREEN}Cảm ơn đã sử dụng GitHub API Pattern Analyzer!{Colors.END}")
            print(f"{Colors.CYAN}Goodbye! 👋{Colors.END}\n")
            break
            
        else:
            print(f"\n{Colors.RED}❌ Lựa chọn không hợp lệ. Vui lòng nhập số từ 0-9.{Colors.END}")
        
        # Pause before showing menu again
        input(f"\n{Colors.CYAN}Nhấn Enter để tiếp tục...{Colors.END}")


if __name__ == "__main__":
    main()
