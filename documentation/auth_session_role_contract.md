DOC NAME: documentation/auth_session_role_contract.md

# Auth, Session, and Role Contract

## Overview

This document describes the new/updated auth-related backend behavior relevant to frontend integration.

It covers:

- `/auth/me`
- `needs_onboarding`
- `/auth/updateRole`
- Google-created users completing role selection

---

## Auth model

Authentication remains cookie/session based.

Frontend must include credentials on authenticated requests.

### fetch

```js
fetch(url, {
  credentials: "include"
})
```

### Axios

```js
axios.get(url, {
  withCredentials: true
})
```

---

## GET `/auth/me`

### Purpose

Hydrates current authenticated user state.

Frontend should use this to determine:

- whether user is authenticated
- current role
- user identity payload
- whether onboarding is still needed

---

### Request

```http
GET /auth/me
```

No request body.

Must include session credentials.

---

### Success response

```json
{
  "authenticated": true,
  "role": "client",
  "user": {
    "first_name": "Alex",
    "last_name": "Taylor",
    "email": "alex@example.com",
    "profile_picture": "/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg"
  },
  "needs_onboarding": false
}
```

---

### Unauthenticated response

```json
{
  "authenticated": false
}
```

Status:

```text
401 Unauthorized
```

---

## `needs_onboarding`

### Purpose

Allows frontend to route authenticated users correctly.

Frontend should use this to decide:

- onboarding flow
- dashboard/app flow

---

### Logic

#### For `client`
Onboarding is incomplete if any required base fields are missing.

#### For `coach`
Onboarding is incomplete if base fields or coach-specific fields are missing.

Frontend does not need to re-implement this logic. It should trust the backend field:

```json
"needs_onboarding": true
```

or

```json
"needs_onboarding": false
```

---

## POST `/auth/updateRole`

### Purpose

Used when a Google-created session user still needs to choose/set their application role.

This is an extension of registration for an already authenticated user.

---

### Request

```http
POST /auth/updateRole
Content-Type: application/json
```

Body:

```json
{
  "role": "coach"
}
```

Allowed values:

```json
{
  "role": "client"
}
```

or

```json
{
  "role": "coach"
}
```

---

### Behavior

This route:

- uses the currently authenticated session user
- does not create a new user
- ensures role-related DB setup exists
- updates session role
- returns updated auth/user payload

---

### Success response

```json
{
  "authenticated": true,
  "role": "coach",
  "user": {
    "first_name": "George",
    "last_name": "Attallah",
    "email": "user@example.com",
    "profile_picture": null
  },
  "needs_onboarding": true
}
```

---

### Error response: unauthenticated

```json
{
  "error": "Unauthorized"
}
```

---

### Error response: invalid role

```json
{
  "error": "role must be 'client' or 'coach'"
}
```

---

## Frontend usage pattern for Google signup

Recommended flow:

1. User completes Google login
2. Frontend loads authenticated session
3. Frontend detects role is missing or role selection is needed
4. Frontend calls:

```http
POST /auth/updateRole
```

5. Frontend reads returned payload
6. Frontend routes user based on:
   - `role`
   - `needs_onboarding`

---

## Example fetch for role update

```js
const res = await fetch("http://localhost:8080/auth/updateRole", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    role: "coach"
  })
});

const data = await res.json();
```

---

## Recommended frontend state model

```ts
type AuthState = {
  isAuthenticated: boolean;
  role: "client" | "coach" | "admin" | null;
  needsOnboarding: boolean;
  user: {
    first_name: string;
    last_name: string;
    email: string;
    profile_picture: string | null;
  } | null;
};
```

---

## Summary

Frontend should treat `/auth/me` as the primary source of truth for:

- auth state
- role
- onboarding state
- basic user identity

and use `/auth/updateRole` when an already-authenticated user must complete role selection after Google signup.