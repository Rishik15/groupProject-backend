# Admin Frontend Implementation Prompt

You are working on the React + Vite + TypeScript frontend for an existing Flask backend workout application.

Your job is to implement the **admin frontend only** for the finalized backend contract described below.

Follow this prompt strictly.

---

# Core Rules

## 1. All non-GET backend input must be sent in the JSON request body

Do **not** pass editable values, action data, filters, status values, reasons, or form fields in the URL query string.

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
Do not invent query-string-based actions.
Do not invent extra route variants.
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

The backend admin implementation is organized around **four domains**:

1. exercise management
2. workout/template management
3. exercise video moderation
4. account enforcement

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

The backend will add the following fields.

## Exercise table additions

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

## Users table additions

The `users_immutables` table will gain:

- `account_status ENUM('active','suspended','deactivated') DEFAULT 'active'`
- `suspension_reason TEXT NULL`

### Meaning

- `account_status` is the master account state
- `suspension_reason` is required when suspending
- `updated_at` already exists and will reflect changes automatically
- there is **no separate suspended_until field**
- there is **no separate reactivation endpoint**

---

# Finalized Endpoint Contract

These are the final endpoints the frontend must use.

---

# 1. Admin Exercise Management

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

### Notes
- `video_url` is optional
- if `video_url` is provided for a newly submitted coach video, the backend may set `video_status` to `"pending"`
- `created_by` should be included when relevant

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

### Notes
- send all edited values in JSON
- do not put `exercise_id` in the URL
- partial update behavior may be supported, but sending the edited fields explicitly is preferred

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

### Notes
- do not place the id in the URL
- backend may reject deletion if the exercise is already used in a workout plan

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

# 2. Admin Workout / Workout Template Management

These endpoints manage workout plans backed by the existing plan/template/day/exercise schema.

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
      "description": "Starter template",
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

### Notes
- the backend will initially follow the existing single-day creation style
- send exercise content as JSON
- do not encode workout content into URL parameters

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

# 3. Admin Exercise Video Moderation

These endpoints moderate exercise-linked videos.

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

### Notes
- the review note should be sent in JSON
- the backend will store the note in `video_review_note`

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

# 4. Admin Account Enforcement

These endpoints manage account status for users and coaches through the shared user system.

## GET `/admin/users`

### Purpose
Fetch users/coaches for admin review.

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
- the backend updates:
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

### Notes
- use JSON body
- this endpoint replaces the idea of a separate reactivate route
- if the account later needs to be made active again, that will be handled through the general update route, not a dedicated `/reactivate` endpoint

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
- this is the only general status-change endpoint
- do not build or call a dedicated `/reactivate` route
- use this route when the UI needs to restore an account to active status

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

# Final Endpoint Checklist

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

## Video Moderation
- `GET /admin/videos/pending`
- `PATCH /admin/videos/approve`
- `PATCH /admin/videos/reject`
- `PATCH /admin/videos/remove`

## Account Enforcement
- `GET /admin/users`
- `PATCH /admin/users/suspend`
- `PATCH /admin/users/deactivate`
- `PATCH /admin/users/status`

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

## Account enforcement

```ts
export type AccountStatus = "active" | "suspended" | "deactivated";

export interface AdminManagedUser {
  user_id: number;
  first_name: string;
  last_name: string;
  name: string;
  email: string;
  is_coach: boolean;
  is_admin: boolean;
  account_status: AccountStatus;
  suspension_reason: string | null;
  updated_at: string | null;
}
```

---

# Required Frontend Service Modules

Create or update the following service modules.

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

## `services/adminAccountModerationService.ts`

Implement:
```ts
getUsers()
suspendUser(payload)
deactivateUser(payload)
updateUserStatus(payload)
```

---

# Required Frontend UI Pages

Create or update these admin pages.

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

## `pages/admin/AdminAccountModerationPage.tsx`

Needs:
- list all managed users
- show account status badge
- suspend modal requiring reason
- deactivate confirmation/modal
- restore-to-active action using `PATCH /admin/users/status`

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
- do not assume form-data unless specifically told otherwise
- do not assume path-param REST style for mutable admin actions
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