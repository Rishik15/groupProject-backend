DOC NAME: documentation/media_uploads_contract.md

# Media Uploads Contract

## Overview

This document defines the general backend contract for image/media uploads.

It applies to all backend-managed image uploads introduced in the new implementation, including:

- profile photos
- progress photos
- meal images

---

## Core principle

All uploaded images are:

- stored by the backend
- persisted on backend-owned storage
- served by the backend
- referenced by backend-relative URLs

---

## URL format

All stored media URLs follow this pattern:

```text
/uploads/<category>/user_<user_id>/<filename>
```

### Examples

```text
/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg
/uploads/progress_photos/user_2/2fa19a4b50eb4ecf9dc6b8cbe89d7f22.jpg
/uploads/meal_images/user_2/579794d5255f4020ae6ca461cd96c9b1.jpg
```

---

## Frontend rendering rule

When the backend returns:

```text
/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg
```

frontend should render with backend origin prepended:

```text
http://localhost:8080/uploads/profile_photos/user_2/06b5368cf1e84d29b578e386464e670b.jpg
```

Do not assume the returned value is already a full absolute URL.

---

## Categories currently in use

### Profile photos

```text
profile_photos
```

### Progress photos

```text
progress_photos
```

### Meal images

```text
meal_images
```

---

## Supported image MIME types

Current backend accepts:

```text
image/jpeg
image/png
image/gif
image/webp
```

Frontend should avoid uploading unsupported file types.

---

## Upload request format

Current image-uploading endpoints use:

```text
multipart/form-data
```

with a file field named:

```text
photo
```

---

## Generic request pattern

Example:

```bash
curl -X POST http://localhost:8080/<endpoint> \
  -b cookiejar.txt \
  -F "photo=@/path/to/file.jpg"
```

Some endpoints also accept additional form fields.

---

## Generic success response pattern

Most image upload endpoints return:

```json
{
  "message": "success",
  "photo_url": "/uploads/<category>/user_<id>/<filename>"
}
```

Some endpoints return additional payload fields depending on feature.

---

## Failure behavior

Common image upload failures:

### Missing auth

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

### Empty file

```json
{
  "error": "uploaded file is empty"
}
```

---

## Frontend guidance

### Always use multipart uploads for image endpoints

Do not send JSON for image-upload endpoints.

Use `FormData`.

### Example using fetch

```js
const form = new FormData();
form.append("photo", file);

const res = await fetch("http://localhost:8080/auth/settings/profile-photo", {
  method: "POST",
  body: form,
  credentials: "include"
});
```

---

## Summary

The frontend should treat backend-managed image upload as a consistent system with:

- multipart upload
- file field `photo`
- backend-relative returned `photo_url`
- backend-origin prepending for rendering
- category-based URL organization