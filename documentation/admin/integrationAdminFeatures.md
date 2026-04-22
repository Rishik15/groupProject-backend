# Admin Frontend Guide

This document defines how the frontend should interact with the admin backend.

---

## Core Rules

### 1. Always use JSON for mutations
All POST, PATCH, DELETE requests must send JSON bodies.

### 2. Always include credentials
Use:
credentials: "include"

---

## Admin Endpoints

### Exercises
GET /admin/exercises  
POST /admin/exercises  
PATCH /admin/exercises  
DELETE /admin/exercises  

---

### Workouts
GET /admin/workouts  
POST /admin/workouts  
PATCH /admin/workouts  
DELETE /admin/workouts  
PATCH /admin/workouts/exercises  

---

### Videos
GET /admin/videos/pending  
PATCH /admin/videos/approve  
PATCH /admin/videos/reject  
PATCH /admin/videos/remove  

---

## Exercises

### Create
{
  "exercise_name": "Push Up",
  "equipment": "Bodyweight",
  "video_url": "/uploads/file.mp4"
}

Notes:
- video_url optional
- if present → status = pending
- if absent → status = approved

---

### Update
{
  "exercise_id": 25,
  "exercise_name": "Incline Push Up",
  "video_url": "/uploads/new.mp4"
}

Effect:
- video_url change resets moderation

---

### Delete
{
  "exercise_id": 25
}

---

## Workouts

### Create
{
  "plan_name": "Workout",
  "description": "...",
  "author_user_id": 4,
  "is_public": 0,
  "exercises": [
    { "exercise_id": 2, "sets": 3, "reps": 10 }
  ]
}

Creates:
- workout_plan
- workout_day (Day 1)
- plan_exercise entries

---

### Update Metadata
{
  "plan_id": 1,
  "plan_name": "Updated",
  "description": "...",
  "is_public": 1
}

---

### Delete
{
  "plan_id": 1
}

---

### Update Exercises (Current Behavior)

{
  "plan_id": 1,
  "exercises": [
    { "exercise_id": 2, "sets": 3, "reps": 10 }
  ]
}

Important:
- Only updates the FIRST day
- Does NOT replace entire plan

---

## Video Moderation

### Approve
{
  "exercise_id": 32
}

### Reject
{
  "exercise_id": 33,
  "video_review_note": "Incorrect form"
}

### Remove
{
  "exercise_id": 34
}

Effect:
- clears video_url
- sets rejected status

---

## Frontend Services

adminExerciseService:
- getExercises
- createExercise
- updateExercise
- deleteExercise

adminWorkoutService:
- getWorkouts
- createWorkout
- updateWorkout
- deleteWorkout
- updateWorkoutExercises

adminVideoModerationService:
- getPendingVideos
- approveVideo
- rejectVideo
- removeVideo

---

## UI Pages

AdminExercisesPage:
- list
- create
- edit
- delete

AdminWorkoutsPage:
- list
- create
- edit metadata
- delete
- edit day 1 exercises only

AdminVideoModerationPage:
- pending queue
- approve
- reject
- remove

---

## Do Not Do

- do not send mutation params in URL
- do not omit credentials
- do not assume multi-day editing