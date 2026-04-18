# Google Authentication + Google Drive Upload (Current Implementation)

## Overview

This backend supports two independent Google integrations:

1. **Google App Login**
   - Users can sign into the application using their personal Google account.
   - The backend creates or links a user account and issues a session cookie.

2. **Google Drive (Global Upload Storage)**
   - A single shared Google account is connected once.
   - All user-uploaded images are stored in that account’s Google Drive.
   - Users do NOT need to connect their own Google accounts for uploads.

---

## Architecture Summary

### Google App Login

Flow:
1. Frontend redirects user to `/auth/googleLogin/start`
2. User signs in with Google
3. Backend callback verifies identity (ID token)
4. Backend:
   - links existing user OR
   - creates a new user
5. Session cookie is set
6. User is redirected back to frontend

No tokens are stored client-side.

---

### Google Drive Upload (Global Mode)

Flow:
1. An admin connects a Google account via `/auth/googleOauth/start`
2. OAuth tokens (including refresh token) are stored in DB
3. Backend uses this stored credential to upload images
4. Each user gets a folder:

Users/user_<user_id>/

5. Uploaded images return a public Drive URL

---

## Key Backend Routes

### Google Login (App Authentication)

- `GET /auth/googleLogin/start`
- `GET /auth/googleLogin/callback`
- `GET /auth/googleLogin/status`

---

### Google Drive Connection

- `GET /auth/googleOauth/start`
- `GET /auth/googleOauth/callback`
- `GET /auth/googleOauth/status`
- `GET /auth/googleOauth/effectiveStatus`

---

### Nutrition + Upload

- `POST /nutrition/logMeal`
- `POST /nutrition/getLoggedMeals`
- `POST /nutrition/createFoodItem`
- `GET /nutrition/getFoodItems`

---

## Environment Variables

```env
GOOGLE_OAUTH_CLIENT_SECRETS_FILE=/app/client_secret.json

# App login
GOOGLE_LOGIN_REDIRECT_URI=http://localhost:8080/auth/googleLogin/callback
GOOGLE_LOGIN_SCOPES=openid,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/userinfo.profile
GOOGLE_LOGIN_FRONTEND_REDIRECT_URI=http://localhost:5173

# Drive
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8080/auth/googleOauth/callback
GOOGLE_OAUTH_SCOPES=openid,https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/userinfo.email

GOOGLE_DRIVE_ROOT_FOLDER_NAME=Users
GOOGLE_DRIVE_USER_FOLDER_PREFIX=user_

OAUTHLIB_INSECURE_TRANSPORT=1
```
## Database Tables Used

Google Login
* google_user_identity
Google Drive
  * google_drive_oauth_connection

## Behavior Guarantees
* Users do NOT need Google for uploads
* Only one Drive account is required
* Session-based authentication is used
* Frontend never sees OAuth tokens

## Known Limitations
* Drive requires manual initial OAuth connection
* Uses shared account for all user uploads
* Not ideal for production-scale storage
* Public URLs rely on Drive sharing behavior

## Status

This implementation is:

* fully functional
* tested end-to-end
* stable for development and demos


---

