# Betafit Prediction Markets Frontend Integration Guide

## Purpose

This document explains how the frontend should integrate with the prediction markets, wallet, and daily survey endpoints.

This guide uses the **exact endpoint names** that must be called by the frontend.

It is written for frontend implementation against the Betafit backend running locally at:

```text
http://localhost:8080
```

---

# Core Rules

## Authentication

All endpoints in this feature set are **session-authenticated**.

The frontend must send requests with credentials so the backend session cookie is included.

For `fetch`, always use:

```js
credentials: "include"
```

Example:

```js
fetch("http://localhost:8080/predictions/markets/open", {
  method: "GET",
  credentials: "include",
})
```

---

## Content Type

For all `POST` and `PATCH` requests, send JSON:

```js
headers: {
  "Content-Type": "application/json"
}
```

---

## Error Handling

The backend pattern is consistent:

### Success

```json
{
  "message": "success",
  "...": "..."
}
```

### Error

```json
{
  "error": "Some message"
}
```

Frontend should always check:

- HTTP status
- presence of `error`
- presence of returned domain object/list

Recommended pattern:

```js
const res = await fetch(url, options)
const data = await res.json()

if (!res.ok) {
  throw new Error(data.error || "Request failed")
}
```

---

## Exact Endpoint Contract

These are the exact endpoints the frontend should use.

### Prediction endpoints

- `GET /predictions/summary`
- `GET /predictions/markets/open`
- `GET /predictions/markets/detail`
- `GET /predictions/completed`
- `GET /predictions/leaderboard`
- `POST /predictions/markets`
- `POST /predictions/bets`
- `PATCH /predictions/markets/close`
- `PATCH /predictions/markets/cancel-request`
- `GET /predictions/me/bets`
- `GET /predictions/me/markets`

### Wallet endpoints

- `GET /wallet`
- `GET /wallet/transactions`

### Daily survey endpoints

- `POST /survey/daily`
- `GET /survey/daily/status`

### Admin prediction review endpoints

- `GET /admin/predictions/review`
- `PATCH /admin/predictions/approve`
- `PATCH /admin/predictions/reject`
- `GET /admin/predictions/pending-settlement`
- `PATCH /admin/predictions/settle`
- `GET /admin/predictions/cancel-review`
- `PATCH /admin/predictions/approve-cancel`
- `PATCH /admin/predictions/reject-cancel`

---

# Feature Overview

## What this feature does

Users can:

- create prediction markets tied to goals
- place point-based bets on markets
- see their own created markets
- see their own bets
- see open and completed markets
- receive daily points from the daily survey
- view their wallet balance and transaction history

Admins can:

- review newly created markets
- approve or reject markets
- review markets ready for settlement
- settle a market as `yes`, `no`, or `cancelled`
- review and approve or reject cancel requests

---

# Frontend Data Models

These are the recommended frontend shapes to use when consuming the API.

## Prediction Market

```ts
type PredictionMarket = {
  market_id: number
  creator_user_id: number
  creator_name?: string
  creator_email?: string
  title: string
  goal_text: string
  end_date: string
  status: "open" | "closed" | "settled" | "cancelled"
  total_bets?: number
  total_points?: number
  created_at?: string
  updated_at?: string
}
```

## Prediction Bet

```ts
type PredictionBet = {
  prediction_id: number
  market_id: number
  predictor_user_id: number
  prediction_value: "yes" | "no"
  points_wagered: number
  created_at?: string
  updated_at?: string
}
```

## Wallet

```ts
type Wallet = {
  user_id: number
  balance: number
  created_at?: string
  updated_at?: string
}
```

## Wallet Transaction

```ts
type WalletTransaction = {
  txn_id: number
  user_id: number
  delta_points: number
  reason: string
  ref_type: string | null
  ref_id: number | null
  created_at?: string
  updated_at?: string
}
```

## Leaderboard Entry

```ts
type LeaderboardEntry = {
  user_id: number
  name: string
  balance: number
  rank?: number
}
```

## Daily Survey Status

