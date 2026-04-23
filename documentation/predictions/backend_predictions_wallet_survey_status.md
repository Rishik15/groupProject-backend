# backend_predictions_wallet_survey_status.md

# Betafit Prediction Markets, Wallet, and Daily Reward Backend Status

## Scope

This document reflects the currently completed backend work for the prediction-market-related feature set.

It is written as a backend implementation and testing status document.

This includes:

- completed tasks
- endpoint inventory
- request and response contracts
- backend state expectations
- verified test behavior
- known constraints

---

# Completed Tasks

## Prediction Markets

Completed:

- create prediction market
- list open prediction markets
- list my created markets
- list my bets
- user summary endpoint
- completed markets endpoint
- leaderboard endpoint

## Prediction Review Workflow

Completed:

- newly created markets start as `pending`
- admin review queue exists
- admin approve endpoint exists
- admin reject endpoint exists
- approved markets appear in open markets
- rejected markets become cancelled

## Betting

Completed:

- place prediction bet
- duplicate-bet prevention per user per market
- open-market enforcement
- wallet deduction on bet placement
- transaction logging on bet placement
- atomic write path for wager + transaction

## Wallet

Completed:

- wallet balance endpoint
- wallet transactions endpoint
- wallet auto-creation if missing

## Daily Reward

Completed:

- once-per-day reward endpoint
- reward adds `100` points
- idempotent behavior
- transaction log entry written

## Settlement

Completed:

- pending settlement queue
- admin settlement endpoint
- yes/no/cancelled settlement handling
- no-winner fallback converts to cancelled + refunds
- payout / refund transaction logging
- completed market visibility

## Cancellation Workflow

Completed:

- user cancel request endpoint
- admin cancel review queue
- admin approve cancel endpoint
- admin reject cancel endpoint
- approved cancel sets market to cancelled
- approved cancel refunds bettors if any

---

# Current Prediction Market State Model

## status

Allowed values:

```text
open
closed
settled
cancelled
```

## review_status

Allowed values:

```text
approved
pending
rejected
```

## settlement_result

Allowed values:

```text
yes
no
cancelled
null
```

## cancel_request_status

Allowed values:

```text
none
pending
approved
rejected
```

---

# Endpoint Inventory

## User / General Endpoints

### POST /predictions/markets

Create a new prediction market.

#### Request body

```json
{
  "title": "Will I hit 10k steps daily?",
  "goal_text": "Goal: 10k steps every day for 1 week.",
  "end_date": "2026-06-01"
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 13,
    "creator_user_id": 2,
    "creator_name": "Alex Taylor",
    "creator_email": "alex@example.com",
    "title": "Will I hit 10k steps daily?",
    "goal_text": "Goal: 10k steps every day for 1 week.",
    "end_date": "2026-06-01",
    "status": "open",
    "review_status": "pending",
    "reviewed_by_admin_id": null,
    "reviewed_at": null,
    "review_note": null,
    "settlement_result": null,
    "settled_by_admin_id": null,
    "settled_at": null,
    "settlement_note": null,
    "cancel_request_status": "none",
    "cancel_request_reason": null,
    "cancel_requested_at": null,
    "cancel_reviewed_by_admin_id": null,
    "cancel_reviewed_at": null,
    "cancel_review_note": null,
    "result": null,
    "total_bets": 0,
    "total_points": 0,
    "created_at": "2026-04-23T06:36:58",
    "updated_at": "2026-04-23T06:36:58"
  }
}
```

#### Backend expectations

- session user must exist
- user account must be active
- title required
- goal_text required
- end_date required
- end_date must be `YYYY-MM-DD`
- end_date must be future
- market is created as:
  - `status = open`
  - `review_status = pending`
  - `cancel_request_status = none`

---

### GET /predictions/markets/open

