# Software Requirements Specification (SRS)
## FindIt – Campus Lost and Found System

### 1. Purpose
Define functional and non-functional requirements for the FindIt campus lost-and-found web application.

### 2. User Roles
- **User (student or staff):** Sign in, browse, create and manage their own reports, and submit claims.
- **Admin:** View and moderate all reports and claims and resolve disputes.

### 3. Functional Requirements
- **FR-01:** The system shall register and authenticate users.
- **FR-02:** The system shall authorize access based on roles (User, Admin).
- **FR-03:** Authenticated users shall create LOST or FOUND reports with title, description, category, location, and date.
- **FR-04:** Users shall browse and search public reports; filters include status, category, and location.
- **FR-05:** Users shall view details for public reports.
- **FR-06:** Report owners shall edit or close their own reports.
- **FR-07:** Authenticated users shall submit private ownership claims for found-item reports.
- **FR-08:** Administrators shall view all claims and review or update their status.
- **FR-09:** Administrators shall hide inappropriate reports and mark items resolved.
- **FR-10:** The system shall validate required fields and provide meaningful errors.

### 4. Non-Functional Requirements
- **NFR-01 Security:** Passwords must be stored using secure password hashing; APIs must validate bearer tokens.
- **NFR-02 Authorization:** Protected endpoints enforce role and ownership permissions on the server.
- **NFR-03 Privacy:** Ownership evidence is visible only to authorized participants/admins, not public visitors.
- **NFR-04 Usability:** Responsive interface usable on mobile and desktop.
- **NFR-05 Reliability:** API errors produce meaningful HTTP responses; invalid input does not crash the server.
- **NFR-06 Maintainability:** Frontend and backend are modular and documented.

### 5. Data Requirements
- User: id, name, email, password_hash, role.
- ItemReport: id, owner_id, report_type, title, description, category, location, event_date, status, created_at.
- Claim: id, item_id, claimant_id, evidence, status, created_at.

### 6. Acceptance Tests
1. A user logs in and receives an access token.
2. A user creates and searches for a report.
3. A different user cannot edit the original report.
4. A user cannot reach an admin endpoint; an admin can.
5. A claim is not included in public report responses.
6. Closing a report updates its status.