```ts
type DailySurveyStatus = {
  already_completed_today: boolean
  reward_points: number
  survey_date?: string
}
```

---

# Endpoint-by-Endpoint Guide

## 1) GET /predictions/markets/open

### Purpose

Get all currently open markets visible to the authenticated user.

### Request

```http
GET /predictions/markets/open
```

### Frontend usage

Use this for:

- open markets page
- home or dashboard prediction section
- selecting a market to bet on

### Example fetch

```js
const res = await fetch("http://localhost:8080/predictions/markets/open", {
  method: "GET",
  credentials: "include",
})

const data = await res.json()
```

### Expected success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 1,
      "creator_user_id": 3,
      "creator_name": "Jane Doe",
      "title": "Lose 10 pounds by June",
      "goal_text": "I will lose 10 pounds before 2026-06-30",
      "end_date": "2026-06-30",
      "status": "open",
      "total_bets": 8,
      "total_points": 340,
      "created_at": "2026-04-23T12:00:00",
      "updated_at": "2026-04-23T12:00:00"
    }
  ]
}
```

### UI notes

Show:

- title
- goal text
- creator
- end date
- current total points
- number of bets
- action button to bet

---

## 2) POST /predictions/markets

### Purpose

Create a new prediction market.

### Request body

```json
{
  "title": "Lose 10 pounds by June",
  "goal_text": "I will lose 10 pounds before 2026-06-30",
  "end_date": "2026-06-30"
}
```

### Required fields

- `title`
- `goal_text`
- `end_date`

### Frontend validation recommendations

Before sending:

- trim strings
- enforce non-empty title
- enforce non-empty goal text
- require `YYYY-MM-DD`
- require future date

### Example fetch

```js
const res = await fetch("http://localhost:8080/predictions/markets", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    title: "Lose 10 pounds by June",
    goal_text: "I will lose 10 pounds before 2026-06-30",
    end_date: "2026-06-30"
  })
})

const data = await res.json()
```

### Expected success response

```json
{
  "message": "success",
  "market": {
    "market_id": 1,
    "creator_user_id": 3,
    "title": "Lose 10 pounds by June",
    "goal_text": "I will lose 10 pounds before 2026-06-30",
    "end_date": "2026-06-30",
    "status": "open",
    "created_at": "2026-04-23T12:00:00",
    "updated_at": "2026-04-23T12:00:00"
  }
}
```

### Common errors

```json
{ "error": "title is required" }
```

```json
{ "error": "goal_text is required" }
```

```json
{ "error": "end_date is required" }
```

```json
{ "error": "end_date must be in YYYY-MM-DD format" }
```

```json
{ "error": "end_date must be in the future" }
```

### UI notes

After success:

- redirect to created market view, or
- refresh open markets list and user markets list

---

## 3) POST /predictions/bets

### Purpose

Place a single bet on a market using wallet points.

### Request body

```json
{
  "market_id": 1,
  "prediction_value": "yes",
  "points_wagered": 50
}
```

### Required fields

- `market_id`
- `prediction_value`
- `points_wagered`

### Allowed values

- `prediction_value` must be `"yes"` or `"no"`

### Frontend validation recommendations

Before sending:

- require numeric market id
- require `"yes"` or `"no"`
- require positive integer `points_wagered`
- do not allow `0` or negative values
- ideally compare against visible wallet balance before submit

### Example fetch

```js
const res = await fetch("http://localhost:8080/predictions/bets", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    market_id: 1,
    prediction_value: "yes",
    points_wagered: 50
  })
})

