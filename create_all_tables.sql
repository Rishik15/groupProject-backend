/* =========================================================
   Exercise App - MySQL 8 Schema (Rubric-aligned)
   - Drops/recreates schema
   - Well-commented
   - FKs + sensible cascades / set null
   - created_at / updated_at on EVERY table
   - Audit logging + triggers
   - Basic mock data included
   ========================================================= */

-- -------------------------
-- Schema reset
-- -------------------------
DROP DATABASE IF EXISTS exercise_app;
CREATE DATABASE exercise_app
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE exercise_app;

SET SESSION sql_mode = CONCAT(@@sql_mode, ',STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION');
SET SESSION time_zone = '+00:00';


-- 0) AUDIT TABLES (for tracking key events)

CREATE TABLE audit_event (
  audit_id        INT AUTO_INCREMENT PRIMARY KEY,
  actor_user_id   INT NULL,
  entity_table    VARCHAR(64) NOT NULL,
  entity_pk       VARCHAR(128) NOT NULL,
  action_type     ENUM('INSERT','UPDATE','DELETE','SYSTEM') NOT NULL,
  action_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  details         JSON NULL,

  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_audit_action_at (action_at),
  INDEX idx_audit_entity (entity_table, entity_pk),
  INDEX idx_audit_actor (actor_user_id)
) ENGINE=InnoDB;


-- 1) CORE USER TABLES


/* Immutable PII + identity baseline */
CREATE TABLE users_immutables (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  dob           DATE NULL,
  first_name    VARCHAR(50) NOT NULL,
  last_name     VARCHAR(50) NOT NULL,
  email         VARCHAR(100) NOT NULL,
  phone_number  VARCHAR(20) NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_users_email (email),
  INDEX idx_users_last_first (last_name, first_name)
) ENGINE=InnoDB;

