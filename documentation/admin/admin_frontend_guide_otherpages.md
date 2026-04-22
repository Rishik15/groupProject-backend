# Frontend Integration Summary for Admin Features

This is a backend-facing summary for the React + Vite frontend so implementation can begin before the backend is fully written.

The frontend should assume all requests and responses are JSON unless explicitly noted otherwise.

This summary is based on the requested backend scope and constraints already defined for the repository. :contentReference[oaicite:0]{index=0}

---

# Goal

We are adding backend-only support for an admin area that covers:

1. exercise database management
2. workout / workout-template management
3. exercise video moderation
4. user / coach account enforcement

The frontend should prepare admin pages, interfaces, service calls, and UI flows around those features.

---

# General API Behavior Assumptions

The frontend should assume:

- session-based auth is already in place
- admin authorization is enforced by the backend
- request bodies are JSON
- response bodies are JSON
- standard success style will usually look like:

```json
{ "message": "success", ... }
```

- standard error style will usually look like:

```json
{ "error": "..." }
```

The frontend should also assume that:
- backend may return `401` for unauthenticated
- backend may return `403` for authenticated but unauthorized
- backend may return `400` for missing/invalid input
- backend may return `404` when a target record does not exist

---

# Recommended Frontend Architecture

Given your React + Vite structure with services, utils, interfaces, components, wrapper pages, and general architecture, the cleanest split is:

## services

Create admin API service modules such as:

- `services/adminExerciseService.ts`
- `services/adminWorkoutService.ts`
- `services/adminVideoModerationService.ts`
- `services/adminAccountModerationService.ts`

Each should wrap fetch/axios calls and return typed JSON.

## interfaces

Create shared admin-facing interfaces for:

- exercises
- workout plans / templates
- moderated videos
- admin-managed accounts
- standard API responses

## components

Likely useful reusable components:

- admin table/list view
- row action buttons
- approve/reject modal
- delete confirmation modal
- suspend/deactivate modal
- edit/create form modal
- status badge component

## wrapper pages

Suggested admin pages:

- `pages/admin/AdminExercisesPage.tsx`
- `pages/admin/AdminWorkoutsPage.tsx`
- `pages/admin/AdminVideoModerationPage.tsx`
- `pages/admin/AdminAccountModerationPage.tsx`

## utils

Useful helpers:

- response error parsing
- date formatting
- status-to-badge mapping
- request payload shaping
- optimistic update helpers if desired

---

# Endpoint Summary

Below is the likely backend contract the frontend can begin against.

---

# 1. Admin Exercise Management

These endpoints support exercise CRUD.

## GET `/admin/exercises`

### Purpose

Fetch all exercises for admin management.

### Request

No body.

### Expected response

```json
{
  "message": "success",
  "exercises": [
    {
      "exercise_id": 1,
      "exercise_name": "Push Up",
      "equipment": "Bodyweight",
      "video_url": "/uploads/exercises/user_12/pushup.mp4"
    }
  ]
}
```

### Frontend use

- populate admin exercise table
- support search/filter client-side initially if backend does not expose filter params yet

---

## POST `/admin/exercises`

### Purpose

Create a new exercise.

### Request body

```json
{
  "exercise_name": "Push Up",
  "equipment": "Bodyweight",
  "video_url": "/uploads/exercises/user_12/pushup.mp4"
}
```

### Notes

Frontend should treat `video_url` as optional unless backend later makes it required.

### Expected response

```json
{
  "message": "success",
  "exercise": {
    "exercise_id": 25,
    "exercise_name": "Push Up",
    "equipment": "Bodyweight",
    "video_url": "/uploads/exercises/user_12/pushup.mp4"
  }
}
```

---

## PATCH `/admin/exercises/:exercise_id`

### Purpose

Edit an existing exercise.

### Request body

Any subset of editable fields:

```json
{
  "exercise_name": "Incline Push Up",
  "equipment": "Bench",
  "video_url": "/uploads/exercises/user_12/incline_pushup.mp4"
}
```

