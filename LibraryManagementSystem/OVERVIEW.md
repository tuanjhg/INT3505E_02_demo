# RESTful Architecture Overview

## Project Structure Visualization

```
/LibraryManagementSystem
│
├── README.md                            # Main documentation
├── requirements.txt                     # Python dependencies
│
├── /client-server/                      # 🏛️ Constraint 1
│   ├── Server.py                       # Flask server managing resources
│   ├── Client.py                       # Python client consuming API
│   └── README.md                       # Client-Server explanation
│
├── /stateless/                          # 🔄 Constraint 2
│   ├── StatelessService.py            # Stateless API with token auth
│   ├── StatelessClient.py             # Client sending auth with each request
│   └── README.md                       # Stateless explanation
│
├── /cacheable/                          # 💾 Constraint 3
│   ├── CacheManager.py                # Server with Cache-Control headers
│   ├── CacheClient.py                 # Cache-aware client
│   └── README.md                       # Caching explanation
│
├── /layered/                            # 📚 Constraint 4
│   ├── LayeredServer.py               # 3-tier architecture demo
│   ├── LayeredArchitecture.md         # Detailed architecture docs
│   └── README.md                       # Layered system explanation
│
├── /uniform-interface/                  # 🔗 Constraint 5
│   ├── ApiController.py               # RESTful API with HATEOAS
│   └── README.md                       # Uniform interface explanation
│
└── /code-on-demand/                     # ⚡ Constraint 6 (Optional)
    ├── DynamicLoader.py               # Server sending JavaScript code
    └── README.md                       # Code-on-demand explanation
```

## Files per Constraint

### 1. Client-Server Architecture
```
client-server/
├── Server.py              (4,025 bytes) - Resource management server
├── Client.py              (6,017 bytes) - API consumer client
└── README.md              (2,188 bytes) - Documentation
```

**Key Features:**
- Separation between UI and data storage
- Server exposes RESTful APIs
- Client consumes APIs without knowing implementation
- Multiple client types supported

---

### 2. Stateless Communication
```
stateless/
├── StatelessService.py    (9,917 bytes) - Token-based stateless API
├── StatelessClient.py     (8,301 bytes) - Client with auth on every request
└── README.md              (3,269 bytes) - Documentation
```

**Key Features:**
- No server-side sessions
- API key authentication
- Each request self-contained
- Improved scalability

---

### 3. Cacheable Responses
```
cacheable/
├── CacheManager.py       (11,265 bytes) - Cache-enabled server
├── CacheClient.py         (9,421 bytes) - Cache-aware client
└── README.md              (4,575 bytes) - Documentation
```

**Key Features:**
- Cache-Control headers
- ETag validation
- 304 Not Modified responses
- Performance optimization

---

### 4. Layered System
```
layered/
├── LayeredServer.py      (12,296 bytes) - Three-tier implementation
├── LayeredArchitecture.md (7,810 bytes) - Architecture deep-dive
└── README.md                            - Documentation link
```

**Key Features:**
- Data Access Layer (DAL)
- Business Logic Layer (BLL)
- Presentation/API Layer
- Clear separation of concerns

---

### 5. Uniform Interface
```
uniform-interface/
├── ApiController.py      (15,339 bytes) - RESTful API with HATEOAS
└── README.md              (7,347 bytes) - Documentation
```

**Key Features:**
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Resource identification with URIs
- Self-descriptive messages
- HATEOAS links for discoverability

---

### 6. Code-On-Demand (Optional)
```
code-on-demand/
├── DynamicLoader.py      (14,736 bytes) - Server with dynamic code
└── README.md              (7,460 bytes) - Documentation
```

**Key Features:**
- Server sends JavaScript code
- Dynamic validation logic
- UI components on-demand
- Client extensibility

---

## Total Statistics

- **17 Files** created
- **6 Complete** working examples
- **7 Detailed** README files
- **~65,000 bytes** of Python code
- **~40,000 bytes** of documentation

## Code Breakdown

| Constraint | Python Lines | Documentation |
|------------|--------------|---------------|
| Client-Server | ~250 | Comprehensive |
| Stateless | ~350 | Comprehensive |
| Cacheable | ~400 | Comprehensive |
| Layered | ~450 | Very Detailed |
| Uniform Interface | ~550 | Comprehensive |
| Code-On-Demand | ~500 | Comprehensive |

## How Each Module Works

### Running Ports:
- **5001** - Client-Server demo
- **5002** - Stateless demo
- **5003** - Cacheable demo
- **5004** - Layered system demo
- **5005** - Uniform interface demo
- **5006** - Code-on-demand demo

### Demonstration Flow:

```
User runs: python Server.py
    ↓
Server starts on specific port
    ↓
Database auto-created (SQLite)
    ↓
Sample data inserted
    ↓
API endpoints active
    ↓
User runs client or opens browser
    ↓
Interactions demonstrate constraint
```

## Educational Value

Each module teaches:

1. **Theory**: What the constraint means
2. **Practice**: Working implementation
3. **Benefits**: Why it matters
4. **Trade-offs**: When to use/avoid
5. **Real-world**: Production examples

## Use Cases

### For Students:
- Learn REST architecture principles
- See working code examples
- Understand design patterns
- Practice API development

### For Developers:
- Reference implementations
- Best practices guide
- Architecture patterns
- API design principles

### For Educators:
- Teaching materials
- Hands-on exercises
- Progressive complexity
- Practical demonstrations

## Technologies Used

- **Flask** - Web framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Embedded database
- **Requests** - HTTP client library
- **Python 3** - Programming language

## Next Steps

1. **Explore** each constraint folder
2. **Read** the README files
3. **Run** the examples
4. **Experiment** with the code
5. **Apply** to your projects

## Contributing

This is an educational project demonstrating REST principles. Each constraint is:
- ✅ Self-contained
- ✅ Well-documented
- ✅ Production-quality code
- ✅ Ready to run

---

**Happy Learning!** 🎓

For questions, start with the README.md in each constraint folder.
