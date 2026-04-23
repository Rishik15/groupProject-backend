DOC NAME: documentation/meal_images_contract.md

# Meal Images Contract

## Overview

This document explains how meal image handling works after the migration to backend-managed local media.

The frontend meal upload flow remains largely unchanged, but the image URLs are now backend-managed local URLs rather than third-party storage URLs.

---

## Relevant endpoints

- `POST /nutrition/logMeal`
- `POST /nutrition/getLoggedMeals`

---

## POST `/nutrition/logMeal`

### Purpose

Creates a meal log entry and optionally uploads a meal image.

---

### Request

```http
POST /nutrition/logMeal
Content-Type: multipart/form-data
```

---

### Form fields

| Field          | Type   | Required | Description |
|---------------|--------|----------|-------------|
| name          | string | yes      | Meal name |
| eaten_at      | string | yes      | ISO datetime |
| servings      | string | yes      | Integer string |
| notes         | string | no       | Optional notes |
| food_item_ids | string | yes      | JSON array string or supported existing format |
| photo         | file   | no/yes depending on flow | Meal image |

Note: current backend validation should be followed exactly as implemented in the route.

---

### Example request

```bash
curl -X POST http://localhost:8080/nutrition/logMeal \
  -b cookiejar.txt \
  -F "name=Test Meal" \
  -F "eaten_at=2026-04-18T01:40:00" \
  -F "servings=1" \
  -F "notes=neutral media package test" \
  -F "food_item_ids=[1]" \
  -F "photo=@/path/to/image.jpg"
```

---

### Success response

```json
{
  "message": "success",
  "photo_url": "/uploads/meal_images/user_2/579794d5255f4020ae6ca461cd96c9b1.jpg"
}
```

---

## POST `/nutrition/getLoggedMeals`

### Purpose

Returns stored meal log entries, including any saved meal image URL.

---

### Request

```http
POST /nutrition/getLoggedMeals
Content-Type: application/json
```

Body can be empty:

```json
{}
```

or include whatever date filters are currently supported by the route.

---

### Success response example

```json
{
  "message": "success",
  "loggedMeals": [
    {
      "calories": 300,
      "carbs": "50.00",
      "created_at": "2026-04-18T01:42:32",
      "eaten_at": "2026-04-18T01:40:00",
      "fats": "6.00",
      "food_item_id": null,
      "log_id": 11,
      "meal_id": 11,
      "meal_name": "Test Meal 3",
      "notes": "neutral media package test",
      "photo_url": "/uploads/meal_images/user_2/579794d5255f4020ae6ca461cd96c9b1.jpg",
      "protein": "10.00",
      "servings": "1.00",
      "updated_at": "2026-04-18T01:42:32",
      "user_id": 2
    }
  ]
}
```

---

## Frontend rendering rule

When `photo_url` is non-null, prepend backend origin:

```text
http://localhost:8080/uploads/meal_images/user_2/579794d5255f4020ae6ca461cd96c9b1.jpg
```

If `photo_url` is `null`, render no image.

---

## Important migration detail

Meal image URLs are no longer assumed to be Google Drive URLs.

Frontend should not make assumptions like:

- Drive file ID parsing
- Drive thumbnail URLs
- external image host rules

Frontend should treat meal image URLs exactly like any other backend-managed media URL.

---

## Recommended frontend integration behavior

### Upload flow
1. Build `FormData`
2. Include all meal fields
3. Include `photo` if user selected one
4. Submit to `POST /nutrition/logMeal`
5. Use returned `photo_url` for immediate optimistic rendering if needed

### Read flow
1. Call `POST /nutrition/getLoggedMeals`
2. For each item:
   - if `photo_url` exists, render image
   - otherwise render text-only meal entry

---

## Summary

Meal images now use the same backend-managed media system as the newer image features.

Frontend should treat `photo_url` in meal payloads as:

- backend-relative
- renderable after prefixing backend origin
- stable across reloads and restarts
- no longer tied to Google Drive