### Expected response

```json
{
  "message": "success",
  "exercise": {
    "exercise_id": 25,
    "exercise_name": "Incline Push Up",
    "equipment": "Bench",
    "video_url": "/uploads/exercises/user_12/incline_pushup.mp4"
  }
}
```

### Frontend use

- edit modal or side panel
- partial updates are safest

---

## DELETE `/admin/exercises/:exercise_id`

### Purpose

Delete an exercise.

### Request

No body.

### Expected response

```json
{
  "message": "success"
}
```

### Frontend use

- destructive action with confirmation modal
- remove item from local list after success

---

# 2. Admin Workout / Workout Template Management

These are intended only if they fit the current backend schema cleanly. The frontend can still scaffold for them now.

Because the backend already appears to use tables like `workout_plan`, `workout_plan_template`, `workout_day`, and `plan_exercise`, the frontend should expect plan/template CRUD around an object model rather than a totally flat record. :contentReference[oaicite:1]{index=1}

## GET `/admin/workouts`

### Purpose

Fetch admin-manageable workout plans and/or templates.

### Expected response

Example shape:

```json
{
  "message": "success",
  "workouts": [
    {
      "workout_plan_id": 3,
      "name": "Beginner Push Pull Legs",
      "description": "Starter template",
      "is_template": true
    }
  ]
}
```

### Frontend note

Use a normalized interface that can support either:
- actual plans
- templates
- both, with an `is_template` flag

---

## POST `/admin/workouts`

### Purpose

Create a workout plan or template.

### Request body

Example:

```json
{
  "name": "Beginner Push Pull Legs",
  "description": "Starter template",
  "is_template": true
}
```

If the backend later accepts nested days/exercises during creation, the frontend can extend to:

```json
{
  "name": "Beginner Push Pull Legs",
  "description": "Starter template",
  "is_template": true,
  "days": [
    {
      "day_name": "Push",
      "exercises": [
        {
          "exercise_id": 1,
          "sets": 3,
          "reps": 12
        }
      ]
    }
  ]
}
```

### Expected response

```json
{
  "message": "success",
  "workout": {
    "workout_plan_id": 8,
    "name": "Beginner Push Pull Legs",
    "description": "Starter template",
    "is_template": true
  }
}
```

---

## PATCH `/admin/workouts/:workout_id`

### Purpose

Edit a workout plan or template.

### Request body

```json
{
  "name": "Updated Plan Name",
  "description": "Updated description"
}
```

### Expected response

```json
{
  "message": "success",
  "workout": {
    "workout_plan_id": 8,
    "name": "Updated Plan Name",
    "description": "Updated description",
    "is_template": true
  }
}
```

---

## DELETE `/admin/workouts/:workout_id`

### Purpose

Delete a workout plan or template.

### Expected response

```json
{
  "message": "success"
}
```

### Frontend note

Use confirmation before delete because related days / exercises may also disappear depending on backend implementation.

---

# 3. Admin Exercise Video Moderation

The backend goal is minimal moderation support for exercise videos, preferably reusing the current `exercise.video_url` model rather than redesigning uploads. :contentReference[oaicite:2]{index=2}

The frontend should assume moderation happens against exercise-linked videos.

## GET `/admin/videos/pending`

### Purpose

List exercise videos waiting for review.

### Expected response

Example:

```json
{
  "message": "success",
  "videos": [
    {
      "exercise_id": 11,
      "exercise_name": "Barbell Row",
      "video_url": "/uploads/exercises/user_19/barbell_row.mp4",
      "video_status": "pending"
    }
  ]
}
```

### Frontend use

- moderation queue page
- preview player + approve/reject/remove actions

---

## PATCH `/admin/videos/:exercise_id/approve`

### Purpose

Approve an exercise video.

### Request body

Can be empty JSON:

```json
{}
```

### Expected response

```json
{
  "message": "success",
  "video": {
    "exercise_id": 11,
    "video_status": "approved"
  }
}
```