const data = await res.json()
```

### Expected success response

```json
{
  "message": "success",
  "bet": {
    "prediction_id": 11,
    "market_id": 1,
    "predictor_user_id": 8,
    "prediction_value": "yes",
    "points_wagered": 50,
    "created_at": "2026-04-23T12:30:00",
    "updated_at": "2026-04-23T12:30:00"
  }
}
```

### Common errors

```json
{ "error": "market_id is required" }
```

```json
{ "error": "prediction_value is required" }
```

```json
{ "error": "prediction_value must be 'yes' or 'no'" }
```

```json
{ "error": "points_wagered is required" }
```

```json
{ "error": "points_wagered must be an integer" }
```

```json
{ "error": "points_wagered must be greater than 0" }
```

```json
{ "error": "Insufficient wallet balance" }
```

```json
{ "error": "User has already placed a bet on this market" }
```

```json
{ "error": "Only open markets can accept bets" }
```

### UI notes

After success:

- refresh wallet balance
- refresh market detail or open list
- disable repeat betting on the same market if user bet is now present

---

## 4) GET /predictions/me/bets

### Purpose

Get all bets placed by the authenticated user.

### Request

```http
GET /predictions/me/bets
```

### Use cases

- profile page
- my predictions tab
- betting history page

### Expected success response

```json
{
  "message": "success",
  "bets": [
    {
      "prediction_id": 11,
      "market_id": 1,
      "prediction_value": "yes",
      "points_wagered": 50,
      "created_at": "2026-04-23T12:30:00",
      "market_title": "Lose 10 pounds by June",
      "market_status": "open",
      "end_date": "2026-06-30"
    }
  ]
}
```

### UI notes

Include:

- market title
- user pick
- wager amount
- status badge
- end date
- final outcome if settled

---

## 5) GET /predictions/me/markets

### Purpose

Get all markets created by the authenticated user.

### Request

```http
GET /predictions/me/markets
```

### Use cases

- creator dashboard
- my goals tab
- prediction management page

### Expected success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 1,
      "title": "Lose 10 pounds by June",
      "goal_text": "I will lose 10 pounds before 2026-06-30",
      "end_date": "2026-06-30",
      "status": "open",
      "total_bets": 8,
      "total_points": 340
    }
  ]
}
```

### UI notes

For creator-owned markets, show:

- close market button when allowed
- cancel request button when allowed
- settlement state
- bet volume

---

## 6) GET /predictions/summary

### Purpose

Return a dashboard-style summary for the authenticated user.

### Likely contents

- wallet balance
- total bets placed
- total markets created
- open markets count
- completed markets count
- maybe wins or losses after settlement

### Example response

```json
{
  "message": "success",
  "summary": {
    "wallet_balance": 450,
    "total_bets_placed": 12,
    "total_markets_created": 3,
    "open_markets_created": 1,
    "completed_markets_participated": 4
  }
}
```

### Use cases

- dashboard cards
- summary header above lists

---

## 7) GET /predictions/markets/detail

### Purpose

Return detail for a single market.

### Important note

Because the endpoint contract is fixed as:

```text
GET /predictions/markets/detail
```

the backend still needs a way to identify which market is requested without changing the path. The safest frontend assumption is that the backend will accept a JSON-based identifier or another repo-aligned mechanism under this exact route.

### Recommended request body

```json
{
  "market_id": 1
}
```

### Expected response

```json
{
  "message": "success",
  "market": {
    "market_id": 1,
    "title": "Lose 10 pounds by June",
    "goal_text": "I will lose 10 pounds before 2026-06-30",
    "end_date": "2026-06-30",
    "status": "open",
    "creator_user_id": 3,
    "creator_name": "Jane Doe",
    "total_bets": 8,
    "total_points": 340
  },
  "bets_breakdown": {
    "yes_count": 5,
    "no_count": 3,
    "yes_points": 220,
    "no_points": 120
  },
  "user_bet": {
    "prediction_id": 11,
    "prediction_value": "yes",
    "points_wagered": 50
  }
}
```

### UI notes

This endpoint should power:

- market detail page
- creator management view
- bettor detail modal

---

## 8) PATCH /predictions/markets/close

### Purpose

Allow the market creator to close their own market to further betting.

### Request body

```json
{
  "market_id": 1
}
```

### Expected behavior

- only creator should be able to close
- only open markets should be closable
- closed means no new bets
- market is not yet settled

### Expected success response

```json
{
  "message": "success",
  "market": {
    "market_id": 1,
    "status": "closed"
  }
}
```

### Common errors

```json
{ "error": "Only the market creator can close this market" }
```

