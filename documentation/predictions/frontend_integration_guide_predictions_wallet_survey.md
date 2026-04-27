# frontend_integration_guide_predictions_wallet_survey.md

# Betafit Frontend Integration Guide

## Scope

This is the finalized frontend integration guide for the currently available prediction-market-related backend features.

Target frontend:

- React
- Vite

This guide only covers features that are currently available in the backend.

---

# Base URL

Use:

```text
http://localhost:8080
```

---

# Authentication Rule

All feature endpoints here are session-authenticated.

Always send requests with credentials included.

For `fetch`:

```ts
credentials: "include"
```

Example:

```ts
await fetch("http://localhost:8080/predictions/markets/open", {
  method: "GET",
  credentials: "include"
})
```

---

# JSON Rule

For all `POST` and `PATCH` requests:

```ts
headers: {
  "Content-Type": "application/json"
}
```

---

# Common Response Pattern

## Success

```json
{
  "message": "success"
}
```

plus endpoint-specific payload.

## Error

```json
{
  "error": "Some message"
}
```

Frontend should always:

- parse JSON
- check `res.ok`
- surface backend error text when available

Example helper:

```ts
const API_BASE = "http://localhost:8080";

export async function apiRequest(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || "Request failed");
  }

  return data;
}
```

---

# Feature Availability

## Available now

- create market
- list open markets
- place bet
- list my bets
- list my created markets
- summary endpoint
- completed markets
- leaderboard
- wallet balance
- wallet transactions
- daily reward endpoint
- creator close market
- creator request cancellation
- admin review queue
- admin approve market
- admin reject market
- admin pending settlement queue
- admin settle market
- admin cancel review queue
- admin approve cancel
- admin reject cancel

## Not included in this guide

- market detail endpoint
- any frontend-side admin auth UI logic
- any websocket or live polling layer

---

# Recommended Frontend Types

## PredictionMarket

```ts
export type PredictionMarket = {
  market_id: number
  creator_user_id: number
  creator_name: string
  creator_email: string
  title: string
  goal_text: string
  end_date: string
  status: "open" | "closed" | "settled" | "cancelled"
  review_status: "approved" | "pending" | "rejected"
  reviewed_by_admin_id: number | null
  reviewed_at: string | null
  review_note: string | null
  settlement_result: "yes" | "no" | "cancelled" | null
  settled_by_admin_id: number | null
  settled_at: string | null
  settlement_note: string | null
  cancel_request_status: "none" | "pending" | "approved" | "rejected"
  cancel_request_reason: string | null
  cancel_requested_at: string | null
  cancel_reviewed_by_admin_id: number | null
  cancel_reviewed_at: string | null
  cancel_review_note: string | null
  result: "yes" | "no" | "cancelled" | null
  total_bets: number
  total_points: number
  created_at: string | null
  updated_at: string | null
}
```

## PredictionBet

```ts
export type PredictionBet = {
  prediction_id: number
  market_id: number
  predictor_user_id: number
  prediction_value: "yes" | "no"
  points_wagered: number
  market_title: string | null
  goal_text: string | null
  end_date: string | null
  market_status: string | null
  created_at: string | null
  updated_at: string | null
}
```

## Wallet

```ts
export type Wallet = {
  user_id: number
  balance: number
  created_at: string | null
  updated_at: string | null
}
```

## WalletTransaction

```ts
export type WalletTransaction = {
  txn_id: number
  user_id: number
  delta_points: number
  reason: string
  ref_type: string | null
  ref_id: number | null
  created_at: string | null
  updated_at: string | null
}
```

## PredictionSummary

```ts
export type PredictionSummary = {
  wallet_balance: number
  total_bets_placed: number
  total_markets_created: number
  open_markets_created: number
  completed_markets_participated: number
}
```

## LeaderboardEntry

```ts
export type LeaderboardEntry = {
  rank: number
  user_id: number
  name: string
  balance: number
}
```

---

# Endpoint Guide

## 1. Create market

### Endpoint

```text
POST /predictions/markets
```

### Request body

```json
{
  "title": "Will I hit 10k steps daily?",
  "goal_text": "Goal: 10k steps every day for 1 week.",
  "end_date": "2026-06-01"
}
```

### Frontend notes

- validate title present
- validate goal text present
- validate date format
- validate future date
- after success, market is **pending review**
- do not expect it to appear in `/predictions/markets/open` until approved

### Example

