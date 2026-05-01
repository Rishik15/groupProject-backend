ADMIN_API_INTEGRATION_AND_TESTING_GUIDE.md

# Admin API Integration Guide
# test
## Base URL
http://localhost:8080/admin

## Authentication
All admin endpoints require a logged-in session.

### Login
curl -i -c cookies.txt \
  -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"liam@example.com","password":"Rishik@1"}'

Use -b cookies.txt for all subsequent requests.

---

# Data Contracts (Frontend Shapes)

## Applications
applications: {
  id: number
  name: string
  email: string
  appliedLabel: string
  certifications: string[]
  avatarInitial?: string
}

## Reports
reports: {
  id: number
  title: string
  description: string
  submittedLabel: string
  statusLabel?: string
}

---

# Endpoints

## 1. Dashboard Stats

GET /admin/dashboard/stats

Response:
{
  "message": "success",
  "stats": {
    "total_users": 50,
    "active_coaches": 12,
    "pending_reviews": 9,
    "pending_coach_applications": 5,
    "open_reports": 4,
    "monthly_revenue": 3200.0
  }
}

Notes:
- pending_reviews = pending_apps + open_reports
- monthly_revenue uses active contracts

---

## 2. Users (Admin View)

GET /admin/users

Response:
{
  "message": "success",
  "users": [
    {
      "user_id": 12,
      "name": "Liam Smith",
      "email": "liam@example.com",
      "username": "liam_12",
      "is_coach": true,
      "is_admin": true
    }
  ]
}

Notes:
- Full user dataset returned
- Includes role flags

---

## 3. Active Coaches

GET /admin/coaches/active

Response:
{
  "message": "success",
  "coaches": [
    {
      "user_id": 23,
      "name": "Alex Rivera",
      "email": "alex@example.com",
      "coach_description": "Strength & conditioning specialist",
      "price": 85.0,
      "contract_count": 6,
      "certifications": [
        {
          "cert_name": "CPT",
          "provider_name": "NASM"
        }
      ]
    }
  ]
}

Data Source:
- users_immutables
- user_mutables
- coach
- certifications
- user_coach_contract (count only)

---

## 4. Coach Applications

GET /admin/coach-applications?status=pending

Query Params:
- pending
- approved
- rejected

Response:
{
  "message": "success",
  "applications": [
    {
      "id": 11,
      "name": "Jordan Lee",
      "email": "jordan@example.com",
      "appliedLabel": "2026-04-18T05:00:00",
      "certifications": ["CPT", "Nutrition Coach"],
      "avatarInitial": "J"
    }
  ]
}

Notes:
- Certifications are flattened → string[]
- Additional fields exist but FE can ignore

---

## 5. Approve Coach Application

PATCH /admin/coach-applications/:id/approve

Body:
{
  "admin_action": "Strong candidate, approved"
}

Behavior:
- Sets application → approved
- Creates row in coach
- Copies certifications → certifications
- Sets:
  - reviewed_at
  - reviewed_by_admin_id

Response:
{
  "message": "Application approved"
}

---

## 6. Reject Coach Application

PATCH /admin/coach-applications/:id/reject

Body:
{
  "admin_action": "Insufficient experience"
}

Behavior:
- Sets application → rejected
- No coach row created
- Saves admin metadata

---

## 7. Reports (Moderation Queue)

GET /admin/reports?status=open

Returns:
- open
- reviewing

Response:
{
  "reports": [
    {
      "id": 4,
      "title": "Report against coach",
      "description": "Unprofessional behavior",
      "submittedLabel": "2026-04-17T12:00:00",
      "statusLabel": "open"
    }
  ]
}

---

GET /admin/reports?status=closed

Returns:
- resolved
- dismissed

---

## 8. Close Report

PATCH /admin/reports/:id/close

Body:
{
  "admin_action": "Resolved after investigation"
}

Behavior:
- status → resolved
- sets:
  - admin_action
  - resolved_by_admin_id
  - updated_at

Edge Case:
{
  "error": "Report is already closed"
}

---

# Backend Logic Summary

## Coach Application Flow
1. User submits → coach_application
2. Admin:
   - Approve:
     - create coach
     - insert certifications
   - Reject:
     - store metadata only

## Report Flow
1. Report created → open
2. Admin closes:
   - → resolved
   - tracked via admin_action

---

# Testing Guide

## 1. Login
curl -i -c cookies.txt \
  -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"liam@example.com","password":"Rishik@1"}'

---

## 2. Dashboard
curl -b cookies.txt http://localhost:8080/admin/dashboard/stats

---

## 3. Applications
curl -b cookies.txt \
"http://localhost:8080/admin/coach-applications?status=pending"

---

## 4. Approve Flow
curl -b cookies.txt \
  -X PATCH http://localhost:8080/admin/coach-applications/11/approve \
  -H "Content-Type: application/json" \
  -d '{"admin_action":"Approved for demo"}'

Verify:
curl -b cookies.txt http://localhost:8080/admin/coaches/active

---

## 5. Reject Flow
curl -b cookies.txt \
  -X PATCH http://localhost:8080/admin/coach-applications/12/reject \
  -H "Content-Type: application/json" \
  -d '{"admin_action":"Rejected"}'

---

## 6. Reports
curl -b cookies.txt \
"http://localhost:8080/admin/reports?status=open"

---

## 7. Close Report
curl -b cookies.txt \
  -X PATCH http://localhost:8080/admin/reports/4/close \
  -H "Content-Type: application/json" \
  -d '{"admin_action":"Handled"}'

---

## 8. DB Verification (optional)
SELECT * FROM coach;
SELECT * FROM certifications;
SELECT * FROM coach_application;
SELECT * FROM user_report;

---

# Final Notes

- All endpoints return { message, ...data }
- Dates are ISO strings
- FE handles label formatting
- No pagination implemented yet