List open markets visible to users.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 2,
      "creator_user_id": 2,
      "creator_name": "Alex Taylor",
      "creator_email": "alex@example.com",
      "title": "Will Sam complete 3 workouts this week?",
      "goal_text": "Goal: 3 logged sessions by 2026-03-08.",
      "end_date": "2026-03-10",
      "status": "open",
      "review_status": "approved",
      "reviewed_by_admin_id": null,
      "reviewed_at": null,
      "review_note": null,
      "settlement_result": null,
      "settled_by_admin_id": null,
      "settled_at": null,
      "settlement_note": null,
      "cancel_request_status": "none",
      "cancel_request_reason": null,
      "cancel_requested_at": null,
      "cancel_reviewed_by_admin_id": null,
      "cancel_reviewed_at": null,
      "cancel_review_note": null,
      "result": null,
      "total_bets": 2,
      "total_points": 25,
      "created_at": "2026-04-23T06:31:32",
      "updated_at": "2026-04-23T06:31:32"
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active
- only returns markets where:
  - `status = open`
  - `review_status = approved`

---

### POST /predictions/bets

Place a bet on an open, approved market.

#### Request body

```json
{
  "market_id": 13,
  "prediction_value": "yes",
  "points_wagered": 50
}
```

#### Success response

```json
{
  "message": "success",
  "bet": {
    "prediction_id": 21,
    "market_id": 13,
    "predictor_user_id": 2,
    "prediction_value": "yes",
    "points_wagered": 50,
    "market_title": "Will I hit 10k steps daily?",
    "goal_text": "Goal: average at least 10k steps daily by 2026-05-15.",
    "end_date": "2026-05-15",
    "market_status": "open",
    "created_at": "2026-04-23T05:54:34",
    "updated_at": "2026-04-23T05:54:34"
  }
}
```

#### Backend expectations

- session user must exist
- user account must be active
- `market_id` required
- `prediction_value` required and must be:
  - `yes`
  - `no`
- `points_wagered` required
- `points_wagered` must be integer
- `points_wagered > 0`
- market must exist
- market must be `open`
- user cannot already have bet on same market
- wallet must contain enough balance
- wallet deduction + prediction insert + txn insert are atomic

#### Transaction side effects

On success:

- `points_wallet.balance -= points_wagered`
- insert into `prediction`
- insert into `points_txn`

---

### GET /predictions/me/bets

