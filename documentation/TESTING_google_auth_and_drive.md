# `backend/TESTING_google_auth_and_drive.md`

```md
# Testing Guide: Google Login + Google Drive Upload

This guide assumes:
- Docker is running
- Backend is available at http://localhost:8080
- Frontend at http://localhost:5173
- curl is used for API testing
- WSL file path is used for image upload

---

## Step 0: Clean State

```bash
rm -f cookies.txt
```

## Step 1: Register User

```bash
curl -i -c cookies.txt -b cookies.txt \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8080/auth/register \
  -d '{"email":"test@example.com","password":"test1234","name":"Test User","role":"client"}'
```

---

## Step 2: Verify Session

```bash
curl -i -c cookies.txt -b cookies.txt \
  http://localhost:8080/auth/me
```

Expected:
```json
{"authenticated":true,...}
```

---

## Step 3: Connect Google Drive (ONE TIME)

Open browser:

```
http://localhost:8080/auth/googleOauth/start
```

Login using shared Google account (e.g. betafit account)

---

## Step 4: Verify Drive Connection

```bash
curl -i -c cookies.txt -b cookies.txt \
  http://localhost:8080/auth/googleOauth/status
```

Expected:
```json
{
  "connected": true,
  "google_email": "...",
  "mode": "global"
}
```

---

## Step 5: Create Food Item

```bash
curl -i -c cookies.txt -b cookies.txt \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8080/nutrition/createFoodItem \
  -d '{
    "name":"Test Meal",
    "calories":500,
    "protein":30,
    "carbs":50,
    "fats":10,
    "image_url":"https://example.com/test.jpg"
  }'
```

---

## Step 6: Upload Meal Image

```bash
curl -i -c cookies.txt -b cookies.txt \
  -X POST http://localhost:8080/nutrition/logMeal \
  -F "name=Meal Upload Test" \
  -F "eaten_at=2026-04-17T19:30:00" \
  -F "servings=1" \
  -F "notes=test upload" \
  -F "food_item_ids=[1]" \
  -F "photo=@/mnt/c/Users/Georg/Pictures/Camera Roll/fullySetUpLab_lab112.JPG"
```

Expected:
```json
{
  "photo_url": "https://drive.google.com/uc?id=...",
  "message": "success"
}
```

---

## Step 7: Fetch Logged Meals

```bash
curl -i -c cookies.txt -b cookies.txt \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8080/nutrition/getLoggedMeals \
  -d '{}'
```

Expected:
```json
{
  "loggedMeals":[
    {
      "photo_url":"https://drive.google.com/uc?id=..."
    }
  ]
}
```

---

## Step 8: Google App Login (Browser Test)

Open incognito:

```
http://localhost:8080/auth/googleLogin/start
```

After login, verify:

```
http://localhost:8080/auth/googleLogin/status
```

Expected:
```json
{
  "auth_provider":"google",
  "authenticated":true
}
```

---

## Success Criteria

All of the following must pass:

- user session works  
- Google Drive connection established  
- image uploads succeed  
- Drive URL returned  
- meals retrieved with correct image URL  
- Google login sets session correctly  

---

## Common Issues

### Scope mismatch
Fix:
- align scopes in `.env`
- ensure both include `openid`

### Token timing error
Fix:
- add `clock_skew_in_seconds=10`

### Upload fails
Check:
- Drive connection exists  
- refresh token stored  
- file path correct  

---

## Status

If all steps pass, the system is fully operational.