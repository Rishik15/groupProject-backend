DOC NAME: documentation/settings_profile_photo_contract.md

# Settings and Profile Photo Contract

## Overview

This document defines the shared account settings API for authenticated users.

These settings endpoints are intentionally separate from onboarding.

They support:

- common account/profile fields
- coach-specific editable settings
- profile photo upload through settings

This applies to both client and coach users.

---

## Endpoints covered

- `GET /auth/settings`
- `PATCH /auth/settings`
- `POST /auth/settings/profile-photo`

---

## GET `/auth/settings`

### Purpose

Returns the current authenticated user's settings payload.

Frontend should use this to populate:

- account/settings page
- editable profile fields
- profile photo preview

---

### Request

```http
GET /auth/settings
```

No request body.

Requires authenticated session.

---

### Success response for client

```json
{
  "message": "success",
  "settings": {
    "dob": "2000-01-01",
    "email": "alex@example.com",
    "first_name": "Alex",
    "goal_weight": 175,
    "height": 70,
    "last_name": "Taylor",
    "phone_number": "555-111-2222",
    "profile_picture": "/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg",
    "role": "client",
    "weight": 180
  }
}
```

---

### Success response for coach

```json
{
  "message": "success",
  "settings": {
    "dob": "1998-05-12",
    "email": "coach@example.com",
    "first_name": "Casey",
    "goal_weight": 160,
    "height": 68,
    "last_name": "Smith",
    "phone_number": "555-000-1111",
    "profile_picture": "/uploads/profile_photos/user_5/abc.jpg",
    "role": "coach",
    "weight": 172,
    "coach_description": "Strength coach focused on sustainable progress.",
    "price": 75
  }
}
```

---

## PATCH `/auth/settings`

### Purpose

Updates editable account settings for the current authenticated user.

This is JSON-based and does not handle file upload.

Use this endpoint for text/numeric settings only.

---

### Request

```http
PATCH /auth/settings
Content-Type: application/json
```

---

### Allowed client fields

```json
{
  "first_name": "Alex",
  "last_name": "Taylor",
  "phone_number": "555-111-2222",
  "dob": "2000-01-01",
  "weight": 180,
  "height": 70,
  "goal_weight": 175
}
```

All fields are optional. Only send what should change.

---

### Additional coach fields

Coach users may also send:

```json
{
  "coach_description": "Online nutrition and training coach",
  "price": 80
}
```

---

### Example request

```json
{
  "phone_number": "555-111-2222",
  "goal_weight": 175
}
```

---

### Success response

```json
{
  "message": "success",
  "settings": {
    "dob": "2000-01-01",
    "email": "alex@example.com",
    "first_name": "Alex",
    "goal_weight": 175,
    "height": 70,
    "last_name": "Taylor",
    "phone_number": "555-111-2222",
    "profile_picture": "/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg",
    "role": "client",
    "weight": 180
  }
}
```

---

## POST `/auth/settings/profile-photo`

### Purpose

Uploads and sets the authenticated user's profile photo.

This is a multipart upload endpoint.

It stores the image through the backend media system and updates:

```text
user_mutables.profile_picture
```

---

### Request

```http
POST /auth/settings/profile-photo
Content-Type: multipart/form-data
```

Form fields:

| Field | Type | Required | Description |
|------|------|----------|-------------|
| photo | file | yes | Image file |

---

### Example request

```bash
curl -X POST http://localhost:8080/auth/settings/profile-photo \
  -b cookiejar.txt \
  -F "photo=@/path/to/profile.jpg"
```

---

### Success response

```json
{
  "message": "success",
  "photo_url": "/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg",
  "settings": {
    "dob": "2000-01-01",
    "email": "alex@example.com",
    "first_name": "Alex",
    "goal_weight": 175,
    "height": 70,
    "last_name": "Taylor",
    "phone_number": "555-111-2222",
    "profile_picture": "/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg",
    "role": "client",
    "weight": 180
  }
}
```

---

## Frontend implementation notes

### Rendering profile picture

Returned value is backend-relative:

```text
/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg
```

Frontend must prepend backend origin when rendering.

---

### Recommended settings page behavior

1. Load settings with:
   - `GET /auth/settings`
2. Populate editable fields
3. Save text/numeric fields with:
   - `PATCH /auth/settings`
4. Upload profile photo with:
   - `POST /auth/settings/profile-photo`
5. Refresh local state from returned `settings` object

---

## Error responses

### Unauthenticated

```json
{
  "error": "Unauthorized"
}
```

### Missing file

```json
{
  "error": "photo file is required"
}
```

### Invalid file type

```json
{
  "error": "uploaded file must be a supported image type"
}
```

---

## Summary

The shared settings API is now the correct backend integration point for:

- account-level editable fields
- coach editable settings
- profile photo upload

It should be treated as the frontend source of truth for the user settings screen.