```ts
export async function createMarket(payload: {
  title: string
  goal_text: string
  end_date: string
}) {
  return apiRequest("/predictions/markets", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
```

---

## 2. List open markets

### Endpoint

```text
GET /predictions/markets/open
```

### Frontend notes

- only approved open markets appear here
- pending or rejected markets will not show

### Example

```ts
export async function getOpenMarkets() {
  return apiRequest("/predictions/markets/open", {
    method: "GET"
  });
}
```

### Best use

- public market list
- browse screen
- bet placement entry point

---

## 3. Place bet

### Endpoint

```text
POST /predictions/bets
```

### Request body

```json
{
  "market_id": 13,
  "prediction_value": "yes",
  "points_wagered": 50
}
```

### Frontend notes

- `prediction_value` must be `"yes"` or `"no"`
- `points_wagered` must be positive integer
- disable button while pending
- refresh:
  - wallet
  - my bets
  - open markets
  after success

### Example

```ts
export async function placeBet(payload: {
  market_id: number
  prediction_value: "yes" | "no"
  points_wagered: number
}) {
  return apiRequest("/predictions/bets", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
```

---

## 4. My bets

### Endpoint

```text
GET /predictions/me/bets
```

### Frontend notes

Use for:

- profile screen
- prediction history
- personal participation screen

### Example

```ts
export async function getMyBets() {
  return apiRequest("/predictions/me/bets", {
    method: "GET"
  });
}
```

---

## 5. My markets

### Endpoint

```text
GET /predictions/me/markets
```

### Frontend notes

Use for:

- creator dashboard
- personal market management page

This response includes:

- review status
- cancel status
- settlement state
- bet totals

### Example

```ts
export async function getMyMarkets() {
  return apiRequest("/predictions/me/markets", {
    method: "GET"
  });
}
```

---

## 6. Summary

### Endpoint

```text
GET /predictions/summary
```

### Frontend notes

Use for dashboard cards.

### Example

```ts
export async function getPredictionSummary() {
  return apiRequest("/predictions/summary", {
    method: "GET"
  });
}
```

---

## 7. Completed markets

### Endpoint

```text
GET /predictions/completed
```

### Frontend notes

Use for a completed-history screen.

Possible end states:

- settled yes
- settled no
- cancelled

### Example

```ts
export async function getCompletedMarkets() {
  return apiRequest("/predictions/completed", {
    method: "GET"
  });
}
```

---

## 8. Leaderboard

### Endpoint

```text
GET /predictions/leaderboard
```

### Frontend notes

Use for ranking page or sidebar.

### Example

```ts
export async function getLeaderboard() {
  return apiRequest("/predictions/leaderboard", {
    method: "GET"
  });
}
```

---

## 9. Close my market

### Endpoint

```text
PATCH /predictions/markets/close
```

### Request body

```json
{
  "market_id": 13
}
```

### Frontend notes

Only show close button when creator owns market and market is:

- approved
- open

Hide or disable action for:
- pending
- rejected
- closed
- cancelled
- settled

### Example

```ts
export async function closeMarket(market_id: number) {
  return apiRequest("/predictions/markets/close", {
    method: "PATCH",
    body: JSON.stringify({ market_id })
  });
}
```

---

## 10. Request cancellation

### Endpoint

```text
PATCH /predictions/markets/cancel-request
```

### Request body

```json
{
  "market_id": 15,
  "reason": "Need to withdraw the market."
}
```

### Frontend notes

Only allow this action for creator-owned markets that are:

- approved
- open or closed
- not already settled
- not already pending cancel review

### Example

```ts
export async function requestCancel(market_id: number, reason: string) {
  return apiRequest("/predictions/markets/cancel-request", {
    method: "PATCH",
    body: JSON.stringify({ market_id, reason })
  });
}
```

---

# Wallet

## 11. Wallet balance

### Endpoint

```text
GET /wallet
```

### Frontend notes

Use for:

- navbar points display
- wallet page
- bet modal available balance
- dashboard summary

### Example

```ts
export async function getWallet() {
  return apiRequest("/wallet", {
    method: "GET"
  });
}
```

---

## 12. Wallet transactions

### Endpoint

```text
GET /wallet/transactions
```

### Frontend notes

Use for:

- wallet activity screen
- transaction history table

### Example

```ts
export async function getWalletTransactions() {
  return apiRequest("/wallet/transactions", {
    method: "GET"
  });
}
```

### Render suggestions

Display:

- positive vs negative amount
- reason
- timestamp
- optional reference type

---