```json
{ "error": "Only open markets can be closed" }
```

---

## 9) PATCH /predictions/markets/cancel-request

### Purpose

Allow the creator to request cancellation review.

### Request body

```json
{
  "market_id": 1,
  "reason": "Goal tracking data became invalid"
}
```

### Expected behavior

- creator requests cancellation
- admin later approves or rejects cancel request
- should not instantly cancel market

### Expected success response

```json
{
  "message": "success",
  "cancel_request": {
    "market_id": 1,
    "status": "pending",
    "reason": "Goal tracking data became invalid"
  }
}
```

---

## 10) GET /predictions/completed

### Purpose

Get completed markets visible to the user.

### Completed means

- settled
- cancelled

### Example response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 7,
      "title": "Run 50 miles in April",
      "status": "settled",
      "result": "yes",
      "end_date": "2026-04-20"
    },
    {
      "market_id": 9,
      "title": "Do 30 workouts in April",
      "status": "cancelled",
      "result": "cancelled",
      "end_date": "2026-04-18"
    }
  ]
}
```

### UI notes

Show:

- final result badge
- payout or refund status if user participated

---

## 11) GET /predictions/leaderboard

### Purpose

Show users ranked by point balance or prediction performance.

### Example response

```json
{
  "message": "success",
  "leaderboard": [
    {
      "user_id": 3,
      "name": "Jane Doe",
      "balance": 1200,
      "rank": 1
    },
    {
      "user_id": 5,
      "name": "John Smith",
      "balance": 950,
      "rank": 2
    }
  ]
}
```

### UI notes

Good for:

- community page
- sidebar widget
- gamification screen

---

# Wallet Endpoints

## 12) GET /wallet

### Purpose

Get the authenticated user’s wallet balance.

### Request

```http
GET /wallet
```

### Example response

```json
{
  "message": "success",
  "wallet": {
    "user_id": 8,
    "balance": 450,
    "created_at": "2026-04-23T00:00:00",
    "updated_at": "2026-04-23T12:30:00"
  }
}
```

### UI notes

Use in:

- navbar balance badge
- wallet page
- bet modal
- summary cards

---

## 13) GET /wallet/transactions

### Purpose

Get wallet transaction history.

### Request

```http
GET /wallet/transactions
```

### Example response

```json
{
  "message": "success",
  "transactions": [
    {
      "txn_id": 101,
      "user_id": 8,
      "delta_points": 100,
      "reason": "Daily survey reward",
      "ref_type": "daily_survey",
      "ref_id": 4,
      "created_at": "2026-04-23T09:00:00"
    },
    {
      "txn_id": 102,
      "user_id": 8,
      "delta_points": -50,
      "reason": "Prediction market wager",
      "ref_type": "prediction",
      "ref_id": 11,
      "created_at": "2026-04-23T12:30:00"
    }
  ]
}
```

### UI notes

Render:

- signed amount
- human-readable reason
- timestamp
- maybe color positive or negative
- optional ref link to market detail if `ref_type === "prediction"`

---

# Daily Survey Endpoints

## 14) GET /survey/daily/status

### Purpose

Tell the frontend whether the user already completed today’s daily survey and whether the `100`-point reward is still available.

### Request

```http
GET /survey/daily/status
```

### Example response

```json
{
  "message": "success",
  "status": {
    "already_completed_today": false,
    "reward_points": 100,
    "survey_date": "2026-04-23"
  }
}
```

### UI notes

Use this before showing:

- daily survey modal
- claim reward banner
- disabled state if already completed

---

## 15) POST /survey/daily

### Purpose

Submit the user’s daily wellness survey and award the once-daily `100` points.

### Important product rule

This is tied to the wellness survey. Users should receive:

- `100` points
- only once per day

### Request body

The final payload depends on the survey questions actually used by the app, but the frontend should expect to send the daily wellness fields in JSON.

A likely shape is:

```json
{
  "mood_score": 4,
  "notes": "Feeling good today"
}
```

If the backend later ties this to multiple questions, the payload may expand.

### Example response

```json
{
  "message": "success",
  "survey": {
    "survey_id": 44,
    "survey_date": "2026-04-23",
    "mood_score": 4,
    "notes": "Feeling good today"
  },
  "reward": {
    "points_awarded": 100,
    "new_balance": 550
  }
}
```

### Common errors

```json
{ "error": "Daily survey already completed today" }
```

### Frontend notes

After success:

- refresh wallet
- refresh daily status
- hide claim banner
- show reward confirmation

---

# Admin Endpoints

These should only be called from admin frontend views.

If a non-admin hits them, expect:

```json
{ "error": "Forbidden" }
```

---

## 16) GET /admin/predictions/review

### Purpose

Get newly created markets pending admin review.

### Example response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 1,
      "creator_user_id": 3,
      "title": "Lose 10 pounds by June",
      "goal_text": "I will lose 10 pounds before 2026-06-30",
      "end_date": "2026-06-30",
      "status": "open"
    }
  ]
}
```

