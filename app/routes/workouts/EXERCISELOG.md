# endpoints headers
- localhost:8080/workoutAction

- localhost:8080/exerciseLog

### For all:  frontend send user_id in session

## getActiveWorkoutSession
-localhost:8080/workoutAction/active

-backend returns

```json 
{
"session": workout_session,
"sets": sets,
 "cardio": cardio
}
```

## startWorkoutSession
localhost:8080/workoutAction/start

## getWorkoutSession


