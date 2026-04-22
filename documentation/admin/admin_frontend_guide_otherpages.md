UC 11.1, UC 11.2, UC 12.5, UC 12.6, UC 12.7, UC 12.8, UC 8.3, UC 5.3
# Admin Frontend Implementation Prompt

You are working on the React + Vite + TypeScript frontend for an existing Flask backend workout application.

Your job is to implement the **admin frontend only** for the finalized backend contract described below.

Follow this prompt strictly.

---

# Core Rules

## 1. All non-GET backend input must be sent in the JSON request body

Do **not** pass editable values, action data, filters, status values, ids for mutable actions, reasons, or form fields in the URL query string.

Use Flask-style JSON request bodies.

Good:
```ts
fetch("/admin/videos/reject", {
  method: "PATCH",
  credentials: "include",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    exercise_id: 12,
    video_review_note: "Demonstrates the wrong movement"
  })
})
```

Bad:
```ts
fetch("/admin/videos/12/reject?reason=wrong")
```

Bad:
```ts
fetch("/admin/users/17/suspend?reason=spam")
```

The backend expects JSON packages from the frontend.

---

## 2. Session auth is cookie-based

Always send requests with credentials included.

Use:
```ts
credentials: "include"
```

or the equivalent axios configuration.

---

## 3. The frontend must match the finalized backend contract exactly

Do not invent alternate endpoints.
Do not invent query-string-based mutation flows.
Do not invent path-param mutation routes.
Do not assume REST nesting that is not listed here.

---

## 4. Keep frontend code organized using this project structure

Use the existing frontend architecture style:

- `services`
- `utils`
- `interfaces`
- `components`
- `main wrapper pages`
- existing app architecture conventions

---

# Finalized Backend Architecture

The backend admin implementation is organized around these domains:

1. dashboard + analytics
2. users and account enforcement
3. active coaches listing
4. coach-application moderation
5. user-report moderation
6. exercise management
7. workout/template management
8. exercise video moderation
9. coach-price moderation

The backend architecture follows these rules:

- Flask blueprint: existing `admin_bp`
- thin route files under `app/routes/admin/...`
- business logic in `app/services/admin/...`
- raw SQL through `run_query(...)`
- admin access verified through database lookup, not session role alone
- JSON request and response bodies
- session-based auth
- media served from `/uploads/...`

---

# Finalized Schema Additions

The backend will add the following fields and table.

---

## 1. Exercise table additions

The `exercise` table will gain:

- `video_status ENUM('pending','approved','rejected') DEFAULT 'approved'`
- `video_review_note TEXT NULL`
- `video_reviewed_by INT NULL`

### Meaning

- `video_url` still stores the actual media URL
- `video_status` stores moderation state
- `video_review_note` stores admin review reason or note
- `video_reviewed_by` stores the admin id who reviewed it

---

## 2. Users table additions

The `users_immutables` table will gain:

- `account_status ENUM('active','suspended','deactivated') DEFAULT 'active'`
- `suspension_reason TEXT NULL`

### Meaning

- `account_status` is the master account state
- `suspension_reason` is stored when suspending or deactivating for policy reasons
- `updated_at` already exists and will reflect changes automatically
- there is **no separate suspended_until field**
- there is **no dedicated reactivate endpoint**

---

## 3. New coach price moderation table

The backend will add a minimal request table for coach price changes.

Expected shape:

```sql
coach_price_change_request
- request_id
- coach_id
- proposed_price
- status ENUM('pending','approved','rejected')
- admin_action
- reviewed_by_admin_id
- reviewed_at
- created_at
- updated_at
```

### Meaning

- coaches do not directly overwrite live `coach.price`
- proposed changes go into a review queue
- admin approves or rejects
- approved requests update the live `coach.price`

---

# Finalized Endpoint Contract

These are the final endpoints the frontend must use.

---

# 1. Dashboard + Analytics

## GET `/admin/dashboard/stats`

### Purpose
Fetch the main admin dashboard statistics.

### Request
No body.

### Response
```json
{
  "message": "success",
  "stats": {
    "total_users": 50,
    "active_coaches": 12,
    "pending_reviews": 8,
    "pending_coach_applications": 3,
    "open_reports": 5,
    "monthly_revenue": 2400.0
  }
}
```