---

## PATCH `/admin/videos/:exercise_id/reject`

### Purpose

Reject an exercise video.

### Request body

Optional reason:

```json
{
  "reason": "Wrong exercise demonstrated"
}
```

### Expected response

```json
{
  "message": "success",
  "video": {
    "exercise_id": 11,
    "video_status": "rejected"
  }
}
```

### Frontend note

Build the UI to support an optional moderation note field, even if backend initially ignores it.

---

## DELETE `/admin/videos/:exercise_id`

### Purpose

Remove a video from an exercise.

This may either:
- clear `video_url`
- remove backing media file if local storage is used
- mark it removed in moderation workflow

### Request

No body.

### Expected response

```json
{
  "message": "success"
}
```

### Frontend use

- destructive action
- remove item from pending queue or update its row

---

# 4. Admin Account Enforcement

The backend goal is minimal support for suspension / deactivation of user and coach accounts for policy violations. :contentReference[oaicite:3]{index=3}

The frontend should assume that both users and coaches can be managed through a shared admin moderation UI.

## GET `/admin/users`

### Purpose

Fetch users/coaches for admin review.

### Expected response

Example:

```json
{
  "message": "success",
  "users": [
    {
      "user_id": 17,
      "full_name": "Jane Doe",
      "email": "jane@example.com",
      "role": "coach",
      "account_status": "active",
      "suspension_reason": null,
      "suspended_until": null
    }
  ]
}
```

### Frontend note

Create a shared `AdminManagedUser` interface that supports both user and coach records.

---

## PATCH `/admin/users/:user_id/suspend`

### Purpose

Suspend a user/coach.

### Request body

```json
{
  "suspension_reason": "Policy violation",
  "suspended_until": "2026-05-15T00:00:00"
}
```

### Expected response

```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "suspended",
    "suspension_reason": "Policy violation",
    "suspended_until": "2026-05-15T00:00:00"
  }
}
```

### Frontend use

- suspension modal with:
  - reason input
  - optional date picker
- allow empty date if backend supports indefinite suspension

---

## PATCH `/admin/users/:user_id/deactivate`

### Purpose

Deactivate a user/coach account.

### Request body

Optional body:

```json
{
  "reason": "Severe policy violation"
}
```

### Expected response

```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "deactivated"
  }
}
```

### Frontend note

Treat as destructive / high-friction admin action.

---

## PATCH `/admin/users/:user_id/reactivate`

### Purpose

Reactivate or unsuspend a previously restricted account.

### Request body

Can be empty:

```json
{}
```

### Expected response

```json
{
  "message": "success",
  "user": {
    "user_id": 17,
    "account_status": "active",
    "suspension_reason": null,
    "suspended_until": null
  }
}
```

### Frontend use

- show conditional button only when status is not active

---

# Suggested TypeScript Interfaces

These are good frontend starter contracts.

## Standard API shapes

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
export interface AdminExercise {
  exercise_id: number;
  exercise_name: string;
  equipment: string | null;
  video_url: string | null;
}
```

---

## Workout

```ts
export interface AdminWorkout {
  workout_plan_id: number;
  name: string;
  description?: string | null;
  is_template?: boolean;
}
```

If nested editing is later supported:

```ts
export interface AdminWorkoutDay {
  day_name: string;
  exercises: AdminWorkoutExercise[];
}

export interface AdminWorkoutExercise {
  exercise_id: number;
  sets?: number | null;
  reps?: number | null;
}
```

---

## Moderated video

```ts
export type VideoStatus = "pending" | "approved" | "rejected";

export interface AdminModeratedVideo {
  exercise_id: number;
  exercise_name: string;
  video_url: string | null;
  video_status: VideoStatus;
}
```

---

## Managed account

```ts
export type AccountStatus = "active" | "suspended" | "deactivated";

