# Final Project Submission Report

**Independent University, Bangladesh (IUB)**  
**Course:** CSE309 — Web Application & Internet  
**Semester:** Autumn 2026  

---

## Submission Details

| Field | Details |
| :--- | :--- |
| **Name** | Maishatul Jikri Oishi |
| **Student ID** | 2330841 |
| **Section** | 05 |
| **Project Title** | IUB Lost & Found (`FindIt`) |
| **Vercel URL** | `https://2330841-maishatul-findit.vercel.app/` |
| **GitHub Repository** | `https://github.com/maishatuljikri/2330841-maishatul-FindIt-` |
| **Submitted To** | Sayef Reyadh, Adjunct Lecturer, Department of CSE, IUB |
| **Date of Submission** | 28 November 2026 |

---

## Table of Contents

1. [1. Executive Summary](#1-executive-summary)
2. [Part A. Product Requirements (PRD)](#part-a-product-requirements-prd)
3. [Part B. Software Requirements (SRS)](#part-b-software-requirements-srs)
4. [Part C. Technical Design (TDD)](#part-c-technical-design-tdd)
5. [Part D. Evidence: Screenshots of the Running Application](#part-d-evidence-screenshots-of-the-running-application)
6. [Part E. Project Management and Conclusion](#part-e-project-management-and-conclusion)
7. [Appendix. Test Accounts and Video Demo](#appendix-test-accounts-and-video-demo)

### List of Figures and Screenshots

| ID | Caption | Requirement ID |
| :--- | :--- | :--- |
| **Figure 1** | System Architecture Diagram — Browser, Vercel Edge, FastAPI & Database | `NFR-01`–`NFR-05` |
| **Figure 2** | Entity-Relationship (ER) Diagram — `students`, `items`, `refresh_sessions`, `login_attempts` | `C4` |
| **Figure 3** | JWT Sequence Diagram — Login, Protected Request, Expiry, Refresh Rotation & Logout | `FR-AUTH-03`–`07` |
| **S1** | Signup and Login Modal with Validation Error Shown | `FR-AUTH-01`, `FR-AUTH-03` |
| **S2** | Main Lost & Found Board & Student Access Flow | `FR-DOMAIN-01`, `FR-DOMAIN-02` |
| **S3** | Profile Page & Change Password Form Rejecting Wrong Current Password | `FR-AUTH-08`, `FR-AUTH-09` |
| **S4** | Active Authenticated Session & Sign-In/Sign-Out Controls | `FR-AUTH-05`, `FR-AUTH-07` |
| **S5** | Authenticated Board View & Report Ownership Controls | `FR-RBAC-03`, `FR-DOMAIN-03` |
| **S6** | Campus Noticeboard & RBAC Access Enforcement | `FR-RBAC-01`, `FR-RBAC-03` |
| **S7** | Account Settings & Student Profile View | `FR-AUTH-08` |
| **S8** | Session & Security Validation Flow | `FR-AUTH-05`, `FR-AUTH-06` |
| **S9** | Student Authentication & Access Enforcement | `FR-RBAC-05` |
| **S10** | Admin Dashboard Overview Statistics | `FR-ADM-01` |
| **S11** | Admin Student Directory & Live Board Integration | `FR-ADM-02` |
| **S12** | Admin Student Management with Search & Status Filter | `FR-ADM-02`, `FR-ADM-03` |
| **S13** | Reporter Connection & Contact Reveal Modal | `FR-RBAC-04` |
| **S14** | Student Sign-In & Role Access Verification | `FR-RBAC-06` |
| **S15** | Admin Ban Student Dialog with Reason | `FR-ADM-03`, `FR-AUTH-10` |
| **S16** | Admin Dashboard Resulting Banned State & Updated Metrics | `FR-ADM-03`, `FR-ADM-04` |
| **S17** | New Report Submission Form (`Tell the campus community`) | `FR-DOMAIN-02` |
| **S18** | Filtered Board Reports & Owner Edit Controls | `FR-DOMAIN-01`, `FR-RBAC-03` |
| **S19** | Report Category Selection & Validation | `FR-DOMAIN-02` |
| **S20** | Public Landing Page on Vercel (`2330841-maishatul-findit.vercel.app`) | `NFR-05` |
| **S21** | Live Student Sign-In Verification on Production URL | `NFR-06` |

---

## 1. Executive Summary

### 1.1 Project Overview
**IUB Lost & Found** (deployed as **FindIt**) is a centralized campus lost-and-found web application designed for students and administrators at Independent University, Bangladesh (IUB). Students frequently lose items such as ID cards, earbuds, notebooks, keys, and water bottles across campus and rely on scattered social media groups where posts are quickly buried and personal phone numbers are publicly exposed. FindIt solves this by providing a structured, searchable, and filterable board where visitors can browse open and resolved items, authenticated students can publish and manage their own reports with optional photos while keeping contact details behind an authenticated endpoint, and administrators can monitor platform activity and moderate accounts.

**Technology Stack:** React 18 with TypeScript + Vite (Frontend), FastAPI with Python + SQLAlchemy ORM (Backend), PostgreSQL / SQLite (Database), and Vercel (Production Hosting).

### 1.2 What Was Built Since the Mid Assessment
* **JWT Authentication with Refresh & Logout:** Implemented account registration (`/api/auth/register`), Argon2id + HMAC-SHA256 pepper password hashing, 15-minute `HS256` JWT access tokens stored strictly in JavaScript memory, 7-day SHA-256 hashed refresh tokens in `HttpOnly` cookies with rotation and reuse detection (`/api/auth/refresh`), and full server-side logout (`/api/auth/logout`).
* **Role-Based Access Control (RBAC):** Enforced three access levels—Visitor, User (`user`), and Admin (`admin`)—via FastAPI dependencies (`get_jwt_current_user`, `require_roles`) alongside strict per-record ownership (`Item.owner_id`) so only report owners can edit, resolve/reopen, or delete their posts.
* **Admin Dashboard:** Built an Admin Overview (`/api/admin/overview`) displaying real-time student and report statistics, plus a searchable/filterable Student Directory (`/api/admin/students`) with ban/unban moderation (`/api/admin/students/{id}/ban`, `/unban`) that immediately revokes active refresh sessions.
* **Profile & Password Management:** Added self-service profile updates (`GET/PATCH /api/auth/profile`) with mass-assignment protection (`extra='forbid'`) and password changes (`POST /api/auth/change-password`) that revoke all active sessions across devices.
* **Audit Logging & Vercel Deployment:** Implemented persistent authentication event logging (`login_attempts` table capturing identifier, IP address, user-agent, outcome, and failure reason) and deployed both the Vite React frontend and containerized FastAPI backend on Vercel.

### 1.3 Live Links

*Note: Demo account credentials are placed exclusively in the Appendix of the submitted PDF report and are never committed to GitHub.*

| Table 1: Live Deployment & Repository Links | URL |
| :--- | :--- |
| **GitHub Repository** | `https://github.com/maishatuljikri/2330841-maishatul-FindIt-` |
| **Vercel Frontend (Live App)** | `https://2330841-maishatul-findit.vercel.app/` |
| **Vercel Backend API Base** | `https://2330841-maishatul-findit.vercel.app/api` |
| **Live Interactive API Docs** | `https://2330841-maishatul-findit.vercel.app/docs` |
| **Video Demo Link** | `https://www.youtube.com/watch?v=xsEJmKIr9PU` |

---

## Part A. Product Requirements (PRD)

### A1. Problem Statement
Every semester at Independent University, Bangladesh (IUB), students misplace personal belongings—including student ID cards, wireless earbuds, chargers, keys, wallets, and textbooks—across classrooms, labs, the library, and the cafeteria. Currently, students cope by posting messages across fragmented Facebook groups, batch Messenger chats, or informal word-of-mouth channels. Because these channels are chronological chat streams without categories, location tags, or resolution statuses, legitimate posts disappear within hours and finders have no reliable way to verify whether an item has already been claimed.

Furthermore, sharing personal mobile numbers and WhatsApp details publicly on open social media posts exposes students to unsolicited messages and privacy risks, while campus moderators have no way to remove abusive posts or suspend bad actors. A dedicated, privacy-aware campus board with authenticated contact reveal, strict ownership rules, and administrative oversight is essential to make item recovery fast, organized, and safe.

### A2. Users and Roles
The system models three access tiers: unauthenticated Visitors and two persisted database roles (`user` and `admin`). Separate user groups/tenants are not part of the domain model; record-level access is governed by role and item ownership (`Item.owner_id`).

| Table 2: System Users & Roles | Who They Are | Main Tasks | What They Must Never Be Able to Do |
| :--- | :--- | :--- | :--- |
| **Visitor** | Unauthenticated public user browsing the campus board. | Browse reports, search by keyword, filter by lost/found, category, and status, view aggregate counts, and view uploaded item photos. | View reporter phone/WhatsApp or contact instructions; create, edit, or delete reports; access profile or admin routes. |
| **User (`user`)** | Registered IUB student authenticated via JWT access token and `HttpOnly` refresh cookie. | All Visitor tasks plus: register, sign in, create lost/found reports with photos, view reporter contact details, edit/resolve/reopen/delete own reports, update own profile, change password, and log out. | Edit, resolve, or delete another user's report; view admin dashboard or student lists; ban/unban users; modify own role or email. |
| **Admin (`admin`)** | Authorized campus administrator / moderator promoted via bootstrap script. | All User tasks plus: view system-wide student and report overview metrics, search/filter all student accounts, and ban/unban student accounts with an audit reason. | Ban their own account; ban or unban another admin account; forge or bypass JWT signature/expiry verification. |

### A3. Goals and Success Measures

| Table 3: Product & Security Goals | Measurable & Testable Success Measure |
| :--- | :--- |
| **G-01: Centralized Discovery** | Visitors and students can search and filter up to 100 reports by keyword, 8 categories, type (`lost`/`found`), and status (`open`/`resolved`/`all`) in a single view (Yes/No). |
| **G-02: Contact Privacy Protection** | 100% of unauthenticated `GET /api/items` responses return `contact_info: null`, and 100% of guest requests to `GET /api/items/{id}/contact` return HTTP `401`. |
| **G-03: Strict Ownership Isolation** | 100% of `PUT`, `PATCH /status`, and `DELETE` attempts by a signed-in user on another user's report return HTTP `403 Forbidden`. |
| **G-04: Short-Lived Revocable Sessions** | Access tokens expire in 15 minutes (stored in JS memory only); 7-day refresh tokens rotate on every refresh, and replaying an old token revokes the entire token family (HTTP `401`). |
| **G-05: Immediate Ban Enforcement** | Banning a student revokes all active `refresh_sessions` immediately, and the banned user's next authenticated API request fails with HTTP `403 Forbidden`. |
| **G-06: Zero Plaintext Credentials** | 100% of user passwords are combined with `PASSWORD_PEPPER` (HMAC-SHA256) and hashed with Argon2id before database storage. |

### A4. Scope and Non-Goals
* **In Scope:** JWT authentication (register, login, 15-min memory access tokens, 7-day `HttpOnly` refresh cookie rotation, logout), Argon2id + pepper password hashing, RBAC (Visitor, User, Admin) with per-item ownership, self-service profile & password management, Admin Dashboard (overview metrics, student search/filter, ban/unban with session revocation), authentication attempt audit logging (`login_attempts`), full Lost & Found report CRUD with image uploads ($\le 2\text{ MB}$), and Vercel deployment.
* **Out of Scope (Non-Goals):** Official IUB Microsoft Entra ID / SSO integration (no access to institutional identity servers), multi-tenant group/club workspaces (not needed for a unified campus board), live WebSocket messaging (phone/WhatsApp reveal suffices), and external S3 bucket storage (Base64 data URLs with `/api/items/{id}/image` streaming meet MVP/final scale).
* **Assumptions & Constraints:** Modern desktop/mobile browsers with cookies enabled (`credentials: 'include'`); managed PostgreSQL configured via `DATABASE_URL` in production on Vercel; `JWT_SECRET_KEY` and `PASSWORD_PEPPER` $\ge 32$ characters stored in environment variables.

### A5. User Stories

| Table 4: User Stories | Role | User Story |
| :--- | :--- | :--- |
| **US-01** | Visitor | As a Visitor, I want to register with my Student ID, full name, email, and a strong password so that I can create an authenticated account. |
| **US-02** | User | As a User, I want to log in and have my short-lived access token silently refreshed via an `HttpOnly` cookie so that my session stays secure without frequent re-logins. |
| **US-03** | User | As a User, I want to change my password and invalidate all active refresh sessions so that stolen sessions on other devices are logged out. |
| **US-04** | Visitor | As a Visitor, I want to search and filter lost/found reports without logging in while private contact info remains hidden so that I can check if my item was found safely. |
| **US-05** | User | As a User, I want to view reporter phone/WhatsApp contact details only after signing in so that student contact numbers are protected from public scraping. |
| **US-06** | User | As a User, I want to edit, mark resolved/reopened, and delete only my own reports so that no other student can tamper with my listings. |
| **US-07** | User | As a User, I want to update my own contact profile while being blocked from changing my role or email so that privilege escalation via over-posting is prevented. |
| **US-08** | Admin | As an Admin, I want to view system-wide student and report overview counts so that I can monitor platform adoption and open cases. |
| **US-09** | Admin | As an Admin, I want to search students by ID, name, or email and filter by active/banned status so that I can quickly locate accounts under review. |
| **US-10** | Admin | As an Admin, I want to ban a misbehaving student with a documented reason—and unban them after review—while being prevented from banning myself or another admin. |

---

## Part B. Software Requirements (SRS)

### B1. Introduction
This Software Requirements Specification (SRS) defines the exact functional, non-functional, access-control, and verification requirements for **IUB Lost & Found (FindIt)** v2.0. It serves as the authoritative contract for the CSE309 course instructor (**Sayef Reyadh**), evaluators, and developers maintaining the system.

| Term | Definition |
| :--- | :--- |
| **JWT** | JSON Web Token (RFC 7519) signed with `HS256` carrying `sub`, `role`, `token_type`, `iss`, `aud`, `iat`, `exp`, and `jti` claims. |
| **Access Token** | Short-lived JWT (15-minute lifetime) stored strictly in frontend JavaScript memory (`accessToken`), never in `localStorage`. |
| **Refresh Token** | 48-byte cryptographically random opaque token stored as a SHA-256 hash in `refresh_sessions` and delivered via an `HttpOnly` cookie (`iub_refresh_token`, 7 days). |
| **RBAC** | Role-Based Access Control enforcing persisted `Student.role` (`user` or `admin`) and per-record ownership (`Item.owner_id`) on every protected API endpoint. |
| **Role** | Privilege level assigned to a `Student` account (`user` or `admin`); unauthenticated callers operate as `Visitor`. |
| **Permission** | Explicit operation allowed on a resource based on role and record ownership (e.g., owner-only report edit/delete, admin-only ban/unban). |
| **Audit Log** | Persistent `login_attempts` table recording every authentication event with identifier, client IP address, user-agent, outcome, and failure reason. |

**References:** RFC 7519 (JSON Web Token), OWASP ASVS v4.0 (Authentication & Session Management), FastAPI & SQLAlchemy 2.0 Documentation.

### B2. Functional Requirements

#### Table 5: Authentication & Session Management (`FR-AUTH`)
| ID | Requirement Statement |
| :--- | :--- |
| **FR-AUTH-01** | The system shall allow a visitor to register via `POST /api/auth/register` with unique `student_id`, `full_name`, unique lowercase `email`, password (`12–128` chars), and optional contact info, assigning `role='user'`. |
| **FR-AUTH-02** | The system shall combine every password with `PASSWORD_PEPPER` using HMAC-SHA256 and hash it using Argon2id (`pwdlib`) before persisting `password_hash`. |
| **FR-AUTH-03** | The system shall authenticate credentials via `POST /api/auth/login` and return a generic `401 Unauthorized` error (`'Email or password is incorrect.'`) for both unknown emails and wrong passwords. |
| **FR-AUTH-04** | The system shall issue `HS256` JWT access tokens valid for 15 minutes (`ACCESS_TOKEN_MINUTES = 15`) containing `sub`, `role`, `token_type='access'`, `iss`, `aud`, `iat`, `exp`, and `jti`. |
| **FR-AUTH-05** | The system shall store SHA-256 hashes of 7-day refresh tokens in `refresh_sessions` with a `family_id` and deliver raw tokens via an `HttpOnly`, `SameSite=Lax` cookie scoped to `/api/auth`. |
| **FR-AUTH-06** | The system shall rotate refresh tokens on `POST /api/auth/refresh` and immediately revoke the entire `family_id` (returning `401`) if a previously revoked token is reused. |
| **FR-AUTH-07** | The system shall revoke the active refresh session family and delete the `iub_refresh_token` cookie on `POST /api/auth/logout`, returning HTTP `204 No Content`. |
| **FR-AUTH-08** | The system shall allow authenticated users to view (`GET /api/auth/profile`) and update (`PATCH /api/auth/profile`) only their own `full_name`, `phone_number`, `whatsapp_number`, and `extra_contact_info`. |
| **FR-AUTH-09** | The system shall allow password updates via `POST /api/auth/change-password` after verifying `current_password`, revoking all active `refresh_sessions` for that user. |
| **FR-AUTH-10** | The system shall record every authentication attempt (`identifier`, `ip_address`, `user_agent`, `successful`, `failure_reason`) in the `login_attempts` table. |

#### Table 6: Role-Based Access Control (`FR-RBAC`)
| ID | Requirement Statement |
| :--- | :--- |
| **FR-RBAC-01** | The system shall enforce Visitor, User (`user`), and Admin (`admin`) roles on the server via centralized FastAPI dependencies (`get_jwt_current_user` and `require_roles`). |
| **FR-RBAC-02** | The system shall verify on every protected request that the JWT signature is valid, unexpired, the user exists, `is_banned` is `False`, and token role matches `Student.role`. |
| **FR-RBAC-03** | The system shall restrict report updates (`PUT`), status toggles (`PATCH /status`), and deletions (`DELETE`) to the report owner (`item.owner_id == current_user.id`), returning HTTP `403 Forbidden` otherwise. |
| **FR-RBAC-04** | The system shall omit private `contact_info` (returning `null`) on public item endpoints and require a valid JWT on `GET /api/items/{id}/contact` (returning HTTP `401` to guests). |
| **FR-RBAC-05** | The system shall reject any authenticated request from a banned user (`is_banned == True`) with HTTP `403 Forbidden` (`'This account has been suspended.'`) on their next request. |
| **FR-RBAC-06** | The system shall prevent an admin from banning their own account (HTTP `400 Bad Request`) or banning/unbanning another admin account (HTTP `403 Forbidden`). |

#### Table 7: Admin Dashboard (`FR-ADM`)
| ID | Requirement Statement |
| :--- | :--- |
| **FR-ADM-01** | The system shall provide `GET /api/admin/overview` (restricted to `admin`) returning `total_students`, `active_students`, `banned_students`, `admin_count`, `total_reports`, `open_reports`, and `resolved_reports`. |
| **FR-ADM-02** | The system shall provide `GET /api/admin/students` (restricted to `admin`) supporting keyword search (`q` across `student_id`, `full_name`, `email`), status filter (`all`, `active`, `banned`), and `limit`/`offset` pagination. |
| **FR-ADM-03** | The system shall allow an admin to ban a non-admin student via `PATCH /api/admin/students/{id}/ban` with a reason (`3–255` chars), immediately revoking all active `refresh_sessions`. |
| **FR-ADM-04** | The system shall allow an admin to unban a suspended student via `PATCH /api/admin/students/{id}/unban`, clearing `is_banned`, `banned_at`, and `banned_reason`. |

#### Table 8: Lost & Found Domain Features (`FR-DOMAIN`)
| ID | Requirement Statement |
| :--- | :--- |
| **FR-DOMAIN-01** | The system shall list up to 100 reports via `GET /api/items` ordered newest-first with filters for `status` (`open`/`resolved`/`all`), `category` (8 categories), `report_type` (`lost`/`found`), and keyword search (`q`). |
| **FR-DOMAIN-02** | The system shall allow authenticated users to create reports via `POST /api/items` with validated fields and optional JPG/PNG/WebP Base64 image data ($\le 2\text{ MB}$). |
| **FR-DOMAIN-03** | The system shall allow report owners to update all report fields (`PUT /api/items/{id}`), toggle `open`/`resolved` status (`PATCH /api/items/{id}/status`), and delete reports (`DELETE /api/items/{id}`). |
| **FR-DOMAIN-04** | The system shall serve stored report images via `GET /api/items/{id}/image` with `Cache-Control` headers, returning HTTP `404` when no photo is attached. |
| **FR-DOMAIN-05** | The system shall return aggregate report metrics (`total_reports`, `open_reports`, `resolved_reports`, `lost_reports`, `found_reports`) via `GET /api/stats`. |

### B3. Non-Functional Requirements

| Table 9: Non-Functional Requirements | Category | Measurable Requirement |
| :--- | :--- | :--- |
| **NFR-01** | Security (Secrets) | `JWT_SECRET_KEY` and `PASSWORD_PEPPER` shall be loaded from environment variables, validated to be $\ge 32$ characters, and never committed to Git. |
| **NFR-02** | Security (XSS/CSRF) | Access tokens shall reside in JS memory only (never `localStorage`); refresh tokens shall use `HttpOnly`, `SameSite=Lax` cookies scoped to `/api/auth`. |
| **NFR-03** | Performance | List endpoints shall enforce pagination/caps (`limit <= 100`) and database indexes on `status`, `category`, `report_type`, `owner_id`, `role`, and `is_banned` (target $< 500\text{ ms}$ API response). |
| **NFR-04** | Usability | The React UI shall adapt across mobile and desktop viewports with loading spinners, empty states, toasts, and clear error feedback. |
| **NFR-05** | Reliability | All records and sessions shall persist across server restarts via SQLAlchemy ORM backed by SQLite locally or managed PostgreSQL on Vercel. |
| **NFR-06** | Maintainability | Authorization logic shall reside in a single RBAC module (`backend/app/dependencies.py`) verified by automated `pytest` integration suites. |

### B4. Roles and Permission Matrix

| Table 10: Endpoint Permissions | Visitor | User (`user`) | Admin (`admin`) |
| :--- | :---: | :---: | :---: |
| `GET /api/health`, `GET /api/stats` | Yes | Yes | Yes |
| `GET /api/items`, `GET /api/items/{id}`, `GET /api/items/{id}/image` | Yes *(no contact)* | Yes *(own contact)* | Yes *(own contact)* |
| `POST /api/auth/register`, `/login`, `/refresh`, `/logout` | Yes | Yes | Yes |
| `GET /api/auth/me`, `GET/PATCH /api/auth/profile`, `POST /change-password` | No (`401`) | Yes *(Own)* | Yes *(Own)* |
| `POST /api/items`, `GET /api/items/{id}/contact` | No (`401`) | Yes | Yes |
| `PUT /api/items/{id}`, `PATCH /api/items/{id}/status`, `DELETE /api/items/{id}` | No (`401`) | Own (`403` others) | Own (`403` others) |
| `GET /api/admin/overview`, `GET /api/admin/students` | No (`401`) | No (`403`) | Yes |
| `PATCH /api/admin/students/{id}/ban`, `PATCH /api/admin/students/{id}/unban` | No (`401`) | No (`403`) | Yes *(non-admin targets)* |

| Table 11: Record-Level Ownership | Ownership & Permission Rule |
| :--- | :--- |
| **Create Report (`POST /api/items`)** | Any authenticated user or admin creates a report bound to `owner_id = current_user.id`. |
| **Read Contact Details (`GET /api/items/{id}/contact`)** | Any authenticated user or admin can view reporter phone, WhatsApp, and contact instructions. |
| **Update / Resolve / Delete Report** | Restricted strictly to `item.owner_id == current_user.id` (Owner-only). Non-owners receive HTTP `403`. |

| Table 12: Administrative Governance | Enforced Behaviour |
| :--- | :--- |
| **Self-Ban Prohibition** | An admin cannot ban their own account (`PATCH /api/admin/students/{self}/ban` returns HTTP `400`). |
| **Admin-to-Admin Protection** | An admin cannot ban or unban another admin account (returns HTTP `403 Forbidden`). |
| **Role Escalation Prevention** | No HTTP endpoint allows changing `Student.role`; admin promotion requires server-side CLI `bootstrap_admin.py`. |

### B5. Use Cases

| Table 13: Use Case Specifications | Actor | Preconditions | Main Flow | Error Flows | Postconditions |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UC-01: Log In & Refresh Token** | User | User has registered account. | 1. Submit email & password to `POST /api/auth/login`.<br>2. Verify Argon2id+pepper hash, log attempt, issue 15-min JWT & 7-day `HttpOnly` refresh cookie.<br>3. On `401` expiry, frontend calls `POST /api/auth/refresh` to rotate tokens. | `401` if wrong password or reused refresh token; `403` if account is banned. | User holds valid in-memory JWT and rotated refresh cookie. |
| **UC-02: Create Lost/Found Report** | User | User is authenticated with valid JWT. | 1. Fill title, description, category, type, location, contact instructions, and optional image.<br>2. Send `POST /api/items` with Bearer token.<br>3. Validate schema and save `Item` with `owner_id`. | `401` if unauthenticated; `403` if banned; `422` if invalid image or missing fields. | New report appears on the public board with `status='open'`. |
| **UC-03: Denied Non-Owner Edit** | User | User B is logged in; Item #5 belongs to User A. | 1. User B sends `PUT /api/items/5` or `DELETE /api/items/5`.<br>2. Server checks `item.owner_id == current_user.id`.<br>3. Check fails and server rejects request. | `403 Forbidden` (`'You can only edit your own reports.'`); `404` if item does not exist. | Item #5 remains unmodified in the database. |
| **UC-04: View Reporter Contact** | User | User is signed in and viewing an open report. | 1. Click `'View Contact Info'` on a report card.<br>2. Call `GET /api/items/{id}/contact` with Bearer JWT.<br>3. Return reporter phone, WhatsApp, and instructions. | `401 Unauthorized` if Visitor attempts access; `404` if item not found. | Contact modal displays phone/WhatsApp safely. |
| **UC-05: Ban Student Account** | Admin | Admin is logged in; target is a non-admin student. | 1. Open Admin Dashboard -> Students, click Ban, and enter a reason.<br>2. Call `PATCH /api/admin/students/{id}/ban`.<br>3. Set `is_banned=True` and revoke all `refresh_sessions`. | `400` if self-ban; `403` if target is admin or caller is non-admin; `409` if already banned. | Target student is suspended and blocked on next request (`403`). |
| **UC-06: Change Password & Revoke** | User | User is logged in. | 1. Submit current and new password to `POST /api/auth/change-password`.<br>2. Verify current password, update hash, revoke all `refresh_sessions`, and clear cookie. | `400` if current password is wrong or new password matches old; `422` if weak. | All active sessions across devices are invalidated. |

### B6. Acceptance Criteria

| Table 14: Acceptance Criteria | Scenario | Given | When | Then |
| :--- | :--- | :--- | :--- | :--- |
| **AC-01** | Token Expiry | User holds an expired JWT access token. | User calls `GET /api/auth/me`. | Server returns `401 Unauthorized`; frontend refreshes once via `POST /api/auth/refresh`. |
| **AC-02** | Tampered Token | Client alters `role='admin'` inside JWT payload. | Client sends tampered Bearer token. | `decode_access_token()` fails `HS256` signature verification and returns `401 Unauthorized`. |
| **AC-03** | Privacy Isolation | Guest visitor browses public board. | Guest calls `GET /api/items` or `GET /api/items/1/contact`. | `GET /api/items` sets `contact_info=null`; `/contact` returns `401 Unauthorized`. |
| **AC-04** | Ownership Guard | Student A owns report #5. | Student B calls `PUT` or `DELETE /api/items/5`. | Server checks `item.owner_id != current_user.id` and returns `403 Forbidden`. |
| **AC-05** | Role Guard | Regular student (`role='user'`) is signed in. | Student calls `GET /api/admin/overview`. | `require_roles('admin')` rejects request with `403 Forbidden`. |
| **AC-06** | Banned User | Admin bans Student A. | Student A sends next authenticated API request. | `get_jwt_current_user` detects `is_banned == True` and returns `403 Forbidden`. |
| **AC-07** | Admin Protection | Admin A is signed in. | Admin A attempts to ban self or Admin B. | Server returns `400` (self) or `403` (Admin B); neither admin is banned. |

### B7. Traceability Matrix

| Table 15: Traceability Matrix | Endpoint / Screen | Automated / Live Test | Screenshot |
| :--- | :--- | :--- | :---: |
| **FR-AUTH-01, 02** | `POST /api/auth/register`, Signup Modal | `test_signup_login_me_refresh_and_logout` | `S1` |
| **FR-AUTH-03, 04, 10** | `POST /api/auth/login`, `login_attempts` table | `test_signup_login_me_refresh_and_logout` | `S1`, `S7` |
| **FR-AUTH-05, 06, 07** | `POST /api/auth/refresh`, `POST /api/auth/logout` | `test_signup_login_me_refresh_and_logout` | `S8` |
| **FR-AUTH-08, 09** | `GET/PATCH /api/auth/profile`, `POST /change-password` | `test_profile_update_and_overposting_protection`, `test_change_password_revokes_existing_refresh_sessions` | `S3`, `S4` |
| **FR-RBAC-01, 02, 03, 04** | `dependencies.py`, `PUT/PATCH/DELETE /api/items/{id}`, `/contact` | `test_item_crud_ownership_and_contact_privacy` | `S2`, `S5`, `S6` |
| **FR-RBAC-05, 06** | `get_jwt_current_user`, `PATCH /api/admin/students/{id}/ban` | Manual & live verification on deployed API | `S9`, `S13` |
| **FR-ADM-01, 02, 03, 04** | `GET /api/admin/overview`, `/students`, `PATCH /ban`, `/unban` | Manual & live verification on Admin Dashboard | `S10`–`S17` |
| **FR-DOMAIN-01 to 05** | `GET/POST /api/items`, `/image`, `GET /api/stats` | `test_health_and_public_board`, `test_item_crud_ownership_and_contact_privacy` | `S2`, `S18`–`S21` |

---

## Part C. Technical Design (TDD)

### C1. Technology Stack

| Table 16: Technology Stack | Technology | Version | Reason for Choosing |
| :--- | :--- | :--- | :--- |
| **Frontend Framework** | React + TypeScript | `18.3.1` / `5.7.2` | Component-based SPA with compile-time static typing. |
| **Build Tool & Icons** | Vite + Lucide React | `6.0.1` / `0.468.0` | Fast HMR dev server, optimized production bundle, clean icons. |
| **Backend Framework** | FastAPI + Uvicorn | $\ge 0.115$ / $\ge 0.30$ | Async-capable Python REST API with automatic OpenAPI `/docs`. |
| **Validation** | Pydantic v2 | $\ge 2.8$ | Strict schema validation and `extra='forbid'` over-posting defense. |
| **Database & ORM** | PostgreSQL / SQLite + SQLAlchemy + Alembic | $\ge 2.0$ / $\ge 1.14$ | Relational ORM with migration support across local SQLite and hosted Postgres. |
| **Password Hashing** | `pwdlib` (Argon2id) + HMAC-SHA256 | $\ge 0.2.1$ | Memory-hard Argon2id hashing combined with server-side `PASSWORD_PEPPER`. |
| **JWT Library** | PyJWT | $\ge 2.10$ | RFC 7519 `HS256` JWT signing and claim verification. |
| **Automated Testing** | `pytest` + `httpx` (`TestClient`) | $\ge 8.0$ / $\ge 0.27$ | Full-stack HTTP integration tests against isolated database sessions. |
| **Deployment & Hosting** | Vercel (Multi-Service Routing) | Production | Unified domain serving Vite static frontend and containerized FastAPI API. |

### C2. System Architecture

```text
+-------------------------------------------------------------------------+
|  User Browser (React 18 + TypeScript SPA)                               |
|  - Memory: 15-min JWT accessToken   - Cookie: HttpOnly iub_refresh_token|
+------------------------------------+------------------------------------+
                                     | (1) HTTPS Request + Bearer JWT + Cookie
                                     v
+-------------------------------------------------------------------------+
|  Vercel Edge Network & Rewrites (vercel.json)                           |
+-------------------+---------------------------------+-------------------+
                    | (2) /* (SPA Routes)             | (3) /api/* & /docs
                    v                                 v
  +-----------------------------------+   +-------------------------------+
  | Vercel Frontend Static Bundle     |   | Vercel FastAPI Container      |
  | (frontend/dist)                   |   | (backend/app/main.py)         |
  +-----------------------------------+   +---------------+---------------+
                                                          |
                     +------------------------------------+----------------+
                     | (4) SQLAlchemy ORM Queries         | (5) Audit Write|
                     v                                    v                |
  +-----------------------------------+   +-------------------------------+
  | Relational Database               |   | Security Audit Log Table      |
  | (students, items, refresh_sessions|   | (login_attempts)              |
  +-----------------------------------+   +-------------------------------+
```
*Figure 1: System architecture showing browser token storage, Vercel edge routing, FastAPI backend, relational database, and audit log.*

* **Arrow (1) Browser $\to$ Vercel Edge:** The React client sends HTTPS requests carrying the in-memory JWT in `Authorization: Bearer <token>` and automatically attaches the `HttpOnly` refresh cookie via `credentials: 'include'`. Vercel's edge terminates TLS and inspects the request path.
* **Arrow (2) Vercel Edge $\to$ Frontend Bundle:** Non-API routes (`/*`) serve the compiled Vite React bundle (`frontend/dist`), rendering the campus board, user profile, or admin views. Client-side state restores the session silently on page load via `/api/auth/refresh`.
* **Arrow (3) Vercel Edge $\to$ FastAPI Container:** Requests matching `/api/*` or `/docs` are routed to the containerized FastAPI service (`backend/Dockerfile.vercel`). FastAPI validates Pydantic schemas, verifies JWTs, and enforces RBAC dependencies.
* **Arrow (4) FastAPI $\to$ Relational Database:** FastAPI executes parameterized SQLAlchemy ORM queries against PostgreSQL (or local SQLite) to read/write `students`, `items`, and `refresh_sessions`. All session hashes and ownership checks are resolved against live rows.
* **Arrow (5) FastAPI $\to$ Audit Log Table:** On every login or registration attempt, FastAPI persists an audit record in `login_attempts` capturing the identifier, IP address, user-agent, outcome, and failure reason. This provides a persistent security trail for failed login monitoring.

### C3. Backend and Frontend Structure

```text
backend/                                  frontend/
├── app/                                  ├── src/
│   ├── routers/                          │   ├── App.tsx          (SPA views, modals, admin UI)
│   │   ├── auth.py     (/api/auth/*)     │   ├── api.ts           (In-memory JWT & refresh)
│   │   └── admin.py    (/api/admin/*)    │   ├── main.tsx         (React root mount)
│   ├── database.py     (Engine/Session)  │   ├── styles.css       (Responsive styling)
│   ├── dependencies.py (JWT & RBAC)      │   └── types.ts         (TypeScript interfaces)
│   ├── main.py         (Items/Stats API) ├── index.html
│   ├── models.py       (SQLAlchemy ORM)  ├── package.json
│   ├── schemas.py      (Pydantic v2)     └── vite.config.ts
│   └── security.py     (Argon2id & JWT)
├── migrations/         (Alembic)
├── scripts/            (bootstrap_admin.py)
├── tests/              (pytest suites)
└── Dockerfile.vercel
```

Backend modules separate routes (`main.py`, `routers/auth.py`, `routers/admin.py`), data models (`models.py`), request schemas (`schemas.py`), cryptographic helpers (`security.py`), and centralized RBAC guards (`dependencies.py`). Frontend modules separate API communication and single-flight refresh locking (`api.ts`), shared TypeScript contracts (`types.ts`), and responsive UI components (`App.tsx`).

### C4. Data Model

```text
STUDENTS (1) ----< (N) ITEMS             STUDENTS (1) ----< (N) REFRESH_SESSIONS
  id (PK)                                  id (PK)
  student_id (UK, IX)                      token_hash (UK, IX, SHA-256)
  full_name                                student_pk (FK -> students.id)
  email (UK, IX)                           family_id (IX)
  password_hash (Argon2id)                 expires_at (IX), created_at
  role ('user' | 'admin', IX)              revoked_at, replaced_by_token_hash
  is_banned (IX), banned_at, banned_reason ip_address, user_agent
  phone_number, whatsapp_number
  extra_contact_info, last_login_at      LOGIN_ATTEMPTS (Standalone Audit Log)
  password_changed_at, created_at          id (PK), identifier (IX), ip_address (IX)
                                           user_agent, successful, failure_reason, attempted_at (IX)
```
*Figure 2: Entity-Relationship (ER) diagram of persisted tables and foreign-key relationships.*

| Table 17: Relational Database Tables | Columns, Keys & Constraints | Indexes |
| :--- | :--- | :--- |
| **`students`** | `id` (PK), `student_id` (UK), `full_name`, `email` (UK), `password_hash`, `role` (`'user'\|'admin'`), `is_banned`, `banned_at`, `banned_reason`, `phone_number`, `whatsapp_number`, `extra_contact_info`, `last_login_at`, `password_changed_at`, `created_at` | Indexes on `student_id`, `email`, `role`, `is_banned`. |
| **`items`** | `id` (PK), `title`, `description`, `category`, `report_type` (`'lost'\|'found'`), `location`, `incident_date`, `contact_info`, `image_data`, `status` (`'open'\|'resolved'`), `owner_id` (FK $\to$ `students.id` `ON DELETE CASCADE`), `created_at` | Indexes on `title`, `category`, `report_type`, `location`, `status`, `owner_id`, `created_at` + composite `(status, created_at)`. |
| **`refresh_sessions`** | `id` (PK), `token_hash` (UK, SHA-256), `student_pk` (FK $\to$ `students.id` `ON DELETE CASCADE`), `family_id`, `expires_at`, `created_at`, `revoked_at`, `replaced_by_token_hash`, `ip_address`, `user_agent` | Indexes on `token_hash`, `student_pk`, `family_id`, `expires_at`. |
| **`login_attempts`** | `id` (PK), `identifier`, `ip_address`, `user_agent`, `successful` (Boolean), `failure_reason`, `attempted_at` | Indexes on `identifier`, `ip_address`, `attempted_at`. |

### C5. API Design
All endpoints live under `/api` and return structured JSON errors via FastAPI's `{"detail": "..."}` schema.

| Table 18: REST API Specification | Auth | Role / Permission | Request | Success | Errors |
| :--- | :--- | :--- | :--- | :---: | :---: |
| `GET /api/health` | None | Public | None | `200` | `500` |
| `GET /api/stats` | None | Public | None | `200` | `500` |
| `GET /api/items` | Optional JWT | Public (no contact) | Query: `q`, `category`, `report_type`, `status` | `200` | `422` |
| `GET /api/items/{id}` | Optional JWT | Public (owner contact) | Path: `id` | `200` | `404` |
| `GET /api/items/{id}/image` | None | Public | Path: `id` | `200` | `404`, `500` |
| `GET /api/items/{id}/contact` | Bearer JWT | `user` or `admin` | Path: `id` | `200` | `401`, `403`, `404` |
| `POST /api/items` | Bearer JWT | `user` or `admin` | `ItemCreate` JSON | `201` | `401`, `403`, `422` |
| `PUT /api/items/{id}` | Bearer JWT | Owner only | `ItemUpdate` JSON | `200` | `401`, `403`, `404`, `422` |
| `PATCH /api/items/{id}/status` | Bearer JWT | Owner only | `{"status": "open \| resolved"}` | `200` | `401`, `403`, `404`, `422` |
| `DELETE /api/items/{id}` | Bearer JWT | Owner only | Path: `id` | `204` | `401`, `403`, `404` |
| `POST /api/auth/register` | None | Public | `SignupRequest` JSON | `201` | `409`, `422` |
| `POST /api/auth/login` | None | Public | `PasswordLoginRequest` JSON | `200` | `401`, `403`, `422` |
| `POST /api/auth/refresh` | `HttpOnly` Cookie | Valid refresh session | Cookie: `iub_refresh_token` | `200` | `401`, `403` |
| `POST /api/auth/logout` | `HttpOnly` Cookie | Any | Cookie: `iub_refresh_token` | `204` | — |
| `GET /api/auth/me` | Bearer JWT | `user` or `admin` | None | `200` | `401`, `403` |
| `GET / PATCH /api/auth/profile` | Bearer JWT | Self | `ProfileUpdateRequest` JSON | `200` | `401`, `403`, `422` |
| `POST /api/auth/change-password` | Bearer JWT | Self | `PasswordChangeRequest` JSON | `204` | `400`, `401`, `403`, `422` |
| `GET /api/admin/overview` | Bearer JWT | `admin` only | None | `200` | `401`, `403` |
| `GET /api/admin/students` | Bearer JWT | `admin` only | Query: `q`, `status`, `limit`, `offset` | `200` | `401`, `403`, `422` |
| `PATCH /api/admin/students/{id}/ban` | Bearer JWT | `admin` (non-admin target) | `AdminBanRequest` JSON | `200` | `400`, `401`, `403`, `404`, `409` |
| `PATCH /api/admin/students/{id}/unban` | Bearer JWT | `admin` (non-admin target) | Path: `id` | `200` | `401`, `403`, `404`, `409` |

### C6. JWT Authentication Design

```text
Browser                        FastAPI (/api/auth & /api/items)             Database
  |--- POST /api/auth/login -------->|                                          |
  |                                  |--- Verify Argon2id+Pepper & Log -------->|
  |<-- 200 {access_token} + Cookie --|--- Insert refresh_sessions (SHA-256) --->|
  |--- GET /api/items/1/contact ---->| (Authorization: Bearer <access_token>)   |
  |<-- 200 Contact Details ----------|--- Verify sig, exp, user, !is_banned --->|
  |--- GET /api/auth/me (expired) -->|                                          |
  |<-- 401 Token Expired ------------|                                          |
  |--- POST /api/auth/refresh ------>| (HttpOnly cookie: iub_refresh_token)     |
  |                                  |--- Rotate hash; revoke family if reused->|
  |<-- 200 {new_token} + New Cookie -|                                          |
  |--- POST /api/auth/logout ------->|--- Revoke family & clear cookie (204) --->|
```
*Figure 3: JWT login, protected request, expiry, single-flight refresh rotation, reuse detection, and logout flow.*

| JWT Claim | Purpose & Validation |
| :--- | :--- |
| **`sub`** | Stringified `Student.id` primary key identifying the authenticated user. |
| **`role`** | User's persisted role (`'user'` or `'admin'`), cross-checked against live DB on every request. |
| **`token_type`** | Fixed string `'access'` preventing refresh tokens from being used as Bearer tokens. |
| **`iss` / `aud`** | Issuer (`'iub-lost-and-found'`) and Audience (`'iub-lost-and-found-api'`) verified on decode. |
| **`iat` / `exp`** | Issued-at timestamp and Expiration timestamp ($+15$ minutes, `ACCESS_TOKEN_MINUTES = 15`). |
| **`jti`** | Cryptographically random URL-safe token ID (16 bytes) ensuring unique token hashes. |

**Browser Storage & 401 Handling:** Access tokens are held exclusively in a module-scoped variable (`accessToken` in `frontend/src/api.ts`)—never in `localStorage`—protecting against XSS token theft. Refresh tokens (7-day lifetime) are stored in an `HttpOnly`, `SameSite=Lax` cookie scoped to `Path=/api/auth`, mitigating CSRF and XSS. On a `401` response, `apiFetch()` executes a single-flight refresh once and logs out if refresh fails.

### C7. RBAC Design
Every protected request traverses a strict linear pipeline in `backend/app/dependencies.py`: (1) Extract Bearer JWT $\to$ (2) Verify `HS256` signature, issuer, audience, and expiry $\to$ (3) Load `Student` by `sub` $\to$ (4) Reject if `is_banned == True` (`403`) $\to$ (5) Reject if token role $\neq$ DB role (`401`) $\to$ (6) Enforce `require_roles(...)` $\to$ (7) Enforce record ownership (`item.owner_id == current_user.id`).

```python
def require_roles(*allowed_roles: str) -> Callable[[Student], Student]:
    normalized_roles = tuple(role.strip().lower() for role in allowed_roles if role.strip())

    def _role_guard(current_user: Student = Depends(get_jwt_current_user)) -> Student:
        user_role = (current_user.role or '').strip().lower()
        if user_role not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You do not have permission to perform this action.',
            )
        return current_user

    return _role_guard
```

Adding a new role (e.g., `'moderator'`) requires adding it to `ALLOWED_USER_ROLES` in `models.py` and passing `require_roles('admin', 'moderator')` to the desired route dependencies.

### C8. Admin Dashboard Design

| Admin UI Section | Endpoint Called | Filters & Pagination | Actions & Side Effects |
| :--- | :--- | :--- | :--- |
| **Overview Cards** | `GET /api/admin/overview` | None (live system aggregates) | Displays Total Students, Active, Banned, Admins, Total Reports, Open, Resolved. |
| **Student Directory** | `GET /api/admin/students` | Keyword `q` (ID/name/email), `status` (`all`/`active`/`banned`), `limit`/`offset` | Paginated student table showing role badge, active/banned status, ban reason, and created timestamp. |
| **Ban / Unban Modal** | `PATCH /api/admin/students/{id}/ban` & `/unban` | Target student ID | Ban requires `3–255` char reason and revokes all `refresh_sessions`; Unban restores access immediately. |

### C9. Security Design and Threats

| Threat | Defence Implemented | File / Module |
| :--- | :--- | :--- |
| **Password Database Leak** | HMAC-SHA256 `PASSWORD_PEPPER` + Argon2id hashing (`pwdlib`). | `backend/app/security.py` |
| **Stolen Access Token (XSS)** | Stored in JS memory only (never `localStorage`) + 15-min TTL. | `frontend/src/api.ts` |
| **Stolen Refresh Token** | SHA-256 hash in DB, `HttpOnly` cookie, rotation & family revocation on reuse. | `backend/app/routers/auth.py` |
| **Brute-Force / Enumeration** | Generic `401` message + persistent `login_attempts` audit log (IP, user-agent). | `backend/app/routers/auth.py` |
| **Privilege Escalation** | Server-side `require_roles('admin')` + self-ban & admin-ban blocks. | `dependencies.py`, `admin.py` |
| **Unauthorized Record Edit** | Server-side owner check (`item.owner_id != current_user.id -> 403`). | `backend/app/main.py` |
| **CSRF** | `SameSite=Lax` cookie scoped to `/api/auth` + Bearer header on mutations. | `backend/app/routers/auth.py` |
| **CORS Misuse** | Explicit `CORS_ORIGINS` allowlist with `allow_credentials=True`. | `backend/app/main.py` |
| **Secrets in Repository** | Environment variables validated $\ge 32$ chars; `.env` excluded in `.gitignore`. | `security.py`, `.gitignore` |
| **SQL Injection** | 100% parameterized SQLAlchemy 2.0 ORM queries. | `main.py`, `auth.py`, `admin.py` |
| **Over-Posting / Mass Assign** | Pydantic `ConfigDict(extra='forbid')` rejecting unexpected JSON keys (`422`). | `backend/app/schemas.py` |

### C10. Deployment on Vercel
The application is deployed as a unified Vercel project via `vercel.json`, routing `/api/*`, `/docs`, `/openapi.json`, and `/redoc` to the containerized FastAPI service (`backend/Dockerfile.vercel`) and all other routes to the Vite React frontend (`frontend/dist`). Redeploying occurs automatically on `git push` to `main` or via Vercel Dashboard $\to$ Redeploy.

| Environment Variable | Purpose (Values Never Committed) |
| :--- | :--- |
| **`DATABASE_URL`** | PostgreSQL connection string (normalized to `postgresql+psycopg://`). |
| **`JWT_SECRET_KEY`** | 32+ character cryptographic secret used to sign `HS256` JWT access tokens. |
| **`PASSWORD_PEPPER`** | 32+ character secret mixed into passwords via HMAC-SHA256 before Argon2id hashing. |
| **`CORS_ORIGINS`** | Allowed frontend origin (`https://2330841-maishatul-findit.vercel.app`). |
| **`REFRESH_COOKIE_SECURE`** | Set to `true` in production so refresh cookies transmit strictly over HTTPS. |

### C11. Testing
Automated integration tests use `pytest` and FastAPI's `TestClient` with isolated database overrides. Run locally via: `cd backend && pytest -v`.

| Automated Test Name | Requirement Checked | Result |
| :--- | :--- | :---: |
| `test_health_and_public_board` | `FR-DOMAIN-01, 04, 05` | `PASSED` |
| `test_signup_login_me_refresh_and_logout` | `FR-AUTH-01 to 07, AC-01` | `PASSED` |
| `test_duplicate_signup_is_rejected` | `FR-AUTH-01` | `PASSED` |
| `test_profile_get_and_update_only_affect_current_user` | `FR-AUTH-08` | `PASSED` |
| `test_profile_update_rejects_overposting_fields` | `FR-RBAC-01, NFR-06` | `PASSED` |
| `test_change_password_revokes_existing_refresh_sessions` | `FR-AUTH-09` | `PASSED` |
| `test_item_crud_ownership_and_contact_privacy` | `FR-RBAC-03, 04, AC-03, 04` | `PASSED` |

---

## Part D. Evidence: Screenshots of the Running Application

*(Note: Full-resolution screenshots `S1` through `S21` captured on `https://2330841-maishatul-findit.vercel.app/` are embedded in the submitted PDF report `Maisha_2330841_CSE309_Final_Report_sec5.pdf`.)*

### D1. User Side
* **Screenshot S1:** Signup and Login Modal with Validation Error Shown (`FR-AUTH-01`, `FR-AUTH-03`)
* **Screenshot S2:** Main Lost & Found Board & Student Access Flow (`FR-DOMAIN-01`, `FR-DOMAIN-02`)
* **Screenshot S3:** Profile Page & Change Password Form Rejecting Wrong Current Password (`FR-AUTH-08`, `FR-AUTH-09`)
* **Screenshot S4:** Active Authenticated Session & Sign-In/Sign-Out Controls (`FR-AUTH-05`, `FR-AUTH-07`)
* **Screenshot S5:** Authenticated Board View & Report Ownership Controls (`FR-RBAC-03`, `FR-DOMAIN-03`)
* **Screenshot S6:** Campus Noticeboard & RBAC Access Enforcement (`FR-RBAC-01`, `FR-RBAC-03`)

### D2. Security Behaviour
* **Screenshot S7:** Account Settings & Student Profile View (`FR-AUTH-08`)
* **Screenshot S8:** Session & Security Validation Flow (`FR-AUTH-05`, `FR-AUTH-06`)
* **Screenshot S9:** Student Authentication & Access Enforcement (`FR-RBAC-05`)

### D3. Admin Dashboard
* **Screenshot S10:** Admin Dashboard Overview Statistics (`FR-ADM-01`)
* **Screenshot S11:** Admin Student Directory & Live Board Integration (`FR-ADM-02`)
* **Screenshot S12:** Admin Student Management with Search & Status Filter (`FR-ADM-02`, `FR-ADM-03`)
* **Screenshot S13:** Reporter Connection & Contact Reveal Modal (`FR-RBAC-04`)
* **Screenshot S14:** Student Sign-In & Role Access Verification (`FR-RBAC-06`)
* **Screenshot S15:** Admin Ban Student Dialog with Reason (`FR-ADM-03`, `FR-AUTH-10`)
* **Screenshot S16:** Admin Dashboard Resulting Banned State & Updated Metrics (`FR-ADM-03`, `FR-ADM-04`)
* **Screenshot S17:** New Report Submission Form (`Tell the campus community`) (`FR-DOMAIN-02`)

### D4. Deployment on Vercel
* **Screenshot S18:** Filtered Board Reports & Owner Edit Controls (`FR-DOMAIN-01`, `FR-RBAC-03`)
* **Screenshot S19:** Report Category Selection & Validation (`FR-DOMAIN-02`)
* **Screenshot S20:** Public Landing Page on Vercel (`https://2330841-maishatul-findit.vercel.app`) (`NFR-05`)

### D5. Automated Tests
* **Screenshot S21:** Live Student Sign-In Verification on Production URL (`NFR-06`)

---

## Part E. Project Management and Conclusion

### E1. How to Run and Test Locally

**Prerequisites:** Python 3.10+, Node.js 20+, npm, and Git.

```bash
# 1. Clone repository
git clone https://github.com/maishatuljikri/2330841-maishatul-FindIt-.git
cd 2330841-maishatul-FindIt-

# 2. Configure backend environment (backend/.env)
DATABASE_URL=sqlite:///./data/lost_found.db
JWT_SECRET_KEY=replace-with-a-32-character-minimum-random-secret-key
PASSWORD_PEPPER=replace-with-another-32-character-minimum-random-pepper
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
REFRESH_COOKIE_SECURE=false

# 3. Start Backend & Run Automated Tests
cd backend && pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload --port 8000

# 4. Start Frontend (in a second terminal)
cd frontend && npm install && npm run dev
```

**Logging In with Demo Accounts:** Both `admin` and `user` roles can be tested on the live Vercel site or locally. Demo account email addresses and passwords are provided exclusively in the Appendix of the submitted PDF report and are never stored in the GitHub repository.

### E2. GitHub Work

| Feature Milestone | Branch / PR | What It Delivered |
| :--- | :--- | :--- |
| **Issue / PR #1 — Core Lost & Found CRUD** | `feat/item-crud` | Implemented FastAPI `/api/items` CRUD, image upload validation, SQLAlchemy models, and React board UI. |
| **Issue / PR #2 — JWT Auth & Rotation** | `feat/jwt-auth` | Added `/api/auth/register`, `/login`, `/refresh`, `/logout`, Argon2id+pepper hashing, and `HttpOnly` refresh cookies. |
| **Issue / PR #3 — RBAC & Profile Security** | `feat/rbac-profile` | Implemented `dependencies.py` role guards, item ownership checks, profile updates, and password revocation. |
| **Issue / PR #4 — Admin Dashboard & Vercel** | `feat/admin-vercel` | Built `/api/admin/overview`, `/students`, `/ban`, `/unban`, Admin UI, and multi-service Vercel deployment. |

All commits, architecture design, backend routers, frontend components, tests, and documentation were authored by **Maishatul Jikri Oishi (2330841)** across the Midterm MVP and Final v2.0 milestones.

### E3. Limitations
* **No Institutional SSO:** Demo registration accepts student details directly rather than authenticating via official IUB Microsoft Entra ID SSO.
* **Database Image Storage:** Item photos are stored as Base64 data URLs in the relational database rather than dedicated object storage (such as AWS S3 or Cloudflare R2).
* **Audit Logging Without Auto-Lockout:** Failed login attempts are logged to `login_attempts` for audit visibility, but automated IP-based rate limiting / account lockout timers are not yet enforced.

### E4. Future Work
1. **Verified University SSO:** Integrate official IUB OAuth2 / OpenID Connect SSO so only verified university students can register.
2. **Rate Limiting & Brute-Force Lockout:** Add sliding-window rate limiting on `/api/auth/login` and `/api/auth/register` to block automated credential stuffing.
3. **Cloud Object Storage for Photos:** Migrate item photos from database Base64 columns to signed cloud object storage URLs for faster CDN delivery.
4. **In-App Audit Log Viewer & CSV Export:** Build an Admin Audit Log viewer and CSV export endpoint directly inside the Admin Dashboard UI.

### E5. Sources, Libraries, and Tools

| Library / Tool | Version / Link | Purpose |
| :--- | :--- | :--- |
| **FastAPI & Pydantic** | `0.115+` / `2.8+` | REST API framework, dependency injection, and schema validation. |
| **SQLAlchemy & Alembic** | `2.0+` / `1.14+` | Relational ORM and database schema migrations. |
| **PyJWT & `pwdlib` (Argon2)** | `2.10+` / `0.2.1+` | `HS256` JWT token signing/verification and Argon2id password hashing. |
| **React, TypeScript & Vite** | `18.3` / `5.7` / `6.0` | Frontend single-page application, type safety, and bundling. |
| **Vercel** | Production Cloud | Hosting and edge routing for frontend and FastAPI container. |
| **AI Assistance (Gemini)** | Documentation & Review | Used for structuring SRS/TDD tables and verifying security edge cases; all code and deployments were manually tested and verified. |

---

## Appendix. Test Accounts and Video Demo

* **Video Demonstration Link:** `https://www.youtube.com/watch?v=xsEJmKIr9PU`
* **Demo Test Accounts (`admin` and `user`):** Provided exclusively in the Appendix of the submitted PDF report and intentionally omitted from this GitHub Markdown file to prevent credential exposure.