---

## GET `/admin/analytics/engagement`

### Purpose
Fetch platform engagement analytics for admin dashboards.

### Request
No body.

### Response
```json
{
  "message": "success",
  "analytics": {
    "daily_active_users": 18,
    "weekly_active_users": 41,
    "monthly_active_users": 76
  }
}
```

### Notes
- this endpoint exists specifically to satisfy admin engagement analytics
- the frontend should display DAU, WAU, and MAU cards/charts

---

# 2. Users and Account Enforcement

## GET `/admin/users`

### Purpose
Fetch users/coaches/admins for admin review.

### Request
No body.

### Response
```json
{
  "message": "success",
  "users": [
    {
      "user_id": 17,
      "first_name": "Jane",
      "last_name": "Doe",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "phone_number": "555-555-5555",
      "is_coach": true,
      "is_admin": false,
      "account_status": "active",
      "suspension_reason": null,
      "updated_at": "2026-04-22T19:00:00"
    }
  ]
}
```

---

## PATCH `/admin/users/suspend`

### Purpose
Suspend a user or coach account.

### Request body
```json
{
  "user_id": 17,
  "suspension_reason": "Policy violation"
}
```

### Notes
- suspension reason is required
- backend updates:
  - `account_status = "suspended"`
  - `suspension_reason = ...`
  - `updated_at` automatically through existing schema behavior

### Response
```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "suspended",
    "suspension_reason": "Policy violation"
  }
}
```

---

## PATCH `/admin/users/deactivate`

### Purpose
Deactivate a user or coach account.

### Request body
```json
{
  "user_id": 17,
  "suspension_reason": "Repeated severe policy violations"
}
```

### Response
```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "deactivated",
    "suspension_reason": "Repeated severe policy violations"
  }
}
```

---

## PATCH `/admin/users/status`

### Purpose
Set the final desired account status directly.

### Request body
```json
{
  "user_id": 17,
  "account_status": "active",
  "suspension_reason": null
}
```

### Supported values
- `"active"`
- `"suspended"`
- `"deactivated"`

### Notes
- use this route to restore an account to active
- do not build or call a dedicated `/reactivate` endpoint

### Response
```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "active",
    "suspension_reason": null
  }
}
```

---

# 3. Active Coaches Listing

## GET `/admin/coaches/active`

### Purpose
Fetch active coaches and their profile/certification details.

### Request
No body.

### Response
```json
{
  "message": "success",
  "coaches": [
    {
      "user_id": 22,
      "first_name": "Chris",
      "last_name": "Smith",
      "name": "Chris Smith",
      "email": "chris@example.com",
      "coach_description": "Strength coach",
      "price": 80.0,
      "contract_count": 5,
      "certifications": [
        {
          "cert_name": "NASM CPT",
          "provider_name": "NASM",
          "description": null,
          "issued_date": "2025-01-01",
          "expires_date": "2027-01-01"
        }
      ]
    }
  ]
}
```

---

# 4. Coach Application Moderation

## POST `/admin/coach-applications/list`

### Purpose
Fetch coach applications by moderation status.

### Request body
```json
{
  "status": "pending"
}
```

### Supported values
- `"pending"`
- `"approved"`
- `"rejected"`

### Response
```json
{
  "message": "success",
  "applications": [
    {
      "id": 4,
      "application_id": 4,
      "user_id": 22,
      "name": "Chris Smith",
      "email": "chris@example.com",
      "appliedLabel": "2026-04-22T18:00:00",
      "status": "pending",
      "years_experience": 3,
      "coach_description": "Strength coach",
      "desired_price": 80.0,
      "admin_action": null,
      "certifications": ["NASM CPT"]
    }
  ]
}
```

---

## PATCH `/admin/coach-applications/approve`

### Purpose
Approve a coach application.

### Request body
```json
{
  "application_id": 4,
  "admin_action": "Approved after credential review"
}
```

### Response
```json
{
  "message": "success",
  "application": {
    "application_id": 4,
    "status": "approved",
    "admin_action": "Approved after credential review"
  }
}
```

---

## PATCH `/admin/coach-applications/reject`

### Purpose
Reject a coach application.