export interface AdminManagedUser {
  user_id: number;
  full_name: string;
  email: string;
  role: string;
  account_status: AccountStatus;
  suspension_reason: string | null;
  suspended_until: string | null;
}
```

---

# Suggested Service Layer Methods

The frontend can scaffold functions like these now.

## `adminExerciseService.ts`

```ts
getExercises()
createExercise(payload)
updateExercise(exerciseId, payload)
deleteExercise(exerciseId)
```

## `adminWorkoutService.ts`

```ts
getWorkouts()
createWorkout(payload)
updateWorkout(workoutId, payload)
deleteWorkout(workoutId)
```

## `adminVideoModerationService.ts`

```ts
getPendingVideos()
approveVideo(exerciseId)
rejectVideo(exerciseId, payload?)
removeVideo(exerciseId)
```

## `adminAccountModerationService.ts`

```ts
getUsers()
suspendUser(userId, payload)
deactivateUser(userId, payload?)
reactivateUser(userId)
```

---

# Suggested Component / Page Breakdown

## Admin Exercises Page

Should support:
- table/list of exercises
- create exercise modal
- edit exercise modal
- delete confirmation

## Admin Workouts Page

Should support:
- list of plans/templates
- create/edit/delete
- possible future nested day/exercise editor

## Admin Video Moderation Page

Should support:
- pending queue
- embedded video preview
- approve / reject / remove buttons
- optional rejection reason modal

## Admin Account Moderation Page

Should support:
- list of users/coaches
- status badge
- suspend modal
- deactivate confirmation
- reactivate action

---

# Important Frontend Assumptions to Keep Flexible

Because backend implementation has not yet inspected all actual files/schema, the frontend should keep these areas flexible:

## 1. Workout object details may change slightly

The backend will reuse existing tables and may return either:
- a simple top-level workout list
- or a richer nested shape later

Frontend should normalize API results in services if needed.

## 2. Video moderation may be tied directly to exercises

At least initially, there may not be a separate `video` entity.
The moderation row may just be an exercise record plus moderation fields.

## 3. Account moderation may use one shared user endpoint

Even for coaches, the backend may expose management under `/admin/users/...` rather than separate `/admin/coaches/...`.

## 4. Some optional fields may be null

The frontend should safely handle nulls for:
- `equipment`
- `video_url`
- `description`
- `suspension_reason`
- `suspended_until`

---

# Minimum Frontend Deliverables That Can Start Immediately

The frontend person can begin now with:

1. TypeScript interfaces
2. admin service modules
3. page shells / route wiring
4. table views for all 4 admin areas
5. create/edit/delete modals
6. moderation action buttons
7. optimistic local state updates after success
8. generic API error handling

Even if backend details shift slightly, these pieces should remain valid.

---

# Final Endpoint Checklist

## Exercises

- `GET /admin/exercises`
- `POST /admin/exercises`
- `PATCH /admin/exercises/:exercise_id`
- `DELETE /admin/exercises/:exercise_id`

## Workouts

- `GET /admin/workouts`
- `POST /admin/workouts`
- `PATCH /admin/workouts/:workout_id`
- `DELETE /admin/workouts/:workout_id`

## Video Moderation

- `GET /admin/videos/pending`
- `PATCH /admin/videos/:exercise_id/approve`
- `PATCH /admin/videos/:exercise_id/reject`
- `DELETE /admin/videos/:exercise_id`

## Account Enforcement

- `GET /admin/users`
- `PATCH /admin/users/:user_id/suspend`
- `PATCH /admin/users/:user_id/deactivate`
- `PATCH /admin/users/:user_id/reactivate`

---

# Bottom Line

Frontend can start building the admin area now around four domains:

- exercises
- workouts
- video moderation
- account moderation

The safest frontend approach is:
- typed service wrappers
- reusable CRUD table patterns
- modal-driven actions
- flexible interfaces with nullable optional fields
- no assumptions beyond JSON request/response contracts

The backend implementation is explicitly intended to stay minimal, reuse existing patterns, keep route files thin, keep logic in services, preserve session auth, and match existing JSON response style. :contentReference[oaicite:4]{index=4}