# Daily Reward

## 13. Daily reward

### Endpoint

```text
POST /survey/daily/reward
```

### Frontend behavior

This backend trusts the frontend.

That means:

- frontend is responsible for deciding whether the survey was filled
- once survey is filled, frontend calls this endpoint
- backend enforces once-per-day reward

### First success response

```json
{
  "message": "success",
  "reward": {
    "already_awarded": false,
    "points_awarded": 100,
    "new_balance": 240
  }
}
```

### Same-day repeated response

```json
{
  "message": "success",
  "reward": {
    "already_awarded": true,
    "points_awarded": 0
  }
}
```

### Frontend notes

Good UX flow:

1. user completes survey in UI
2. frontend submits or marks survey locally
3. frontend calls `/survey/daily/reward`
4. refresh wallet after success
5. optionally show toast

### Example

```ts
export async function rewardDailySurvey() {
  return apiRequest("/survey/daily/reward", {
    method: "POST"
  });
}
```

---

# Admin Endpoints

These should only be used in admin-only screens.

If called by a non-admin session, expect:

```json
{
  "error": "Forbidden"
}
```

---

## 14. Admin review queue

### Endpoint

```text
GET /admin/predictions/review
```

### Use

List markets waiting for approval.

### Example

```ts
export async function getAdminReviewQueue() {
  return apiRequest("/admin/predictions/review", {
    method: "GET"
  });
}
```

---

## 15. Admin approve market

### Endpoint

```text
PATCH /admin/predictions/approve
```

### Request body

```json
{
  "market_id": 15,
  "admin_action": "Valid market."
}
```

### Example

```ts
export async function approveMarket(market_id: number, admin_action?: string) {
  return apiRequest("/admin/predictions/approve", {
    method: "PATCH",
    body: JSON.stringify({ market_id, admin_action })
  });
}
```

---

## 16. Admin reject market

### Endpoint

```text
PATCH /admin/predictions/reject
```

### Request body

```json
{
  "market_id": 14,
  "admin_action": "Too vague."
}
```

### Example

```ts
export async function rejectMarket(market_id: number, admin_action?: string) {
  return apiRequest("/admin/predictions/reject", {
    method: "PATCH",
    body: JSON.stringify({ market_id, admin_action })
  });
}
```

---

## 17. Pending settlement queue

### Endpoint

```text
GET /admin/predictions/pending-settlement
```

### Use

List approved closed markets that still need settlement.

### Example

```ts
export async function getPendingSettlementQueue() {
  return apiRequest("/admin/predictions/pending-settlement", {
    method: "GET"
  });
}
```

---

## 18. Settle market

### Endpoint

```text
PATCH /admin/predictions/settle
```

### Request body

```json
{
  "market_id": 13,
  "result": "yes",
  "admin_action": "Verified complete."
}
```

### Allowed result values

- `yes`
- `no`
- `cancelled`

### Example

```ts
export async function settleMarket(
  market_id: number,
  result: "yes" | "no" | "cancelled",
  admin_action?: string
) {
  return apiRequest("/admin/predictions/settle", {
    method: "PATCH",
    body: JSON.stringify({ market_id, result, admin_action })
  });
}
```

### Frontend notes

After settlement:
- refresh pending settlement queue
- refresh completed markets
- refresh wallet and leaderboard views if needed

---

## 19. Cancel review queue

### Endpoint

```text
GET /admin/predictions/cancel-review
```

### Use

List markets with `cancel_request_status = pending`.

### Example

```ts
export async function getCancelReviewQueue() {
  return apiRequest("/admin/predictions/cancel-review", {
    method: "GET"
  });
}
```

---

## 20. Approve cancel

### Endpoint

```text
PATCH /admin/predictions/approve-cancel
```

### Request body

```json
{
  "market_id": 15,
  "admin_action": "Approved cancel."
}
```

### Example

```ts
export async function approveCancel(market_id: number, admin_action?: string) {
  return apiRequest("/admin/predictions/approve-cancel", {
    method: "PATCH",
    body: JSON.stringify({ market_id, admin_action })
  });
}
```

### Frontend notes

After success:
- market becomes cancelled
- refresh cancel-review queue
- refresh completed markets

---

## 21. Reject cancel

### Endpoint

```text
PATCH /admin/predictions/reject-cancel
```

### Request body

```json
{
  "market_id": 15,
  "admin_action": "Market should remain active."
}
```

### Example