### Request body
```json
{
  "application_id": 4,
  "admin_action": "Missing valid certification"
}
```

### Response
```json
{
  "message": "success",
  "application": {
    "application_id": 4,
    "status": "rejected",
    "admin_action": "Missing valid certification"
  }
}
```

---

# 5. User Report Moderation

## POST `/admin/reports/list`

### Purpose
Fetch user/coach reports by status bucket.

### Request body
```json
{
  "status": "open"
}
```

### Supported values
- `"open"`
- `"closed"`

### Response
```json
{
  "message": "success",
  "reports": [
    {
      "id": 7,
      "report_id": 7,
      "reported_user_id": 33,
      "reporter_user_id": 18,
      "title": "Report against Jane Doe",
      "description": "Harassment in chat",
      "status": "open",
      "admin_action": null
    }
  ]
}
```

---

## PATCH `/admin/reports/close`

### Purpose
Close a report after admin review.

### Request body
```json
{
  "report_id": 7,
  "admin_action": "Closed after review and warning issued"
}
```

### Response
```json
{
  "message": "success",
  "report": {
    "report_id": 7,
    "status": "resolved",
    "admin_action": "Closed after review and warning issued"
  }
}
```

---

# 6. Exercise Management

## GET `/admin/exercises`

### Purpose
Fetch all exercises for admin management.

### Request
No body.

### Response
```json
{
  "message": "success",
  "exercises": [
    {
      "exercise_id": 1,
      "exercise_name": "Push Up",
      "equipment": "Bodyweight",
      "video_url": "/uploads/exercise_videos/coach_12/file.mp4",
      "video_status": "approved",
      "video_review_note": null,
      "created_by": 12
    }
  ]
}
```

---

## POST `/admin/exercises`

### Purpose
Create a new exercise.

### Request body
```json
{
  "exercise_name": "Push Up",
  "equipment": "Bodyweight",
  "video_url": "/uploads/exercise_videos/coach_12/file.mp4",
  "created_by": 12
}
```

### Response
```json
{
  "message": "success",
  "exercise": {
    "exercise_id": 25,
    "exercise_name": "Push Up",
    "equipment": "Bodyweight",
    "video_url": "/uploads/exercise_videos/coach_12/file.mp4",
    "video_status": "pending",
    "video_review_note": null,
    "created_by": 12
  }
}
```

---

## PATCH `/admin/exercises`

### Purpose
Update an existing exercise.

### Request body
```json
{
  "exercise_id": 25,
  "exercise_name": "Incline Push Up",
  "equipment": "Bench",
  "video_url": "/uploads/exercise_videos/coach_12/incline_pushup.mp4"
}
```

### Response
```json
{
  "message": "success",
  "exercise": {
    "exercise_id": 25,
    "exercise_name": "Incline Push Up",
    "equipment": "Bench",
    "video_url": "/uploads/exercise_videos/coach_12/incline_pushup.mp4",
    "video_status": "pending",
    "video_review_note": null,
    "created_by": 12
  }
}
```

---

## DELETE `/admin/exercises`

### Purpose
Delete an exercise.

### Request body
```json
{
  "exercise_id": 25
}
```

### Response
```json
{
  "message": "success"
}
```

### Possible error
```json
{
  "error": "Cannot delete exercise in use"
}
```

---

# 7. Workout / Template Management

## GET `/admin/workouts`

### Purpose
Fetch workout plans/templates for admin management.

### Request
No body.

### Response
```json
{
  "message": "success",
  "workouts": [
    {
      "plan_id": 3,
      "plan_name": "Beginner Push Pull Legs",
      "description": "Strength | 3 days/week | 45 min | Beginner",
      "author_user_id": 1,
      "is_public": 1,
      "total_exercises": 9
    }
  ]
}
```

---

## POST `/admin/workouts`

### Purpose
Create a workout plan/template.

### Request body
```json
{
  "plan_name": "Beginner Push Pull Legs",
  "description": "Strength | 3 days/week | 45 min | Beginner",
  "author_user_id": 1,
  "is_public": 1,
  "exercises": [
    {
      "exercise_id": 1,
      "sets": 3,
      "reps": 12
    },
    {
      "exercise_id": 2,
      "sets": 4,
      "reps": 10
    }
  ]
}
```

