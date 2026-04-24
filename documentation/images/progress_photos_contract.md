DOC NAME: documentation/progress_photos_contract.md

# Progress Photos Contract

## Overview

This document defines the backend contract for the progress photo feature.

Progress photos are a historical user-owned media feature.

They are intentionally separate from profile photos.

---

## Why progress photos are separate

Profile photo:
- one current account image
- stored on the user profile

Progress photos:
- many per user
- historical
- optionally captioned
- optionally timestamped
- intended for progress tracking over time

---

## Endpoints covered

- `POST /client/progress-photo`
- `GET /client/progress-photos`

---

## POST `/client/progress-photo`

### Purpose

Uploads a new progress photo for the authenticated client and creates a DB record.

---

### Request

```http
POST /client/progress-photo
Content-Type: multipart/form-data
```

---

### Form fields

| Field   | Type   | Required | Description |
|--------|--------|----------|-------------|
| photo  | file   | yes      | Image file |
| caption | string | no      | Optional text/caption |
| taken_at | string | no     | Optional ISO datetime |

---

### Example request

```bash
curl -X POST http://localhost:8080/client/progress-photo \
  -b cookiejar.txt \
  -F "caption=Front pose week 1" \
  -F "taken_at=2026-04-18T01:50:00" \
  -F "photo=@/path/to/image.jpg"
```

---

### Success response

```json
{
  "message": "success",
  "progress_photo_id": 12,
  "photo_url": "/uploads/progress_photos/user_2/2fa19a4b50eb4ecf9dc6b8cbe89d7f22.jpg"
}
```

---

## GET `/client/progress-photos`

### Purpose

Returns all progress photos for the authenticated client.

Ordered newest first using:

- `taken_at` when present
- otherwise `created_at`

---

### Request

```http
GET /client/progress-photos
```

No request body.

Requires authenticated client session.

---

### Success response

```json
{
  "message": "success",
  "progressPhotos": [
    {
      "progress_photo_id": 12,
      "user_id": 2,
      "photo_url": "/uploads/progress_photos/user_2/2fa19a4b50eb4ecf9dc6b8cbe89d7f22.jpg",
      "caption": "Front pose week 1",
      "taken_at": "2026-04-18T01:50:00",
      "created_at": "2026-04-18T01:52:10",
      "updated_at": "2026-04-18T01:52:10"
    }
  ]
}
```

---

## Data model semantics

Each progress photo is a dedicated record with:

- one image URL
- one user
- optional caption
- optional taken_at timestamp
- standard created/updated timestamps

Frontend should treat this as a historical list, not a single mutable image field.

---

## Image URL behavior

Returned `photo_url` values are backend-relative:

```text
/uploads/progress_photos/user_2/2fa19a4b50eb4ecf9dc6b8cbe89d7f22.jpg
```

Frontend must prepend backend origin for rendering.

---

## Example frontend usage

### Upload

```js
const form = new FormData();
form.append("photo", file);
form.append("caption", "Week 1");
form.append("taken_at", "2026-04-18T01:50:00");

const res = await fetch("http://localhost:8080/client/progress-photo", {
  method: "POST",
  body: form,
  credentials: "include"
});
```

---

### List

```js
const res = await fetch("http://localhost:8080/client/progress-photos", {
  credentials: "include"
});
```

---

## Error responses

### Unauthenticated

```json
{
  "error": "Unauthorized"
}
```

### Wrong role

```json
{
  "error": "Only clients can upload progress photos"
}
```

or

```json
{
  "error": "Only clients can access progress photos"
}
```

### Missing file

```json
{
  "error": "photo file is required"
}
```

---

## Frontend rendering recommendations

Each progress photo item should support:

- image preview
- optional caption
- optional taken-at label
- newest-first ordering
- expandable/lightbox image display if desired

---

## Summary

Progress photos are a dedicated historical image feature.

Frontend should treat them as:

- many-per-user
- chronological
- media-backed
- independent from profile photo settings