```ts
export async function rejectCancel(market_id: number, admin_action?: string) {
  return apiRequest("/admin/predictions/reject-cancel", {
    method: "PATCH",
    body: JSON.stringify({ market_id, admin_action })
  });
}
```

---

# Suggested Frontend Screens

## User-facing

### Open Markets Page
Use:
- `GET /predictions/markets/open`
- `GET /wallet`

Actions:
- place bet
- browse markets

### Create Market Page
Use:
- `POST /predictions/markets`

After creation:
- show pending-review state
- redirect to My Markets

### My Markets Page
Use:
- `GET /predictions/me/markets`

Actions:
- close market
- request cancellation

### My Bets Page
Use:
- `GET /predictions/me/bets`

---

### Completed Markets Page
Use:
- `GET /predictions/completed`

---

### Wallet Page
Use:
- `GET /wallet`
- `GET /wallet/transactions`

---

### Daily Survey Reward Hook
Use:
- `POST /survey/daily/reward`

---

### Leaderboard Page
Use:
- `GET /predictions/leaderboard`

---

## Admin-facing

### Review Queue Page
Use:
- `GET /admin/predictions/review`
- `PATCH /admin/predictions/approve`
- `PATCH /admin/predictions/reject`

---

### Pending Settlement Page
Use:
- `GET /admin/predictions/pending-settlement`
- `PATCH /admin/predictions/settle`

---

### Cancel Review Page
Use:
- `GET /admin/predictions/cancel-review`
- `PATCH /admin/predictions/approve-cancel`
- `PATCH /admin/predictions/reject-cancel`

---

# UI State Logic (CRITICAL)

## Market Visibility Rules

### Show in Open Markets
- status = open
- review_status = approved

---

### Show in My Markets
- creator_user_id = current session user

---

### Show in Completed Markets
- status = settled
- OR status = cancelled

---

## Button Visibility Rules

### Place Bet Button
Show ONLY if:
- status = open
- review_status = approved

---

### Close Market Button
Show ONLY if:
- user is creator
- status = open
- review_status = approved

---

### Request Cancel Button
Show ONLY if:
- user is creator
- review_status = approved
- status is open or closed
- settlement_result is null
- cancel_request_status is not pending

---

### Disable All Actions If
- status = cancelled
- OR status = settled
- OR review_status = rejected

---

# Data Refresh Rules (IMPORTANT)

After ANY mutation, refetch dependent data.

---

## After create market
Refetch:
- my markets

---

## After placing bet
Refetch:
- wallet
- my bets
- open markets

---

## After daily reward
Refetch:
- wallet
- wallet transactions

---

## After closing market
Refetch:
- my markets

---

## After cancel request
Refetch:
- my markets

---

## After admin approve/reject
Refetch:
- admin review queue
- open markets (optional)

---

## After admin settlement
Refetch:
- pending settlement queue
- completed markets
- leaderboard
- wallet (optional)

---

## After admin cancel approve/reject
Refetch:
- cancel review queue
- completed markets

---

# Error Handling Rules

Always expect:

```json
{
  "error": "Some message"
}
```

Frontend must:
- display message
- not crash
- not silently ignore

---

## Common Errors

### Unauthorized
```json
{ "error": "Unauthorized" }
```

### Forbidden
```json
{ "error": "Forbidden" }
```

### Validation
```json
{ "error": "market_id is required" }
```

```json
{ "error": "Invalid result value" }
```

```json
{ "error": "Insufficient balance" }
```

---

# Recommended Frontend Structure

## API Layer

```
/api/
  predictions.ts
  wallet.ts
  admin.ts
  survey.ts
```

---

## State Layer

```
/store/
  walletStore.ts
  predictionStore.ts
  adminStore.ts
```

---

## Pages

```
/pages/
  OpenMarkets.tsx
  CreateMarket.tsx
  MyMarkets.tsx
  MyBets.tsx
  CompletedMarkets.tsx
  Wallet.tsx
  Leaderboard.tsx
  AdminReview.tsx
  AdminSettlement.tsx
  AdminCancel.tsx
```

---

# Final Build Order (STRICT)

1. API helper
2. wallet system
3. open markets
4. betting
5. create market
6. my markets
7. my bets
8. completed markets
9. leaderboard
10. daily reward
11. admin review
12. admin settlement
13. admin cancel review

---

# Final Notes

- session-based auth (cookies required)
- backend already validated via curl
- no websocket required
- state transitions are strict
- safe for full frontend implementation

---

# END OF DOCUMENT