### Response
```json
{
  "message": "success",
  "workout": {
    "plan_id": 8,
    "plan_name": "Beginner Push Pull Legs",
    "description": "Strength | 3 days/week | 45 min | Beginner",
    "author_user_id": 1,
    "is_public": 1
  }
}
```

---

## PATCH `/admin/workouts`

### Purpose
Update workout/template metadata.

### Request body
```json
{
  "plan_id": 8,
  "plan_name": "Updated Plan Name",
  "description": "Strength | 4 days/week | 60 min | Intermediate",
  "is_public": 0
}
```

### Response
```json
{
  "message": "success",
  "workout": {
    "plan_id": 8,
    "plan_name": "Updated Plan Name",
    "description": "Strength | 4 days/week | 60 min | Intermediate",
    "author_user_id": 1,
    "is_public": 0
  }
}
```

---

## DELETE `/admin/workouts`

### Purpose
Delete a workout plan/template.

### Request body
```json
{
  "plan_id": 8
}
```

### Response
```json
{
  "message": "success"
}
```

---

# 8. Exercise Video Moderation

## GET `/admin/videos/pending`

### Purpose
Fetch all exercise videos currently pending admin review.

### Request
No body.

### Response
```json
{
  "message": "success",
  "videos": [
    {
      "exercise_id": 11,
      "exercise_name": "Barbell Row",
      "video_url": "/uploads/exercise_videos/coach_19/barbell_row.mp4",
      "video_status": "pending",
      "video_review_note": null,
      "created_by": 19
    }
  ]
}
```

---

## PATCH `/admin/videos/approve`

### Purpose
Approve a pending exercise video.

### Request body
```json
{
  "exercise_id": 11
}
```

### Response
```json
{
  "message": "success",
  "video": {
    "exercise_id": 11,
    "video_status": "approved",
    "video_review_note": null
  }
}
```

---

## PATCH `/admin/videos/reject`

### Purpose
Reject a pending exercise video.

### Request body
```json
{
  "exercise_id": 11,
  "video_review_note": "Wrong exercise demonstrated in the clip"
}
```

### Response
```json
{
  "message": "success",
  "video": {
    "exercise_id": 11,
    "video_status": "rejected",
    "video_review_note": "Wrong exercise demonstrated in the clip"
  }
}
```

---

## PATCH `/admin/videos/remove`

### Purpose
Remove the current video from an exercise.

### Request body
```json
{
  "exercise_id": 11
}
```

### Response
```json
{
  "message": "success",
  "video": {
    "exercise_id": 11,
    "video_url": null,
    "video_status": "rejected"
  }
}
```

---

# 9. Coach Price Moderation

## GET `/admin/coach-prices/pending`

### Purpose
Fetch pending coach price change requests.

### Request
No body.

### Response
```json
{
  "message": "success",
  "requests": [
    {
      "request_id": 5,
      "coach_id": 22,
      "coach_name": "Chris Smith",
      "current_price": 70.0,
      "proposed_price": 80.0,
      "status": "pending",
      "created_at": "2026-04-22T18:00:00"
    }
  ]
}
```

---

## PATCH `/admin/coach-prices/approve`

### Purpose
Approve a pending coach price change request.

### Request body
```json
{
  "request_id": 5,
  "admin_action": "Approved after review"
}
```

### Response
```json
{
  "message": "success",
  "request": {
    "request_id": 5,
    "status": "approved",
    "proposed_price": 80.0
  }
}
```

---

## PATCH `/admin/coach-prices/reject`

### Purpose
Reject a pending coach price change request.

### Request body
```json
{
  "request_id": 5,
  "admin_action": "Price increase exceeds policy"
}
```

### Response
```json
{
  "message": "success",
  "request": {
    "request_id": 5,
    "status": "rejected",
    "proposed_price": 80.0
  }
}
```

---

# Final Endpoint Checklist

## Dashboard + Analytics
- `GET /admin/dashboard/stats`
- `GET /admin/analytics/engagement`

## Users
- `GET /admin/users`
- `PATCH /admin/users/suspend`
- `PATCH /admin/users/deactivate`
- `PATCH /admin/users/status`

## Coaches
- `GET /admin/coaches/active`