/* Mutable profile fields (1:1 with users_immutables) */
CREATE TABLE user_mutables (
  user_id          INT PRIMARY KEY,
  profile_picture  VARCHAR(255) NULL,
  weight           INT NULL,
  height           INT NULL,
  goal_weight      INT NULL,

  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_user_mutables_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

/* Authentication / credentials (separate from PII where possible) */
CREATE TABLE user_creds (
  user_id        INT PRIMARY KEY,
  username       CHAR(25) NOT NULL,
  password_hash  VARCHAR(255) NOT NULL,
  email          VARCHAR(100) NOT NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_user_creds_username (username),
  UNIQUE KEY uq_user_creds_email (email),

  CONSTRAINT fk_user_creds_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

/* Coaches are users (1:1) */
CREATE TABLE coach (
  coach_id           INT PRIMARY KEY,
  coach_description  TEXT NULL,
  price              DECIMAL(10,2) NOT NULL DEFAULT 0.00,

  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_coach_user
    FOREIGN KEY (coach_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_coach_price (price)
) ENGINE=InnoDB;

/* Admins are users (1:1) */
CREATE TABLE admin (
  admin_id     INT PRIMARY KEY,

  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_admin_user
    FOREIGN KEY (admin_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

/* Coach certifications */
CREATE TABLE certifications (
  cert_id        INT AUTO_INCREMENT PRIMARY KEY,
  coach_id       INT NOT NULL,
  cert_name      VARCHAR(120) NOT NULL,
  provider_name  VARCHAR(120) NULL,
  description    TEXT NULL,
  issued_date    DATE NULL,
  expires_date   DATE NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_certs_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_certs_coach (coach_id),
  INDEX idx_certs_dates (issued_date, expires_date)
) ENGINE=InnoDB;


-- 2) CALENDAR / PLANNING


/* Calendar day helper table */
CREATE TABLE calendar (
  calendar_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  full_date    DATE NOT NULL,
  day_name     ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,

  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_calendar_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_calendar_user_date (user_id, full_date),
  INDEX idx_calendar_date (full_date),
  INDEX idx_calendar_user (user_id)
) ENGINE=InnoDB;


-- 3) WORKOUTS


CREATE TABLE workout_plan (
  plan_id      INT AUTO_INCREMENT PRIMARY KEY,
  plan_name    VARCHAR(120) NOT NULL,

  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_workout_plan_name (plan_name)
) ENGINE=InnoDB;

CREATE TABLE exercise (
  exercise_id    INT AUTO_INCREMENT PRIMARY KEY,
  exercise_name  VARCHAR(120) NOT NULL,
  equipment      VARCHAR(120) NULL,
  video_url      VARCHAR(255) NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_exercise_name (exercise_name),
  INDEX idx_exercise_equipment (equipment)
) ENGINE=InnoDB;

/* Plan -> Exercise ordering + goals (junction) */
CREATE TABLE plan_exercise (
  plan_id          INT NOT NULL,
  exercise_id      INT NOT NULL,
  order_in_workout INT NOT NULL DEFAULT 1,
  sets_goal        INT NULL,
  reps_goal        INT NULL,
  weight_goal      DECIMAL(10,2) NULL,

  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (plan_id, exercise_id),

  CONSTRAINT fk_plan_exercise_plan
    FOREIGN KEY (plan_id) REFERENCES workout_plan(plan_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_plan_exercise_exercise
    FOREIGN KEY (exercise_id) REFERENCES exercise(exercise_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  INDEX idx_plan_exercise_order (plan_id, order_in_workout),
  INDEX idx_plan_exercise_exercise (exercise_id)
) ENGINE=InnoDB;

/* User events (optionally tied to workout plan) */
CREATE TABLE event (
  event_id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id           INT NOT NULL,
  event_date        DATE NOT NULL,
  start_time        TIME NULL,
  end_time          TIME NULL,
  event_type        ENUM('workout','meal','coach_session','reminder','other') NOT NULL DEFAULT 'other',
  description       TEXT NULL,
  workout_plan_id   INT NULL,

  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_event_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_event_workout_plan
    FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_event_user_date (user_id, event_date),
  INDEX idx_event_date (event_date),
  INDEX idx_event_type (event_type),
  INDEX idx_event_plan (workout_plan_id)
) ENGINE=InnoDB;


-- 4) MEALS / NUTRITION


CREATE TABLE meal (
  meal_id     INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(120) NOT NULL,
  calories    INT NOT NULL DEFAULT 0,
  protein     DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  carbs       DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  fats        DECIMAL(7,2) NOT NULL DEFAULT 0.00,

  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uq_meal_name (name),
  INDEX idx_meal_calories (calories)
) ENGINE=InnoDB;

/* User-created food items (custom entries) */
CREATE TABLE food_item (
  food_item_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  name          VARCHAR(120) NOT NULL,
  calories      INT NOT NULL DEFAULT 0,
  protein       DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  carbs         DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  fats          DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  image_url     VARCHAR(255) NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_food_item_creator
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_food_item_user_name (user_id, name),
  INDEX idx_food_item_user (user_id)
) ENGINE=InnoDB;

CREATE TABLE meal_plan (
  meal_plan_id    INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  plan_name       VARCHAR(120) NOT NULL,
  start_date      DATE NULL,
  end_date        DATE NULL,
  total_calories  INT NULL,

  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_meal_plan_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_meal_plan_user_name (user_id, plan_name),
  INDEX idx_meal_plan_user (user_id),
  INDEX idx_meal_plan_dates (start_date, end_date)
) ENGINE=InnoDB;

/* Meal plan items (junction) */
CREATE TABLE user_meal (
  meal_id        INT NOT NULL,
  meal_plan_id   INT NOT NULL,
  meal_type      ENUM('breakfast','lunch','dinner','snack') NOT NULL,
  servings       DECIMAL(6,2) NOT NULL DEFAULT 1.00,
  day_of_week    ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (meal_id, meal_plan_id),

  CONSTRAINT fk_user_meal_meal
    FOREIGN KEY (meal_id) REFERENCES meal(meal_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT fk_user_meal_meal_plan
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(meal_plan_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_user_meal_plan (meal_plan_id),
  INDEX idx_user_meal_type (meal_type),
  INDEX idx_user_meal_dow (day_of_week)
) ENGINE=InnoDB;

/* Actual consumption log */
CREATE TABLE meal_log (
  log_id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  meal_id       INT NULL,
  food_item_id  INT NULL,
  eaten_at      DATETIME NOT NULL,
  servings      DECIMAL(6,2) NOT NULL DEFAULT 1.00,
  notes         TEXT NULL,
  photo_url     VARCHAR(255) NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_meal_log_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_meal_log_meal
    FOREIGN KEY (meal_id) REFERENCES meal(meal_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT fk_meal_log_food_item
    FOREIGN KEY (food_item_id) REFERENCES food_item(food_item_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_meal_log_user_time (user_id, eaten_at),
  INDEX idx_meal_log_time (eaten_at),
  INDEX idx_meal_log_meal (meal_id),
  INDEX idx_meal_log_food_item (food_item_id)
) ENGINE=InnoDB;


-- 5) COACHING / CONTRACTS / AVAILABILITY


CREATE TABLE user_coach_contract (
  contract_id    INT AUTO_INCREMENT PRIMARY KEY,
  coach_id       INT NOT NULL,
  user_id        INT NOT NULL,
  agreed_price   DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  start_date     DATE NOT NULL,
  end_date       DATE NULL,
  contract_text  TEXT NULL,
  active         TINYINT(1) NOT NULL DEFAULT 1,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_contract_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_contract_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_contract_coach (coach_id),
  INDEX idx_contract_user (user_id),
  INDEX idx_contract_active (active),
  INDEX idx_contract_dates (start_date, end_date)
) ENGINE=InnoDB;

CREATE TABLE coach_availability (
  availability_id  INT AUTO_INCREMENT PRIMARY KEY,
  coach_id         INT NOT NULL,
  day_of_week      ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
  start_time       TIME NOT NULL,
  end_time         TIME NOT NULL,
  recurring        TINYINT(1) NOT NULL DEFAULT 1,
  active           TINYINT(1) NOT NULL DEFAULT 1,

  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_availability_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_availability_coach (coach_id),
  INDEX idx_availability_dow (day_of_week),
  INDEX idx_availability_active (active)
) ENGINE=InnoDB;

CREATE TABLE coach_time_off (
  time_off_id  INT AUTO_INCREMENT PRIMARY KEY,
  coach_id     INT NOT NULL,
  start_dt     DATETIME NOT NULL,
  end_dt       DATETIME NOT NULL,
  reason       VARCHAR(255) NULL,

  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_time_off_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_time_off_coach (coach_id),
  INDEX idx_time_off_range (start_dt, end_dt)
) ENGINE=InnoDB;

CREATE TABLE coach_client_note (
  note_id         INT AUTO_INCREMENT PRIMARY KEY,
  coach_id        INT NOT NULL,
  client_user_id  INT NOT NULL,
  note_text       TEXT NOT NULL,
  private         TINYINT(1) NOT NULL DEFAULT 1,

  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_client_note_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_client_note_user
    FOREIGN KEY (client_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_client_note_coach (coach_id),
  INDEX idx_client_note_user (client_user_id),
  INDEX idx_client_note_private (private)
) ENGINE=InnoDB;


-- 6) ASSIGNMENTS / TEMPLATES


CREATE TABLE workout_plan_template (
  template_id      INT AUTO_INCREMENT PRIMARY KEY,
  plan_id          INT NOT NULL,
  author_user_id   INT NOT NULL,
  is_public        TINYINT(1) NOT NULL DEFAULT 0,
  description      TEXT NULL,

  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_template_plan
    FOREIGN KEY (plan_id) REFERENCES workout_plan(plan_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_template_author
    FOREIGN KEY (author_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_template_public (is_public),
  INDEX idx_template_author (author_user_id),
  INDEX idx_template_plan (plan_id)
) ENGINE=InnoDB;

CREATE TABLE coach_assignment_log (
  assignment_id     INT AUTO_INCREMENT PRIMARY KEY,
  coach_id          INT NOT NULL,
  user_id           INT NOT NULL,
  assigned_type     ENUM('workout_plan','meal_plan','template') NOT NULL,
  workout_plan_id   INT NULL,
  meal_plan_id      INT NULL,
  template_id       INT NULL,
  assigned_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note              TEXT NULL,

  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_assignment_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_assignment_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_assignment_workout_plan
    FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT fk_assignment_meal_plan
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(meal_plan_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT fk_assignment_template
    FOREIGN KEY (template_id) REFERENCES workout_plan_template(template_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_assignment_coach (coach_id),
  INDEX idx_assignment_user (user_id),
  INDEX idx_assignment_type (assigned_type),
  INDEX idx_assignment_time (assigned_at)
) ENGINE=InnoDB;


-- 7) MESSAGING


CREATE TABLE conversation (
  conversation_id    INT AUTO_INCREMENT PRIMARY KEY,
  conversation_type  ENUM('dm','group') NOT NULL,
  created_by         INT NOT NULL,
  title              VARCHAR(120) NULL,

  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_conversation_creator
    FOREIGN KEY (created_by) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_conversation_type (conversation_type),
  INDEX idx_conversation_creator (created_by)
) ENGINE=InnoDB;

CREATE TABLE conversation_member (
  conversation_id  INT NOT NULL,
  user_id          INT NOT NULL,
  joined_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  role             ENUM('member','admin','owner') NOT NULL DEFAULT 'member',

  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (conversation_id, user_id),

  CONSTRAINT fk_conv_member_conversation
    FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_conv_member_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_conv_member_user (user_id),
  INDEX idx_conv_member_joined (joined_at)
) ENGINE=InnoDB;

CREATE TABLE message (
  message_id        INT AUTO_INCREMENT PRIMARY KEY,
  conversation_id   INT NOT NULL,
  sender_user_id    INT NOT NULL,
  content           TEXT NOT NULL,
  sent_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  edited_at         DATETIME NULL,
  deleted_at        DATETIME NULL,

  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_message_conversation
    FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_message_sender
    FOREIGN KEY (sender_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_message_conv_time (conversation_id, sent_at),
  INDEX idx_message_sender_time (sender_user_id, sent_at),
  INDEX idx_message_deleted (deleted_at)
) ENGINE=InnoDB;

-- 8) REVIEWS / REPORTS / MODERATION


CREATE TABLE coach_review (
  review_id          INT AUTO_INCREMENT PRIMARY KEY,
  coach_id           INT NOT NULL,
  reviewer_user_id   INT NOT NULL,
  rating             TINYINT NOT NULL,
  review_text        TEXT NULL,

  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_review_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_review_reviewer
    FOREIGN KEY (reviewer_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_review_unique (coach_id, reviewer_user_id),
  INDEX idx_review_coach (coach_id),
  INDEX idx_review_rating (rating)
) ENGINE=InnoDB;

CREATE TABLE user_report (
  report_id              INT AUTO_INCREMENT PRIMARY KEY,
  reported_user_id       INT NOT NULL,
  reporter_user_id       INT NOT NULL,
  reason                 TEXT NOT NULL,
  status                 ENUM('open','reviewing','resolved','dismissed') NOT NULL DEFAULT 'open',
  admin_action           TEXT NULL,
  resolved_by_admin_id   INT NULL,

  created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_report_reported
    FOREIGN KEY (reported_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_report_reporter
    FOREIGN KEY (reporter_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_report_resolved_admin
    FOREIGN KEY (resolved_by_admin_id) REFERENCES admin(admin_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_report_status (status),
  INDEX idx_report_reported (reported_user_id),
  INDEX idx_report_reporter (reporter_user_id),
  INDEX idx_report_created (created_at)
) ENGINE=InnoDB;


-- 9) WORKOUT TRACKING / METRICS


CREATE TABLE workout_session (
  session_id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id           INT NOT NULL,
  started_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at          DATETIME NULL,
  workout_plan_id   INT NULL,
  notes             TEXT NULL,

  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_session_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_session_plan
    FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_session_user_time (user_id, started_at),
  INDEX idx_session_plan (workout_plan_id)
) ENGINE=InnoDB;

CREATE TABLE exercise_set_log (
  set_log_id     INT AUTO_INCREMENT PRIMARY KEY,
  session_id     INT NOT NULL,
  exercise_id    INT NOT NULL,
  set_number     INT NOT NULL,
  reps           INT NULL,
  weight         DECIMAL(10,2) NULL,
  rpe            DECIMAL(4,2) NULL,
  performed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_setlog_session
    FOREIGN KEY (session_id) REFERENCES workout_session(session_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_setlog_exercise
    FOREIGN KEY (exercise_id) REFERENCES exercise(exercise_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  INDEX idx_setlog_session (session_id),
  INDEX idx_setlog_exercise (exercise_id),
  INDEX idx_setlog_time (performed_at)
) ENGINE=InnoDB;

CREATE TABLE cardio_log (
  cardio_log_id  INT AUTO_INCREMENT PRIMARY KEY,
  session_id     INT NULL,
  user_id        INT NOT NULL,
  performed_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  steps          INT NULL,
  distance_km    DECIMAL(10,3) NULL,
  duration_min   INT NULL,
  calories       INT NULL,
  avg_hr         INT NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_cardio_session
    FOREIGN KEY (session_id) REFERENCES workout_session(session_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  CONSTRAINT fk_cardio_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_cardio_user_time (user_id, performed_at),
  INDEX idx_cardio_time (performed_at),
  INDEX idx_cardio_session (session_id)
) ENGINE=InnoDB;

CREATE TABLE daily_metrics (
  metrics_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id        INT NOT NULL,
  metric_date    DATE NOT NULL,
  weight         DECIMAL(7,2) NULL,
  sleep_hours    DECIMAL(4,2) NULL,
  resting_hr     INT NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_metrics_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_metrics_user_date (user_id, metric_date),
  INDEX idx_metrics_date (metric_date)
) ENGINE=InnoDB;


-- 10) MENTAL WELLNESS SURVEYS


CREATE TABLE mental_wellness_survey (
  survey_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  survey_date   DATE NOT NULL,
  mood_score    TINYINT NULL,
  notes         TEXT NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_mws_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_mws_user_date (user_id, survey_date),
  INDEX idx_mws_date (survey_date)
) ENGINE=InnoDB;

CREATE TABLE survey_question (
  question_id     INT AUTO_INCREMENT PRIMARY KEY,
  prompt          TEXT NOT NULL,
  question_type   ENUM('text','scale','multi_choice','yes_no') NOT NULL DEFAULT 'text',
  active          TINYINT(1) NOT NULL DEFAULT 1,

  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_question_active (active),
  INDEX idx_question_type (question_type)
) ENGINE=InnoDB;

CREATE TABLE survey_response (
  response_id    INT AUTO_INCREMENT PRIMARY KEY,
  question_id    INT NOT NULL,
  user_id        INT NOT NULL,
  response_date  DATE NOT NULL,
  answer_text    TEXT NULL,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_response_question
    FOREIGN KEY (question_id) REFERENCES survey_question(question_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_response_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_response_user_date (user_id, response_date),
  INDEX idx_response_question (question_id),
  UNIQUE KEY uq_response_unique (question_id, user_id, response_date)
) ENGINE=InnoDB;


-- 11) POINTS + PREDICTION MARKET


CREATE TABLE points_wallet (
  user_id      INT PRIMARY KEY,
  balance      INT NOT NULL DEFAULT 0,

  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_wallet_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_wallet_balance (balance)
) ENGINE=InnoDB;

CREATE TABLE points_txn (
  txn_id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  delta_points  INT NOT NULL,
  reason        VARCHAR(255) NOT NULL,
  ref_type      VARCHAR(50) NULL,
  ref_id        INT NULL,

  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_points_txn_user
    FOREIGN KEY (user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_points_txn_user (user_id),
  INDEX idx_points_txn_created (created_at),
  INDEX idx_points_txn_ref (ref_type, ref_id)
) ENGINE=InnoDB;

CREATE TABLE prediction_market (
  market_id         INT AUTO_INCREMENT PRIMARY KEY,
  creator_user_id   INT NOT NULL,
  title             VARCHAR(200) NOT NULL,
  goal_text         TEXT NOT NULL,
  end_date          DATE NOT NULL,
  status            ENUM('open','closed','settled','cancelled') NOT NULL DEFAULT 'open',

  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_market_creator
    FOREIGN KEY (creator_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  INDEX idx_market_status (status),
  INDEX idx_market_end_date (end_date),
  INDEX idx_market_creator (creator_user_id)
) ENGINE=InnoDB;

CREATE TABLE prediction (
  prediction_id       INT AUTO_INCREMENT PRIMARY KEY,
  market_id           INT NOT NULL,
  predictor_user_id   INT NOT NULL,
  prediction_value    ENUM('yes','no') NOT NULL,
  points_wagered      INT NOT NULL DEFAULT 0,

  created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_prediction_market
    FOREIGN KEY (market_id) REFERENCES prediction_market(market_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_prediction_user
    FOREIGN KEY (predictor_user_id) REFERENCES users_immutables(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_prediction_once (market_id, predictor_user_id),
  INDEX idx_prediction_market (market_id),
  INDEX idx_prediction_user (predictor_user_id),
  INDEX idx_prediction_value (prediction_value)
) ENGINE=InnoDB;


-- 12) LANDING / FEATURES / SHOWCASE


CREATE TABLE landing_testimonial (
  testimonial_id       INT AUTO_INCREMENT PRIMARY KEY,
  before_after_story   TEXT NULL,
  text                TEXT NOT NULL,
  rating              TINYINT NULL,
  display_order        INT NOT NULL DEFAULT 0,

  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_testimonial_order (display_order),
  INDEX idx_testimonial_rating (rating)
) ENGINE=InnoDB;

CREATE TABLE progress_showcase_media (
  media_id        INT AUTO_INCREMENT PRIMARY KEY,
  media_url       VARCHAR(255) NOT NULL,
  media_type      ENUM('image','video') NOT NULL,
  testimonial_id  INT NULL,

  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_media_testimonial
    FOREIGN KEY (testimonial_id) REFERENCES landing_testimonial(testimonial_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE,

  INDEX idx_media_type (media_type),
  INDEX idx_media_testimonial (testimonial_id)
) ENGINE=InnoDB;

CREATE TABLE feature (
  feature_id     INT AUTO_INCREMENT PRIMARY KEY,
  title          VARCHAR(120) NOT NULL,
  description    TEXT NULL,
  icon           VARCHAR(120) NULL,
  display_order  INT NOT NULL DEFAULT 0,
  active         TINYINT(1) NOT NULL DEFAULT 1,

  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_feature_active (active),
  INDEX idx_feature_order (display_order)
) ENGINE=InnoDB;

CREATE TABLE coach_featured (
  coach_featured_id  INT AUTO_INCREMENT PRIMARY KEY,
  coach_id           INT NOT NULL,
  display_order      INT NOT NULL DEFAULT 0,
  start_date         DATE NULL,
  end_date           DATE NULL,
  active             TINYINT(1) NOT NULL DEFAULT 1,

  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_coach_featured_coach
    FOREIGN KEY (coach_id) REFERENCES coach(coach_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  UNIQUE KEY uq_featured_coach_active (coach_id, active),
  INDEX idx_featured_order (display_order),
  INDEX idx_featured_active (active),
  INDEX idx_featured_dates (start_date, end_date)
) ENGINE=InnoDB;


-- 13) AUDIT TRIGGERS (key tables)

DELIMITER $$

/* users_immutables audit */
CREATE TRIGGER trg_users_immutables_ins
AFTER INSERT ON users_immutables
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'users_immutables', CAST(NEW.user_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('email', NEW.email, 'first_name', NEW.first_name, 'last_name', NEW.last_name));
END$$

CREATE TRIGGER trg_users_immutables_upd
AFTER UPDATE ON users_immutables
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'users_immutables', CAST(NEW.user_id AS CHAR), 'UPDATE', NOW(),
          JSON_OBJECT('old_email', OLD.email, 'new_email', NEW.email));
END$$

CREATE TRIGGER trg_users_immutables_del
AFTER DELETE ON users_immutables
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (OLD.user_id, 'users_immutables', CAST(OLD.user_id AS CHAR), 'DELETE', NOW(),
          JSON_OBJECT('email', OLD.email));
END$$

/* message audit (write-level tracking) */
CREATE TRIGGER trg_message_ins
AFTER INSERT ON message
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.sender_user_id, 'message', CAST(NEW.message_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('conversation_id', NEW.conversation_id, 'sent_at', NEW.sent_at));
END$$

CREATE TRIGGER trg_message_upd
AFTER UPDATE ON message
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.sender_user_id, 'message', CAST(NEW.message_id AS CHAR), 'UPDATE', NOW(),
          JSON_OBJECT('edited_at', NEW.edited_at, 'deleted_at', NEW.deleted_at));
END$$

/* points_txn audit */
CREATE TRIGGER trg_points_txn_ins
AFTER INSERT ON points_txn
FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'points_txn', CAST(NEW.txn_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('delta_points', NEW.delta_points, 'reason', NEW.reason, 'ref_type', NEW.ref_type, 'ref_id', NEW.ref_id));
END$$

DELIMITER ;


-- 14) BASIC MOCK DATA (utility seed)


/* Users */
INSERT INTO users_immutables (dob, first_name, last_name, email, phone_number)
VALUES
  ('2000-01-01','Alex','Taylor','alex@example.com','555-1000'),
  ('1998-06-15','Sam','Nguyen','sam@example.com','555-2000'),
  ('1995-11-20','Jordan','Patel','jordan@example.com','555-3000');

/* Mutables */
INSERT INTO user_mutables (user_id, profile_picture, weight, height, goal_weight)
VALUES
  (1,'https://cdn.example.com/pfp/alex.png',180,70,170),
  (2,'https://cdn.example.com/pfp/sam.png',150,66,145),
  (3,NULL,210,72,190);

/* Credentials */
INSERT INTO user_creds (user_id, username, password_hash, email)
VALUES
  (1,'alex_t','hash_abc123','alex@example.com'),
  (2,'sam_n','hash_def456','sam@example.com'),
  (3,'jordan_p','hash_ghi789','jordan@example.com');

/* Coach + Admin */
INSERT INTO coach (coach_id, coach_description, price)
VALUES
  (2,'Certified coach focusing on strength + habit building.',75.00);

INSERT INTO admin (admin_id) VALUES (3);

/* Certifications */
INSERT INTO certifications (coach_id, cert_name, provider_name, description, issued_date, expires_date)
VALUES
  (2,'CPT','NASM','Certified Personal Trainer','2022-01-01','2026-01-01'),
  (2,'Nutrition Coach','Precision Nutrition','Nutrition coaching fundamentals','2023-05-01',NULL);

/* Calendar samples */
INSERT INTO calendar (user_id, full_date, day_name)
VALUES
  (1,'2026-03-01','Sun'),
  (1,'2026-03-02','Mon'),
  (2,'2026-03-02','Mon');

/* Workout plan + exercises */
INSERT INTO workout_plan (plan_name) VALUES ('Beginner Full Body A'), ('Upper/Lower Split');

INSERT INTO exercise (exercise_name, equipment, video_url)
VALUES
  ('Push-Up','Bodyweight','https://video.example.com/pushup'),
  ('Goblet Squat','Dumbbell','https://video.example.com/goblet_squat'),
  ('Lat Pulldown','Machine','https://video.example.com/lat_pulldown');

INSERT INTO plan_exercise (plan_id, exercise_id, order_in_workout, sets_goal, reps_goal, weight_goal)
VALUES
  (1,1,1,3,10,NULL),
  (1,2,2,3,12,40.00),
  (1,3,3,3,10,70.00);

/* Events */
INSERT INTO event (user_id, event_date, start_time, end_time, event_type, description, workout_plan_id)
VALUES
  (1,'2026-03-02','18:00:00','19:00:00','workout','Full body session.',1),
  (2,'2026-03-02','09:00:00','09:30:00','coach_session','Check-in call.',NULL);

/* Meals + food items */
INSERT INTO meal (name, calories, protein, carbs, fats)
VALUES
  ('Chicken Bowl',650,45.00,70.00,18.00),
  ('Greek Yogurt',140,15.00,10.00,3.00);

INSERT INTO food_item (user_id, name, calories, protein, carbs, fats, image_url)
VALUES
  (1,'Homemade Oatmeal',300,10.00,50.00,6.00,NULL);

/* Meal plan + schedule */
INSERT INTO meal_plan (user_id, plan_name, start_date, end_date, total_calories)
VALUES
  (1,'Cut Plan Week 1','2026-03-02','2026-03-08',2000);

INSERT INTO user_meal (meal_id, meal_plan_id, meal_type, servings, day_of_week)
VALUES
  (1,1,'dinner',1.00,'Mon'),
  (2,1,'breakfast',1.00,'Mon');

/* Meal log */
INSERT INTO meal_log (user_id, meal_id, food_item_id, eaten_at, servings, notes, photo_url)
VALUES
  (1,2,NULL,'2026-03-02 08:10:00',1.00,'Quick breakfast.',NULL),
  (1,NULL,1,'2026-03-02 12:30:00',1.00,'Added berries.',NULL);

/* Contract + availability */
INSERT INTO user_coach_contract (coach_id, user_id, agreed_price, start_date, end_date, contract_text, active)
VALUES
  (2,1,75.00,'2026-03-01','2026-06-01','Monthly coaching agreement.',1);

INSERT INTO coach_availability (coach_id, day_of_week, start_time, end_time, recurring, active)
VALUES
  (2,'Mon','08:00:00','11:00:00',1,1),
  (2,'Wed','14:00:00','18:00:00',1,1);

/* Messaging */
INSERT INTO conversation (conversation_type, created_by, title)
VALUES
  ('dm',1,NULL),
  ('group',2,'Week 1 Accountability');

INSERT INTO conversation_member (conversation_id, user_id, role)
VALUES
  (1,1,'owner'),
  (1,2,'member'),
  (2,2,'owner'),
  (2,1,'member'),
  (2,3,'admin');

INSERT INTO message (conversation_id, sender_user_id, content, sent_at)
VALUES
  (1,1,'Hey coach, excited to start.','2026-03-02 07:55:00'),
  (1,2,'Let’s do it. Keep it simple, keep it consistent.','2026-03-02 08:00:00');

/* Reviews / reports */
INSERT INTO coach_review (coach_id, reviewer_user_id, rating, review_text)
VALUES
  (2,1,5,'Clear, practical, and motivating.');

INSERT INTO user_report (reported_user_id, reporter_user_id, reason, status, admin_action, resolved_by_admin_id)
VALUES
  (1,3,'Test report: spam content.','resolved','No action needed (test).',3);

/* Sessions + logs */
INSERT INTO workout_session (user_id, started_at, ended_at, workout_plan_id, notes)
VALUES
  (1,'2026-03-02 18:00:00','2026-03-02 18:55:00',1,'Felt good.');

INSERT INTO exercise_set_log (session_id, exercise_id, set_number, reps, weight, rpe, performed_at)
VALUES
  (1,1,1,10,NULL,7.5,'2026-03-02 18:10:00'),
  (1,2,1,12,40.00,8.0,'2026-03-02 18:25:00'),
  (1,3,1,10,70.00,8.0,'2026-03-02 18:40:00');

INSERT INTO cardio_log (session_id, user_id, performed_at, steps, distance_km, duration_min, calories, avg_hr)
VALUES
  (NULL,1,'2026-03-02 12:00:00',6500,4.800,45,280,118);

/* Metrics + wellness */
INSERT INTO daily_metrics (user_id, metric_date, weight, sleep_hours, resting_hr)
VALUES
  (1,'2026-03-02',179.5,7.25,58);

INSERT INTO mental_wellness_survey (user_id, survey_date, mood_score, notes)
VALUES
  (1,'2026-03-02',8,'Pretty solid day.');

INSERT INTO survey_question (prompt, question_type, active)
VALUES
  ('How stressed do you feel today (1-10)?','scale',1),
  ('Any notes about your mood?','text',1);

INSERT INTO survey_response (question_id, user_id, response_date, answer_text)
VALUES
  (1,1,'2026-03-02','3'),
  (2,1,'2026-03-02','Felt focused and productive.');

/* Landing + feature + showcase */
INSERT INTO landing_testimonial (before_after_story, text, rating, display_order)
VALUES
  ('Lost 12 lbs in 8 weeks.','I finally found a plan I can stick to.',5,1);

INSERT INTO progress_showcase_media (media_url, media_type, testimonial_id)
VALUES
  ('https://cdn.example.com/progress/alex_before_after.jpg','image',1);

INSERT INTO feature (title, description, icon, display_order, active)
VALUES
  ('Workout Plans','Build and follow structured plans.','dumbbell',1,1),
  ('Meal Tracking','Log meals and monitor macros.','utensils',2,1),
  ('Coach Messaging','Chat with your coach in-app.','message-circle',3,1);

INSERT INTO coach_featured (coach_id, display_order, start_date, end_date, active)
VALUES
  (2,1,'2026-03-01','2026-04-01',1);

/* Templates + assignment log */
INSERT INTO workout_plan_template (plan_id, author_user_id, is_public, description)
VALUES
  (1,2,1,'A simple full-body routine for beginners.');

INSERT INTO coach_assignment_log (coach_id, user_id, assigned_type, workout_plan_id, meal_plan_id, template_id, assigned_at, note)
VALUES
  (2,1,'workout_plan',1,NULL,NULL,'2026-03-01 10:00:00','Start with this plan for 2 weeks.'),
  (2,1,'meal_plan',NULL,1,NULL,'2026-03-01 10:05:00','Keep calories consistent.'),
  (2,1,'template',NULL,NULL,1,'2026-03-01 10:10:00','Public template reference.');

/* Points */
INSERT INTO points_wallet (user_id, balance) VALUES (1,100), (2,250), (3,500);

INSERT INTO points_txn (user_id, delta_points, reason, ref_type, ref_id)
VALUES
  (1, +50, 'Completed workout session', 'workout_session', 1),
  (1, -10, 'Prediction wager', 'prediction_market', NULL);

/* Prediction market */
INSERT INTO prediction_market (creator_user_id, title, goal_text, end_date, status)
VALUES
  (3,'Will Alex hit 175 by April?','Goal: reach 175 lbs by 2026-04-01.','2026-04-01','open');

INSERT INTO prediction (market_id, predictor_user_id, prediction_value, points_wagered)
VALUES
  (1,1,'yes',10),
  (1,2,'no',20);