### Admin UI notes

Show:

- title
- creator
- full goal text
- end date
- approve and reject actions

---

## 17) PATCH /admin/predictions/approve

### Purpose

Approve a pending market for normal use.

### Request body

```json
{
  "market_id": 1,
  "admin_action": "Approved after review"
}
```

### Expected success response

```json
{
  "message": "success",
  "market": {
    "market_id": 1,
    "status": "open"
  }
}
```

---

## 18) PATCH /admin/predictions/reject

### Purpose

Reject a pending market.

### Request body

```json
{
  "market_id": 1,
  "admin_action": "Rejected due to vague goal"
}
```

### Expected success response

```json
{
  "message": "success",
  "market": {
    "market_id": 1,
    "status": "cancelled"
  }
}
```

---

## 19) GET /admin/predictions/pending-settlement

### Purpose

Get markets that are ready for admin settlement.

### Example response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 7,
      "title": "Run 50 miles in April",
      "status": "closed",
      "end_date": "2026-04-20"
    }
  ]
}
```

### UI notes

Admins should see:

- creator
- title
- yes or no totals
- settlement controls

---

## 20) PATCH /admin/predictions/settle

### Purpose

Settle a closed market with final outcome.

### Request body

```json
{
  "market_id": 7,
  "result": "yes",
  "admin_action": "Verified completed"
}
```

### Allowed result values

- `"yes"`
- `"no"`
- `"cancelled"`

### Expected success response

```json
{
  "message": "success",
  "market": {
    "market_id": 7,
    "status": "settled"
  },
  "result": {
    "result": "yes"
  }
}
```

### UI notes

After settlement:

- refresh pending settlement list
- refresh completed list
- refresh leaderboard and wallet views if visible

---

## 21) GET /admin/predictions/cancel-review

### Purpose

Get cancellation requests awaiting admin decision.

### Example response

```json
{
  "message": "success",
  "requests": [
    {
      "market_id": 9,
      "title": "Do 30 workouts in April",
      "reason": "Tracking data became invalid",
      "status": "pending"
    }
  ]
}
```

---

## 22) PATCH /admin/predictions/approve-cancel

### Purpose

Approve a market cancellation request.

### Request body

```json
{
  "market_id": 9,
  "admin_action": "Cancellation approved"
}
```

### Expected behavior

- market becomes cancelled
- existing wagers are refunded
- wallet transactions are created for refunds

### Example response

```json
{
  "message": "success",
  "market": {
    "market_id": 9,
    "status": "cancelled"
  }
}
```

---

## 23) PATCH /admin/predictions/reject-cancel

### Purpose

Reject a market cancellation request.

### Request body

```json
{
  "market_id": 9,
  "admin_action": "Cancellation rejected"
}
```

### Example response

```json
{
  "message": "success",
  "request": {
    "market_id": 9,
    "status": "rejected"
  }
}
```

---

# Frontend Page Recommendations

## User-facing pages

### Open Markets Page

Use:

- `GET /predictions/markets/open`
- `GET /wallet`

Actions:

- create market
- place bet
- navigate to detail

### My Bets Page

Use:

- `GET /predictions/me/bets`

### My Markets Page

Use:

- `GET /predictions/me/markets`

Actions:

- close market
- request cancel

### Wallet Page

Use:

- `GET /wallet`
- `GET /wallet/transactions`

### Daily Survey Widget or Modal

Use:

- `GET /survey/daily/status`
- `POST /survey/daily`

### Leaderboard Page

Use:

- `GET /predictions/leaderboard`

### Completed Markets Page

Use:

- `GET /predictions/completed`

---

## Admin-facing pages

### Admin Market Review Page

Use:

- `GET /admin/predictions/review`
- `PATCH /admin/predictions/approve`
- `PATCH /admin/predictions/reject`

### Admin Settlement Page

Use:

- `GET /admin/predictions/pending-settlement`
- `PATCH /admin/predictions/settle`

### Admin Cancel Review Page

Use:

- `GET /admin/predictions/cancel-review`
- `PATCH /admin/predictions/approve-cancel`
- `PATCH /admin/predictions/reject-cancel`

---

# Suggested Frontend API Layer

## Example API wrapper

```ts
const API_BASE = "http://localhost:8080"

