# Workout Plan Feature Integration and Testing Guide

## Scope

This guide covers the frontend integration expectations for the workout-plan-related backend changes shown in the PR/files you shared.

The main functional areas covered here are:

- creating a custom workout plan
- duplicate-plan prevention
- predefined/public plan browsing
- reading exercises inside a plan
- workout session lifecycle support that depends on the new plan structure

Important structural change: workout plans now use `workout_day` as the parent for `plan_exercise`. `plan_exercise` is no longer treated as directly belonging to `plan_id`; it belongs to `day_id`. That affects duplicate checking, plan creation, predefined-plan counting, and exercise retrieval.

---

# Routing / Blueprint Overview

The workouts feature is split across three blueprints:

- workoutAction_bp
- exerciseLog_bp
- workouts_bp

These are registered from app/routes/workouts/__init__.py, which imports:

- exerciseLogging
- workoutActions
- predefinedPlans
- assignPlan
- exercisesInPlan
- createWorkoutPlan

Confirmed route:

POST /workouts/create

---

# Feature Summary

## 1. Create Custom Workout Plan

### Request body

{
  "name": "Leg Day Builder",
  "exercises": [
    {
      "exercise_id": 2,
      "sets": 4,
      "reps": 10
    },
    {
      "exercise_id": 28,
      "sets": 3,
      "reps": 15
    }
  ]
}

### Backend usage

- ex["exercise_id"]
- ex.get("sets")
- ex.get("reps")

### Success response

{
  "message": "Workout plan created successfully",
  "plan_id": 123
}

### Validation

Do not submit if:

- user not logged in
- name empty
- exercises empty

Backend returns:

- 401 if no session
- 400 if missing name
- 400 if no exercises

---

## 2. Duplicate Plan Detection

Two checks:

### Name conflict

- same author_user_id
- same plan_name

### Structure conflict

Compared fields:

- exercise_id
- sets_goal
- reps_goal

Ignored:

- weight_goal

Responses:

409 "You already have a plan with this name."
409 "You already have a plan with these exact exercises and goals."

---

## Data Model Change

Flow:

- workout_plan
- workout_plan_template
- workout_day (single)
- plan_exercise (linked via day_id)

Defaults:

- day_order = 1
- day_label = "Day 1"

Implication:

All custom plans are single-day.

---

## Visibility

Inserted as:

- author_user_id = current user
- is_public = 0

Custom plans are private.

---

## Predefined Plans

Filter:

- author_user_id = 1
- is_public = 1

Returns:

- plan_id
- plan_name
- description
- exercise_count

Filters (string LIKE):

- category
- days_per_week
- duration
- level

Format:

{Category} | {X} days/week | {Duration} min | {Level}

---

## Plan Exercises Response Shape

type WorkoutPlanExerciseDetail = {
  order_in_workout: number
  sets_goal: number | null
  reps_goal: number | null
  weight_goal: number | null
  exercise_name: string
  equipment: string | null
  video_url: string | null
  day_order: number
  day_label: string
}

Render:

- group by day_order
- sort by order_in_workout

---

## Workout Session Integration

Returned:

- exercise_id
- order_in_workout
- sets_goal
- reps_goal
- weight_goal
- day_order
- day_label

Session lifecycle:

- startWorkoutSession
- getWorkoutSessionById
- getActiveWorkoutSession
- endWorkoutSession

---

# Frontend Integration

## Create Payload

{
  "name": "My Custom Plan",
  "exercises": [
    {
      "exercise_id": 5,
      "sets": 4,
      "reps": 8
    }
  ]
}

## Error Handling

- 401 → login
- 400 → validation
- 409 → duplicate
- 500 → generic

---

# Testing Guide

## Happy Path

- returns 201
- returns plan_id
- creates Day 1

## Missing Name

{
  "name": "",
  "exercises": [...]
}

→ 400

## Empty Exercises

{
  "name": "Test",
  "exercises": []
}

→ 400

## Duplicate Name

→ 409

## Duplicate Structure

→ 409

---

# Types

type CreateWorkoutPlanExercise = {
  exercise_id: number
  sets: number
  reps: number
}

type CreateWorkoutPlanRequest = {
  name: string
  exercises: CreateWorkoutPlanExercise[]
}

type CreateWorkoutPlanResponse = {
  message: string
  plan_id: number
}

---

# Notes

- session-based auth
- private plans
- single-day only
- duplicate check ignores weight

---

# Summary

Plans now depend on workout_day.

Frontend must:

- handle day_order / day_label
- treat custom plans as single-day
- handle duplicate conflicts correctly