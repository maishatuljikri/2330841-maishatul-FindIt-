# Technical Design Document (TDD)
## FindIt – Campus Lost and Found System

### 1. Architecture
A client-server web application with a React + TypeScript frontend, FastAPI + Python backend, REST APIs, and a relational database (SQLite for local development; PostgreSQL is an optional production choice).

### 2. High-Level Flow
Browser (React) -> HTTP/JSON REST API (FastAPI) -> Database

### 3. Frontend Design
- React with TypeScript.
- Pages: Login/Register, Report List, Report Detail, New Report, My Reports, Claims, Admin Dashboard.
- Components: navigation, search filters, report cards, report forms, claim forms.
- API client attaches access token to protected requests.

### 4. Backend Design
- FastAPI routers: auth, reports, claims, admin.
- Services apply business rules; database layer handles persistence.
- Input and output schemas use Pydantic validation.
- Passwords stored as hashes; tokens validated on each protected request.
- Server-side role and ownership checks prevent unauthorized operations.

### 5. Proposed API Endpoints
| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | /api/register | Public | Register user |
| POST | /api/login | Public | Authenticate and issue token |
| GET | /api/reports | Public | Browse/search reports |
| GET | /api/reports/{id} | Public | Report details |
| POST | /api/reports | User | Create report |
| PATCH | /api/reports/{id} | Owner/Admin | Update report |
| POST | /api/reports/{id}/claims | User | Submit claim |
| GET | /api/admin/claims | Admin | Review claims |
| PATCH | /api/admin/claims/{id} | Admin | Update claim status |

*These are proposed endpoints; align names and implementation with the repository before claiming they are complete.*

### 6. Database Relationships
- One User has many ItemReports.
- One User has many Claims.
- One ItemReport has many Claims.

### 7. Access Control
- Public: browse/search public reports.
- User: post, edit own reports, submit claims.
- Admin: review claims and moderate reports.
- Secure each restricted API using authenticated identity and role checks.

### 8. Development and Testing
- Start FastAPI backend and verify generated Swagger API docs at /docs.
- Run React frontend and confirm API integration.
- Test authentication, report creation, searching, ownership restrictions, claim privacy, and admin permissions.
- Use environment variables for secrets; do not commit production credentials.

### 9. Future Improvements
Campus email verification, attachment uploads, notification emails, and audit history.