## Coach Applications
- `POST /admin/coach-applications/list`
- `PATCH /admin/coach-applications/approve`
- `PATCH /admin/coach-applications/reject`

## Reports
- `POST /admin/reports/list`
- `PATCH /admin/reports/close`

## Exercises
- `GET /admin/exercises`
- `POST /admin/exercises`
- `PATCH /admin/exercises`
- `DELETE /admin/exercises`

## Workouts
- `GET /admin/workouts`
- `POST /admin/workouts`
- `PATCH /admin/workouts`
- `DELETE /admin/workouts`

## Videos
- `GET /admin/videos/pending`
- `PATCH /admin/videos/approve`
- `PATCH /admin/videos/reject`
- `PATCH /admin/videos/remove`

## Coach Prices
- `GET /admin/coach-prices/pending`
- `PATCH /admin/coach-prices/approve`
- `PATCH /admin/coach-prices/reject`

---

# Required Frontend Interfaces

## Standard API

```ts
export interface ApiSuccess {
  message: string;
}

export interface ApiError {
  error: string;
}
```

---

## Dashboard

```ts
export interface AdminDashboardStats {
  total_users: number;
  active_coaches: number;
  pending_reviews: number;
  pending_coach_applications: number;
  open_reports: number;
  monthly_revenue: number;
}

export interface AdminEngagementAnalytics {
  daily_active_users: number;
  weekly_active_users: number;
  monthly_active_users: number;
}
```

---

## User/account moderation

```ts
export type AccountStatus = "active" | "suspended" | "deactivated";

export interface AdminManagedUser {
  user_id: number;
  first_name: string;
  last_name: string;
  name: string;
  email: string;
  phone_number?: string | null;
  is_coach: boolean;
  is_admin: boolean;
  account_status: AccountStatus;
  suspension_reason: string | null;
  updated_at: string | null;
}
```

---

## Active coach listing

```ts
export interface AdminActiveCoach {
  user_id: number;
  first_name: string;
  last_name: string;
  name: string;
  email: string;
  coach_description: string | null;
  price: number | null;
  contract_count: number;
  certifications: {
    cert_name: string;
    provider_name: string | null;
    description: string | null;
    issued_date: string | null;
    expires_date: string | null;
  }[];
}
```

---

## Coach applications

```ts
export interface AdminCoachApplication {
  id: number;
  application_id: number;
  user_id: number;
  name: string;
  email: string;
  appliedLabel: string | null;
  status: "pending" | "approved" | "rejected";
  years_experience: number | null;
  coach_description: string | null;
  desired_price: number | null;
  admin_action: string | null;
  certifications: string[];
}
```

---

## Reports

```ts
export interface AdminReport {
  id: number;
  report_id: number;
  reported_user_id: number;
  reporter_user_id: number;
  title: string;
  description: string;
  status: string;
  admin_action: string | null;
}
```

---

## Exercise

```ts
export type VideoStatus = "pending" | "approved" | "rejected";

export interface AdminExercise {
  exercise_id: number;
  exercise_name: string;
  equipment: string | null;
  video_url: string | null;
  video_status: VideoStatus;
  video_review_note: string | null;
  created_by: number;
}
```

---

## Workout

```ts
export interface AdminWorkout {
  plan_id: number;
  plan_name: string;
  description: string | null;
  author_user_id: number;
  is_public: number;
  total_exercises?: number;
}

export interface AdminWorkoutExerciseInput {
  exercise_id: number;
  sets?: number | null;
  reps?: number | null;
}
```

---

## Video moderation

```ts
export interface AdminModeratedVideo {
  exercise_id: number;
  exercise_name: string;
  video_url: string | null;
  video_status: VideoStatus;
  video_review_note: string | null;
  created_by: number;
}
```

---

## Coach price moderation

```ts
export interface AdminCoachPriceRequest {
  request_id: number;
  coach_id: number;
  coach_name: string;
  current_price: number;
  proposed_price: number;
  status: "pending" | "approved" | "rejected";
  created_at: string;
}
```

---

# Required Frontend Service Modules

Create or update the following service modules.

## `services/adminDashboardService.ts`

Implement:
```ts
getDashboardStats()
getEngagementAnalytics()
```

---

## `services/adminAccountModerationService.ts`