async function apiRequest(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  })

  const data = await res.json()

  if (!res.ok) {
    throw new Error(data.error || "Request failed")
  }

  return data
}
```

## Example usage

```ts
export async function getOpenMarkets() {
  return apiRequest("/predictions/markets/open", {
    method: "GET"
  })
}

export async function createMarket(payload: {
  title: string
  goal_text: string
  end_date: string
}) {
  return apiRequest("/predictions/markets", {
    method: "POST",
    body: JSON.stringify(payload)
  })
}

export async function placeBet(payload: {
  market_id: number
  prediction_value: "yes" | "no"
  points_wagered: number
}) {
  return apiRequest("/predictions/bets", {
    method: "POST",
    body: JSON.stringify(payload)
  })
}
```

---

# Frontend Validation Checklist

## Create market form

- require title
- require goal text
- require future date
- disable submit while loading

## Bet form

- require yes or no selection
- require positive integer wager
- compare against visible wallet balance
- disable submit after success or while loading

## Daily survey

- check status before rendering reward CTA
- prevent duplicate submit
- refresh wallet after completion

## Admin pages

- show clear action confirmations for approve, reject, settle, and cancel decisions
- refresh list after successful action

---

# UX Recommendations

## Good user feedback

For all mutation endpoints:

- show loading state
- show success toast
- show backend error message directly when safe

## Recommended success messages

- market created successfully
- bet placed successfully
- daily survey submitted, 100 points awarded
- market closed successfully
- cancellation request submitted
- admin action completed

## Recommended error handling

Surface backend messages such as:

- Unauthorized
- Forbidden
- Insufficient wallet balance
- User has already placed a bet on this market
- Daily survey already completed today

---

# Important Integration Notes

## 1) Session cookies are required

If the frontend forgets `credentials: "include"`, authenticated endpoints will fail.

## 2) Route strings must match exactly

Do not change endpoint names in the frontend.

## 3) Use JSON for POST and PATCH

Do not send form data unless the backend explicitly changes to support it.

## 4) Keep status handling strict

Prediction market status values are:

```text
open
closed
settled
cancelled
```

Prediction bet values are:

```text
yes
no
```

Settlement result values are:

```text
yes
no
cancelled
```

## 5) Refresh dependent data after mutations

After a successful mutation, refresh the dependent screens:

- wallet
- relevant market lists
- daily survey status
- leaderboard if needed

---

# Final Recommended Frontend Build Order

## User flow first

1. wallet badge
2. open markets list
3. create market form
4. place bet modal
5. my bets page
6. my markets page
7. daily survey widget
8. completed markets page
9. leaderboard

## Admin flow second

1. review page
2. settlement page
3. cancel review page

---

# Final Notes

This guide is the frontend contract reference for the prediction market feature.

The frontend should code against the exact endpoints listed above and should not invent alternate route names.

If backend implementation details tighten any response shape later, the endpoint names and core behaviors should still remain exactly as documented here.