# endpoints headers
- localhost:8080/workoutAction

- localhost:8080/exerciseLog

### For all:
- frontend sends `user_id` in session

---

## getActiveWorkoutSession
-localhost:8080/workoutAction/active

-method: `GET`

-backend returns

```json
{
  "session": {
    "session_id": int,
    "user_id": int,
    "started_at": str,
    "ended_at": str | null,
    "workout_plan_id": int | null,
    "notes": str | null
  },
  "sets": [
    {
      "set_log_id": int,
      "session_id": int,
      "exercise_id": int,
      "set_number": int,
      "reps": int | null,
      "weight": float | null,
      "rpe": float | null,
      "performed_at": str
    }
  ],
  "cardio": [
    {
      "cardio_log_id": int,
      "session_id": int | null,
      "user_id": int,
      "performed_at": str,
      "steps": int | null,
      "distance_km": float | null,
      "duration_min": int | null,
      "calories": int | null,
      "avg_hr": int | null
    }
  ]
}
```

-if no active session

```json
{
  "message": "No active workout session",
  "session": null
}
```

---

## startWorkoutSession
-localhost:8080/workoutAction/start

-method: `POST`

-frontend sends

```json
{
  "workout_plan_id": int | null,
  "notes": str | null
}
```

-backend returns

```json
{
  "message": "Workout session started successfully",
  "session": {
    "session_id": int,
    "user_id": int,
    "started_at": str,
    "ended_at": str | null,
    "workout_plan_id": int | null,
    "notes": str | null
  }
}
```

---

## getWorkoutSession
-localhost:8080/workoutAction/get_workout

-method: `GET`

-frontend sends

```json
{
  "session_id": int
}
```

-backend returns

```json
{
  "session": {
    "session_id": int,
    "user_id": int,
    "started_at": str,
    "ended_at": str | null,
    "workout_plan_id": int | null,
    "notes": str | null
  },
  "sets": [
    {
      "set_log_id": int,
      "session_id": int,
      "exercise_id": int,
      "set_number": int,
      "reps": int | null,
      "weight": float | null,
      "rpe": float | null,
      "performed_at": str
    }
  ],
  "cardio": [
    {
      "cardio_log_id": int,
      "session_id": int | null,
      "user_id": int,
      "performed_at": str,
      "steps": int | null,
      "distance_km": float | null,
      "duration_min": int | null,
      "calories": int | null,
      "avg_hr": int | null
    }
  ]
}
```

-if session not found

```json
{
  "error": "Workout session not found"
}
```

---

## markWorkoutDone
-localhost:8080/workoutAction/mark_workout_done

-method: `PATCH`

-frontend sends

```json
{
  "session_id": int
}
```

-backend returns

```json
{
  "message": "Workout session ended successfully"
}
```

-if session already ended

```json
{
  "error": "Workout session already ended"
}
```

-if session not found

```json
{
  "error": "Workout session not found"
}
```

---

## Get plan / session ids
-localhost:8080/workoutAction/getSWPids

-method: `GET`

-backend returns

```json
{
  "message": "successful",
  "Sessions": [
    {
      "session_id": int,
      "workout_plan_id": int,
      "plan_name": str
    }
  ]
}
```

-if no sessions found

```json
{
  "message": "successful",
  "Sessions": []
}
```

---

## Get exercise information
-localhost:8080/workoutAction/getExerciseInfo

-method: `GET`

-frontend sends

```json
{
  "workout_plan_id": int
}
```

-backend returns

```json
{
  "message": "success",
  "exercise_info": [
    {
      "exercise_id": int,
      "order_in_workout": int,
      "sets_goal": int | null,
      "reps_goal": int | null,
      "weight_goal": float | null,
      "exercise_name": str,
      "equipment": str | null,
      "video_url": str | null
    }
  ]
}
```

-if no exercise info found

```json
{
  "message": "success",
  "exercise_info": []
}
```

---

## logWeights
-localhost:8080/exerciseLog/log_weights

-method: `POST`

-frontend sends

```json
{
  "session_id": int,
  "exercise_id": int,
  "set_number": int,
  "reps": int | null,
  "weight": float | null,
  "rpe": float | null,
  "datetimeFinished": str | null
}
```

-required fields
- `session_id`
- `exercise_id`
- `set_number`

-validation rules
- `set_number >= 1`
- `reps >= 0` if provided
- `weight >= 0` if provided
- `rpe >= 0` if provided
- `datetimeFinished` must be ISO datetime if provided

-backend returns

```json
{
  "message": "Set logged successfully"
}
```

-if session not found

```json
{
  "error": "Workout session not found"
}
```

-if session already ended

```json
{
  "error": "Cannot log to an ended workout session"
}
```

-if invalid number or datetime

```json
{
  "error": "Invalid numeric or datetime format"
}
```

---

## logCardio
-localhost:8080/exerciseLog/log_cardio

-method: `POST`

-frontend sends

```json
{
  "session_id": int | null,
  "performed_at": str | null,
  "steps": int | null,
  "distance_km": float | null,
  "duration_min": int | null,
  "calories": int | null,
  "avg_hr": int | null
}
```

-note
- `session_id` is optional
- at least one of the following cardio fields must be provided:
  - `steps`
  - `distance_km`
  - `duration_min`
  - `calories`
  - `avg_hr`

-validation rules
- `steps >= 0` if provided
- `distance_km >= 0` if provided
- `duration_min >= 0` if provided
- `calories >= 0` if provided
- `avg_hr >= 0` if provided
- `performed_at` must be ISO datetime if provided

-backend returns

```json
{
  "message": "Cardio logged successfully"
}
```

-if session not found

```json
{
  "error": "Workout session not found"
}
```

-if session already ended

```json
{
  "error": "Cannot log cardio to an ended workout session"
}
```

-if no cardio fields were provided

```json
{
  "error": "At least one cardio field is required: steps, distance_km, duration_min, calories, avg_hr"
}
```

-if invalid number or datetime

```json
{
  "error": "Invalid numeric or datetime format"
}
```

---

## Common error responses

### Unauthorized
```json
{
  "error": "Unauthorized"
}
```

### Bad request
```json
{
  "error": str
}
```

### Not found
```json
{
  "error": str
}
```

### Server error
```json
{
  "error": "Internal server error"
}
```

---

## Notes for backend consistency

- `Sessions` should always be a list
- `exercise_info` should always be a list
- `get_workout` must pass `session_id` into `getWorkoutSessionById(user_id, session_id)`
- `getSWPids` should return the direct result of `getPlanNamesAndIds(user_id)`
- route handlers should not return raw exception text to the client