Implement:
```ts
getUsers()
suspendUser(payload)
deactivateUser(payload)
updateUserStatus(payload)
getActiveCoaches()
```

---

## `services/adminCoachApplicationService.ts`

Implement:
```ts
getCoachApplications(payload)
approveCoachApplication(payload)
rejectCoachApplication(payload)
```

---

## `services/adminReportService.ts`

Implement:
```ts
getReports(payload)
closeReport(payload)
```

---

## `services/adminExerciseService.ts`

Implement:
```ts
getExercises()
createExercise(payload)
updateExercise(payload)
deleteExercise(payload)
```

---

## `services/adminWorkoutService.ts`

Implement:
```ts
getWorkouts()
createWorkout(payload)
updateWorkout(payload)
deleteWorkout(payload)
```

---

## `services/adminVideoModerationService.ts`

Implement:
```ts
getPendingVideos()
approveVideo(payload)
rejectVideo(payload)
removeVideo(payload)
```

---

## `services/adminCoachPriceService.ts`

Implement:
```ts
getPendingCoachPriceRequests()
approveCoachPriceRequest(payload)
rejectCoachPriceRequest(payload)
```

---

# Required Frontend UI Pages

Create or update these admin pages.

## `pages/admin/AdminDashboardPage.tsx`

Needs:
- dashboard stat cards
- engagement analytics cards/charts
- pending review counts
- revenue summary

---

## `pages/admin/AdminUsersPage.tsx`

Needs:
- list all users
- status badge
- suspend modal requiring reason
- deactivate confirmation
- restore-to-active action using `PATCH /admin/users/status`

---

## `pages/admin/AdminActiveCoachesPage.tsx`

Needs:
- list active coaches
- show coach pricing
- show certifications
- show contract counts

---

## `pages/admin/AdminCoachApplicationsPage.tsx`

Needs:
- pending / approved / rejected tabs
- application detail cards
- approve/reject actions with admin note

---

## `pages/admin/AdminReportsPage.tsx`

Needs:
- open / closed tabs
- report detail display
- close action with admin note

---

## `pages/admin/AdminExercisesPage.tsx`

Needs:
- list all exercises
- create exercise modal
- edit exercise modal
- delete confirmation

---

## `pages/admin/AdminWorkoutsPage.tsx`

Needs:
- list all workouts/templates
- create workout modal
- edit workout modal
- delete confirmation

---

## `pages/admin/AdminVideoModerationPage.tsx`

Needs:
- list pending videos
- embedded video preview
- approve button
- reject modal with review note
- remove button

---

## `pages/admin/AdminCoachPricesPage.tsx`

Needs:
- pending price request list
- show current price vs proposed price
- approve/reject actions with admin note

---

# Request Construction Rules

## For GET requests
Use normal GET with credentials included.

## For POST/PATCH/DELETE requests
Always send:
- `Content-Type: application/json`
- a JSON body
- credentials included

Example:
```ts
fetch("/admin/users/suspend", {
  method: "PATCH",
  credentials: "include",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    user_id: 17,
    suspension_reason: "Policy violation"
  })
})
```

---

# Do Not Do These Things

- do not pass action parameters in the URL query string
- do not invent `/admin/users/:user_id/reactivate`
- do not invent `/admin/videos/:exercise_id/reject`
- do not invent `/admin/exercises/:exercise_id`
- do not invent `/admin/coach-applications?status=pending`
- do not invent `/admin/reports?status=open`
- do not assume form-data unless specifically told otherwise
- do not assume path-param mutation routes
- do not omit `credentials: "include"`

---

# Expected Error Handling

The frontend should handle these common response shapes:

## Unauthorized
```json
{
  "error": "Unauthorized"
}
```

## Forbidden
```json
{
  "error": "Forbidden"
}
```

## Validation failure
```json
{
  "error": "..."
}
```

## Success
```json
{
  "message": "success",
  ...
}
```

---

# Implementation Goal

Build a clean admin frontend that exactly matches this finalized backend contract.

Prioritize:
- typed interfaces
- service wrappers
- modal-based CRUD flows
- JSON-body request helpers
- no URL-param mutation patterns
- compatibility with existing React + Vite project organization
- full admin coverage, not just the newer CRUD endpoints