List bets placed by authenticated user.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "bets": [
    {
      "prediction_id": 21,
      "market_id": 13,
      "predictor_user_id": 2,
      "prediction_value": "yes",
      "points_wagered": 50,
      "market_title": "Will I hit 10k steps daily?",
      "goal_text": "Goal: average at least 10k steps daily by 2026-05-15.",
      "end_date": "2026-05-15",
      "market_status": "open",
      "created_at": "2026-04-23T05:54:34",
      "updated_at": "2026-04-23T05:54:34"
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active
- ordered newest first

---

### GET /predictions/me/markets

List markets created by authenticated user.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 13,
      "creator_user_id": 2,
      "creator_name": "Alex Taylor",
      "creator_email": "alex@example.com",
      "title": "Will I hit 10k steps daily?",
      "goal_text": "Goal: average at least 10k steps daily by 2026-05-15.",
      "end_date": "2026-05-15",
      "status": "open",
      "review_status": "approved",
      "reviewed_by_admin_id": 4,
      "reviewed_at": "2026-04-23T06:38:37",
      "review_note": "Looks valid.",
      "settlement_result": null,
      "settled_by_admin_id": null,
      "settled_at": null,
      "settlement_note": null,
      "cancel_request_status": "none",
      "cancel_request_reason": null,
      "cancel_requested_at": null,
      "cancel_reviewed_by_admin_id": null,
      "cancel_reviewed_at": null,
      "cancel_review_note": null,
      "result": null,
      "total_bets": 1,
      "total_points": 50,
      "created_at": "2026-04-23T05:45:36",
      "updated_at": "2026-04-23T06:38:37"
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active

---

### GET /predictions/summary

Dashboard summary for authenticated user.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "summary": {
    "wallet_balance": 90,
    "total_bets_placed": 6,
    "total_markets_created": 3,
    "open_markets_created": 2,
    "completed_markets_participated": 0
  }
}
```

#### Backend expectations

- session user must exist
- user account must be active
- wallet auto-created if missing

---

### GET /predictions/completed

List completed prediction markets.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 15,
      "creator_user_id": 2,
      "creator_name": "Alex Taylor",
      "creator_email": "alex@example.com",
      "title": "Will I meal prep all week?",
      "goal_text": "Goal: meal prep for 7 straight days.",
      "end_date": "2026-05-12",
      "status": "cancelled",
      "review_status": "approved",
      "reviewed_by_admin_id": 4,
      "reviewed_at": "2026-04-23T07:12:02",
      "review_note": "Valid market.",
      "settlement_result": "cancelled",
      "settled_by_admin_id": 4,
      "settled_at": "2026-04-23T07:12:15",
      "settlement_note": "Approved cancel.",
      "cancel_request_status": "approved",
      "cancel_request_reason": "Need to withdraw the market.",
      "cancel_requested_at": "2026-04-23T07:12:06",
      "cancel_reviewed_by_admin_id": 4,
      "cancel_reviewed_at": "2026-04-23T07:12:15",
      "cancel_review_note": "Approved cancel.",
      "result": "cancelled",
      "total_bets": 0,
      "total_points": 0,
      "created_at": "2026-04-23T07:11:02",
      "updated_at": "2026-04-23T07:12:15"
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active
- returns markets where:
  - `status = settled`
  - or `status = cancelled`

---

### GET /predictions/leaderboard

Rank active users by wallet balance.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "leaderboard": [
    {
      "rank": 1,
      "user_id": 23,
      "name": "Isabella Lopez",
      "balance": 800
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active
- leaderboard is derived from `points_wallet.balance`

---

### PATCH /predictions/markets/close

Allow creator to close their approved open market.

#### Request body

```json
{
  "market_id": 13
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 13,
    "status": "closed",
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be creator of market
- market must be:
  - `review_status = approved`
  - `status = open`

---

### PATCH /predictions/markets/cancel-request

Allow creator to request cancellation for approved market.

#### Request body

```json
{
  "market_id": 15,
  "reason": "Need to withdraw the market."
}
```

#### Success response

```json
{
  "message": "success",
  "cancel_request": {
    "market_id": 15,
    "status": "pending",
    "reason": "Need to withdraw the market."
  },
  "market": {
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be creator
- reason required
- market must be:
  - `review_status = approved`
  - `status in ('open', 'closed')`
  - `settlement_result IS NULL`
- `cancel_request_status` cannot already be `pending`

---

## Wallet Endpoints

### GET /wallet

Return wallet balance for authenticated user.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "wallet": {
    "user_id": 2,
    "balance": 240,
    "created_at": "2026-04-23T06:17:11",
    "updated_at": "2026-04-23T06:17:41"
  }
}
```

#### Backend expectations

- session user must exist
- user account must be active
- wallet auto-created if missing

---

### GET /wallet/transactions

Return wallet transaction history.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "transactions": [
    {
      "txn_id": 21,
      "user_id": 2,
      "delta_points": 100,
      "reason": "Daily survey reward",
      "ref_type": "daily_survey",
      "ref_id": null,
      "created_at": "2026-04-23T06:17:41",
      "updated_at": "2026-04-23T06:17:41"
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user account must be active
- ordered newest first

---

## Survey Endpoint

### POST /survey/daily/reward

Grant once-daily reward after frontend decides survey is filled.

#### Request body

None.

#### Success response, first call

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

#### Success response, repeated same-day call

```json
{
  "message": "success",
  "reward": {
    "already_awarded": true,
    "points_awarded": 0
  }
}
```

#### Backend expectations

- session user must exist
- user account must be active
- wallet auto-created if missing
- reward is granted only if no `points_txn` row exists today with:
  - `reason = 'Daily survey reward'`

#### Transaction side effects

On first call of the day:

- `points_wallet.balance += 100`
- insert `points_txn`:
  - `delta_points = 100`
  - `reason = 'Daily survey reward'`
  - `ref_type = 'daily_survey'`

---

## Admin Prediction Review Endpoints

### GET /admin/predictions/review

List pending markets awaiting approval.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 13,
      "review_status": "pending",
      "...": "..."
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user must be admin
- returns markets where `review_status = pending`

---

### PATCH /admin/predictions/approve

Approve pending market.

#### Request body

```json
{
  "market_id": 13,
  "admin_action": "Looks valid."
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 13,
    "review_status": "approved",
    "reviewed_by_admin_id": 4,
    "reviewed_at": "2026-04-23T06:38:37",
    "review_note": "Looks valid.",
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be admin
- market must currently be `pending`

---

### PATCH /admin/predictions/reject

Reject pending market.

#### Request body

```json
{
  "market_id": 14,
  "admin_action": "Too vague."
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 14,
    "review_status": "rejected",
    "status": "cancelled",
    "result": "cancelled",
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be admin
- market must currently be `pending`

---

## Admin Settlement Endpoints

### GET /admin/predictions/pending-settlement

List approved closed markets awaiting settlement.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "markets": [
    {
      "market_id": 13,
      "status": "closed",
      "review_status": "approved",
      "settlement_result": null,
      "...": "..."
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user must be admin
- returns markets where:
  - `review_status = approved`
  - `status = closed`
  - `settlement_result IS NULL`

---

### PATCH /admin/predictions/settle

Settle approved closed market.

#### Request body

```json
{
  "market_id": 13,
  "result": "yes",
  "admin_action": "Verified complete."
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 13,
    "status": "settled",
    "settlement_result": "yes",
    "...": "..."
  },
  "result": {
    "result": "yes"
  }
}
```

#### Alternate success response when no winners exist

```json
{
  "message": "success",
  "market": {
    "market_id": 13,
    "status": "cancelled",
    "settlement_result": "cancelled",
    "settlement_note": "No winners found; market cancelled during settlement.",
    "...": "..."
  },
  "result": {
    "result": "cancelled"
  }
}
```

#### Backend expectations

- session user must exist
- user must be admin
- market must be:
  - `review_status = approved`
  - `status = closed`
  - `settlement_result IS NULL`
- result must be:
  - `yes`
  - `no`
  - `cancelled`

#### Transaction side effects

If result is `cancelled`:
- refund every bettor

If result is `yes` or `no`:
- compute winners by `prediction_value`
- if no winners:
  - convert to cancelled
  - refund all
- else:
  - distribute pool proportionally to winners
  - insert payout transactions

---

## Admin Cancel Review Endpoints

### GET /admin/predictions/cancel-review

List pending cancellation requests.

#### Request body

None.

#### Success response

```json
{
  "message": "success",
  "requests": [
    {
      "market_id": 15,
      "cancel_request_status": "pending",
      "cancel_request_reason": "Need to withdraw the market.",
      "...": "..."
    }
  ]
}
```

#### Backend expectations

- session user must exist
- user must be admin
- returns markets where `cancel_request_status = pending`

---

### PATCH /admin/predictions/approve-cancel

Approve cancellation request.

#### Request body

```json
{
  "market_id": 15,
  "admin_action": "Approved cancel."
}
```

#### Success response

```json
{
  "message": "success",
  "market": {
    "market_id": 15,
    "status": "cancelled",
    "settlement_result": "cancelled",
    "cancel_request_status": "approved",
    "cancel_review_note": "Approved cancel.",
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be admin
- market must have `cancel_request_status = pending`

#### Transaction side effects

- refund all bettors if any
- set:
  - `status = cancelled`
  - `settlement_result = cancelled`
  - `cancel_request_status = approved`

---

### PATCH /admin/predictions/reject-cancel

Reject cancellation request.

#### Request body

```json
{
  "market_id": 15,
  "admin_action": "Market should remain active."
}
```

#### Success response

```json
{
  "message": "success",
  "request": {
    "market_id": 15,
    "status": "rejected"
  },
  "market": {
    "...": "..."
  }
}
```

#### Backend expectations

- session user must exist
- user must be admin
- market must have `cancel_request_status = pending`

---

# Testing Convention

## Login must always be included before authenticated tests

Assume database rebuild resets sessions.

Use:

```bash
rm -f cookies.txt

curl -c cookies.txt -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alex@example.com",
    "password": "Rishik@1"
  }'
```

For admin:

```bash
rm -f cookies.txt

curl -c cookies.txt -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jordan@example.com",
    "password": "Rishik@1"
  }'
```

---

# Known Constraints

- `GET /predictions/markets/detail` is not implemented in the currently completed feature set
- payout uses integer division and may leave small undistributed remainder
- daily reward trusts frontend to decide whether survey is filled
- daily reward idempotency currently keys off the `points_txn.reason` string
- open market listing requires approval first
- closed market settlement requires admin action

---

# Completion Summary

All currently implemented and verified feature groups:

- prediction creation
- prediction review
- prediction betting
- wallet balance and history
- once-daily reward
- prediction summaries
- completed markets
- leaderboard
- settlement
- cancellation workflow