# Frontend Guide: Google Login + Google Drive Upload

## Overview

This frontend interacts with two backend features:

1. Google app login (authentication)
2. Google Drive image uploads (handled entirely by backend)

The frontend does NOT directly interact with Google APIs.

---

## Google Login Flow

### Step 1: Trigger login

```js
window.location.href = "http://localhost:8080/auth/googleLogin/start";
```

---

### Step 2: User signs into Google

Handled entirely by backend.

---

### Step 3: Backend redirects to frontend

User returns to:

```
http://localhost:5173
```

---

### Step 4: Fetch session

```js
fetch("http://localhost:8080/auth/me", {
  credentials: "include"
})
```

Expected:

```json
{
  "authenticated": true,
  "user": { ... }
}
```

---

## Upload Flow

Frontend does NOT talk to Google.

### Upload request

```js
const formData = new FormData();

formData.append("name", "Meal");
formData.append("eaten_at", "2026-04-17T19:30:00");
formData.append("servings", "1");
formData.append("notes", "test");
formData.append("food_item_ids", JSON.stringify([1]));
formData.append("photo", file);

fetch("http://localhost:8080/nutrition/logMeal", {
  method: "POST",
  body: formData,
  credentials: "include"
});
```

---

### Response

```json
{
  "photo_url": "https://drive.google.com/uc?id=..."
}
```

---

### Rendering image

```jsx
<img src={photo_url} />
```

---

## Important Rules

### ALWAYS include credentials

```js
credentials: "include"
```

Without this:
- session will not persist
- auth will appear broken

---

### DO NOT:

- call Google APIs directly
- handle OAuth tokens in frontend
- attempt to upload to Drive manually
- store Google credentials

---

## Required UI Elements

- Login page:
  - email/password form
  - "Continue with Google" button

- App bootstrap:
  - call `/auth/me`
  - determine auth state

---

## Expected UX

1. User clicks Google login
2. Google login screen appears
3. User signs in
4. User returns to app
5. App automatically recognizes user
6. Upload works without additional steps

---

## Summary

Frontend responsibilities are minimal:

- redirect to backend login
- check session
- upload files
- render returned URLs

All Google complexity is handled by backend.