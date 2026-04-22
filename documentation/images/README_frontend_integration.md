DOC NAME: documentation/README_frontend_integration.md

# Frontend Integration Guide for New Backend Features

This folder documents the new backend features added for frontend integration.

These docs are focused on:

- new endpoints
- updated response payloads
- image/media handling
- settings/profile photo flows
- progress photo flows
- role update flow for Google-created users
- updated auth/session payload behavior

This documentation is intended for frontend developers integrating against the current backend.

---

## What is covered

### 1. General media upload contract
See:

- `media_uploads_contract.md`

This explains:

- how backend-served media URLs work
- what image URLs look like
- where files end up logically
- how image-uploading endpoints behave

---

### 2. Auth, session, and role updates
See:

- `auth_session_role_contract.md`

This explains:

- `/auth/me`
- `needs_onboarding`
- `/auth/updateRole`
- how Google-created users finish role selection
- what the frontend should do after role update

---

### 3. Shared settings and profile photo upload
See:

- `settings_profile_photo_contract.md`

This explains:

- `GET /auth/settings`
- `PATCH /auth/settings`
- `POST /auth/settings/profile-photo`

---

### 4. Progress photo feature
See:

- `progress_photos_contract.md`

This explains:

- `POST /client/progress-photo`
- `GET /client/progress-photos`

---

### 5. Meal image behavior
See:

- `meal_images_contract.md`

This explains:

- how meal image upload now works through local media
- what `photo_url` looks like
- how to render returned images

---

## Important backend-wide conventions

### Media URLs are backend-relative

Image fields now return values like:

```text
/uploads/profile_photos/user_2/abc.jpg
/uploads/progress_photos/user_2/def.jpg
/uploads/meal_images/user_2/ghi.jpg
```

These are not full external URLs.

Frontend should prepend backend origin when rendering, for example:

```text
http://localhost:8080/uploads/profile_photos/user_2/abc.jpg
```

In production, prepend the deployed backend origin.

---

### Auth is cookie/session based

Authenticated frontend requests must include credentials.

For `fetch`:

```js
fetch(url, {
  credentials: "include"
})
```

For Axios:

```js
axios.get(url, {
  withCredentials: true
})
```

---

### Images are now backend-owned

Frontend should not assume:

- Google Drive URLs
- CDN URLs
- third-party asset hosting

All new image uploads are backend-managed local media.

---

## Recommended frontend implementation order

1. Read `auth_session_role_contract.md`
2. Read `media_uploads_contract.md`
3. Implement `GET /auth/settings`
4. Implement `POST /auth/settings/profile-photo`
5. Implement progress photo upload/list
6. Render meal photo URLs from existing meal APIs

---

## Summary

These docs define the current expected backend contract for all newly implemented media/settings/auth features.

They should be treated as the source of truth for frontend integration of:

- profile photo settings
- progress photos
- onboarding-aware auth state
- role completion after Google signup
- local media URL rendering