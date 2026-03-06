DROP DATABASE IF EXISTS exercise_app;
CREATE DATABASE exercise_app;
USE exercise_app;

SET SESSION time_zone = '+00:00';

-- append-only log written to by triggers
CREATE TABLE audit_event (
  audit_id      INT AUTO_INCREMENT PRIMARY KEY,
  actor_user_id INT NULL,
  entity_table  VARCHAR(64) NOT NULL,
  entity_pk     VARCHAR(128) NOT NULL,
  action_type   ENUM('INSERT','UPDATE','DELETE','SYSTEM') NOT NULL,
  action_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  details       JSON NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (action_at),
  INDEX (entity_table, entity_pk),
  INDEX (actor_user_id)
);

-- split from user_mutables, These are attributes that don't change 
CREATE TABLE users_immutables (
  user_id      INT AUTO_INCREMENT PRIMARY KEY,
  dob          DATE NULL,
  first_name   VARCHAR(50) NOT NULL,
  last_name    VARCHAR(50) NOT NULL,
  email        VARCHAR(100) NOT NULL,
  phone_number VARCHAR(20) NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (email),
  INDEX (last_name, first_name)
);

-- mutable profile fields, the ones that change with fitness
CREATE TABLE user_mutables (
  user_id         INT PRIMARY KEY,
  profile_picture VARCHAR(255) NULL,
  weight          INT NULL,
  height          INT NULL,
  goal_weight     INT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- auth credentials kept separate personal info 
CREATE TABLE user_creds (
  user_id       INT PRIMARY KEY,
  username      CHAR(25) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  email         VARCHAR(100) NOT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (username),
  UNIQUE KEY (email),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- coaches and admins are users (1:1)
CREATE TABLE coach (
  coach_id          INT PRIMARY KEY,
  coach_description TEXT NULL,
  price             DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (coach_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX (price)
);

CREATE TABLE admin (
  admin_id   INT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (admin_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE certifications (
  cert_id       INT AUTO_INCREMENT PRIMARY KEY,
  coach_id      INT NOT NULL,
  cert_name     VARCHAR(120) NOT NULL,
  provider_name VARCHAR(120) NULL,
  description   TEXT NULL,
  issued_date   DATE NULL,
  expires_date  DATE NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX (issued_date, expires_date)
);

CREATE TABLE calendar (
  calendar_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  full_date   DATE NOT NULL,
  day_name    ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (user_id, full_date),
  INDEX (full_date),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE workout_plan (
  plan_id    INT AUTO_INCREMENT PRIMARY KEY,
  plan_name  VARCHAR(120) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (plan_name)
);

CREATE TABLE exercise (
  exercise_id   INT AUTO_INCREMENT PRIMARY KEY,
  exercise_name VARCHAR(120) NOT NULL,
  equipment     VARCHAR(120) NULL,
  video_url     VARCHAR(255) NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (exercise_name),
  INDEX (equipment)
);

-- junction table: links exercises to a workout plan with exercise ordering and perexercise targets
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
  -- order index useful for sorted fetches
  INDEX (plan_id, order_in_workout),
  FOREIGN KEY (plan_id) REFERENCES workout_plan(plan_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercise(exercise_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE event (
  event_id        INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  event_date      DATE NOT NULL,
  start_time      TIME NULL,
  end_time        TIME NULL,
  event_type      ENUM('workout','meal','coach_session','reminder','other') NOT NULL DEFAULT 'other',
  description     TEXT NULL,
  workout_plan_id INT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (user_id, event_date),
  INDEX (event_date),
  INDEX (event_type),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE meal (
  meal_id    INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(120) NOT NULL,
  calories   INT NOT NULL DEFAULT 0,
  protein    DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  carbs      DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  fats       DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (name),
  INDEX (calories)
);

CREATE TABLE food_item (
  food_item_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  name         VARCHAR(120) NOT NULL,
  calories     INT NOT NULL DEFAULT 0,
  protein      DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  carbs        DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  fats         DECIMAL(7,2) NOT NULL DEFAULT 0.00,
  image_url    VARCHAR(255) NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (user_id, name),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE meal_plan (
  meal_plan_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id        INT NOT NULL,
  plan_name      VARCHAR(120) NOT NULL,
  start_date     DATE NULL,
  end_date       DATE NULL,
  total_calories INT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (user_id, plan_name),
  INDEX (start_date, end_date),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- junction table: assigns meals to a plan with serving size and day of week
CREATE TABLE user_meal (
  meal_id      INT NOT NULL,
  meal_plan_id INT NOT NULL,
  meal_type    ENUM('breakfast','lunch','dinner','snack') NOT NULL,
  servings     DECIMAL(6,2) NOT NULL DEFAULT 1.00,
  day_of_week  ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (meal_id, meal_plan_id),
  INDEX (meal_type),
  INDEX (day_of_week),
  FOREIGN KEY (meal_id) REFERENCES meal(meal_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(meal_plan_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- meal_id and food_item_id are mutually exclusive 
CREATE TABLE meal_log (
  log_id       INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  meal_id      INT NULL,
  food_item_id INT NULL,
  eaten_at     DATETIME NOT NULL,
  servings     DECIMAL(6,2) NOT NULL DEFAULT 1.00,
  notes        TEXT NULL,
  photo_url    VARCHAR(255) NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (user_id, eaten_at),
  INDEX (eaten_at),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (meal_id) REFERENCES meal(meal_id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (food_item_id) REFERENCES food_item(food_item_id) ON DELETE SET NULL ON UPDATE CASCADE
);


CREATE TABLE user_coach_contract (
  contract_id   INT AUTO_INCREMENT PRIMARY KEY,
  coach_id      INT NOT NULL,
  user_id       INT NOT NULL,
  agreed_price  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  start_date    DATE NOT NULL,
  end_date      DATE NULL,
  contract_text TEXT NULL,
  active        TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (active),
  INDEX (start_date, end_date),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE coach_availability (
  availability_id INT AUTO_INCREMENT PRIMARY KEY,
  coach_id        INT NOT NULL,
  day_of_week     ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') NOT NULL,
  start_time      TIME NOT NULL,
  end_time        TIME NOT NULL,
  recurring       TINYINT(1) NOT NULL DEFAULT 1,
  active          TINYINT(1) NOT NULL DEFAULT 1,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (day_of_week),
  INDEX (active),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE coach_time_off (
  time_off_id INT AUTO_INCREMENT PRIMARY KEY,
  coach_id    INT NOT NULL,
  start_dt    DATETIME NOT NULL,
  end_dt      DATETIME NOT NULL,
  reason      VARCHAR(255) NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (start_dt, end_dt),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE coach_client_note (
  note_id        INT AUTO_INCREMENT PRIMARY KEY,
  coach_id       INT NOT NULL,
  client_user_id INT NOT NULL,
  note_text      TEXT NOT NULL,
  private        TINYINT(1) NOT NULL DEFAULT 1,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (private),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (client_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE workout_plan_template (
  template_id    INT AUTO_INCREMENT PRIMARY KEY,
  plan_id        INT NOT NULL,
  author_user_id INT NOT NULL,
  is_public      TINYINT(1) NOT NULL DEFAULT 0,
  description    TEXT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (is_public),
  FOREIGN KEY (plan_id) REFERENCES workout_plan(plan_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (author_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE coach_assignment_log (
  assignment_id   INT AUTO_INCREMENT PRIMARY KEY,
  coach_id        INT NOT NULL,
  user_id         INT NOT NULL,
  assigned_type   ENUM('workout_plan','meal_plan','template') NOT NULL,
  workout_plan_id INT NULL,
  meal_plan_id    INT NULL,
  template_id     INT NULL,
  assigned_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note            TEXT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (assigned_type),
  INDEX (assigned_at),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(meal_plan_id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (template_id) REFERENCES workout_plan_template(template_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE conversation (
  conversation_id   INT AUTO_INCREMENT PRIMARY KEY,
  conversation_type ENUM('dm','group') NOT NULL,
  created_by        INT NOT NULL,
  title             VARCHAR(120) NULL,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (conversation_type),
  FOREIGN KEY (created_by) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE conversation_member (
  conversation_id INT NOT NULL,
  user_id         INT NOT NULL,
  joined_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  role            ENUM('member','admin','owner') NOT NULL DEFAULT 'member',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (conversation_id, user_id),
  INDEX (joined_at),
  FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE message (
  message_id      INT AUTO_INCREMENT PRIMARY KEY,
  conversation_id INT NOT NULL,
  sender_user_id  INT NOT NULL,
  content         TEXT NOT NULL,
  sent_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  edited_at       DATETIME NULL,
  deleted_at      DATETIME NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (conversation_id, sent_at),
  INDEX (sender_user_id, sent_at),
  INDEX (deleted_at),
  FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (sender_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE coach_review (
  review_id        INT AUTO_INCREMENT PRIMARY KEY,
  coach_id         INT NOT NULL,
  reviewer_user_id INT NOT NULL,
  rating           TINYINT NOT NULL,
  review_text      TEXT NULL,
  created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (coach_id, reviewer_user_id),
  INDEX (rating),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (reviewer_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE user_report (
  report_id            INT AUTO_INCREMENT PRIMARY KEY,
  reported_user_id     INT NOT NULL,
  reporter_user_id     INT NOT NULL,
  reason               TEXT NOT NULL,
  status               ENUM('open','reviewing','resolved','dismissed') NOT NULL DEFAULT 'open',
  admin_action         TEXT NULL,
  resolved_by_admin_id INT NULL,
  created_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (status),
  INDEX (created_at),
  FOREIGN KEY (reported_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (reporter_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (resolved_by_admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE workout_session (
  session_id      INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  started_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at        DATETIME NULL,
  workout_plan_id INT NULL,
  notes           TEXT NULL,
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (user_id, started_at),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (workout_plan_id) REFERENCES workout_plan(plan_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE exercise_set_log (
  set_log_id   INT AUTO_INCREMENT PRIMARY KEY,
  session_id   INT NOT NULL,
  exercise_id  INT NOT NULL,
  set_number   INT NOT NULL,
  reps         INT NULL,
  weight       DECIMAL(10,2) NULL,
  rpe          DECIMAL(4,2) NULL,
  performed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (performed_at),
  FOREIGN KEY (session_id) REFERENCES workout_session(session_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (exercise_id) REFERENCES exercise(exercise_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE cardio_log (
  cardio_log_id INT AUTO_INCREMENT PRIMARY KEY,
  session_id    INT NULL,
  user_id       INT NOT NULL,
  performed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  steps         INT NULL,
  distance_km   DECIMAL(10,3) NULL,
  duration_min  INT NULL,
  calories      INT NULL,
  avg_hr        INT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (user_id, performed_at),
  INDEX (performed_at),
  FOREIGN KEY (session_id) REFERENCES workout_session(session_id) ON DELETE SET NULL ON UPDATE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE daily_metrics (
  metrics_id  INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  metric_date DATE NOT NULL,
  weight      DECIMAL(7,2) NULL,
  sleep_hours DECIMAL(4,2) NULL,
  resting_hr  INT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (user_id, metric_date),
  INDEX (metric_date),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE mental_wellness_survey (
  survey_id   INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  survey_date DATE NOT NULL,
  mood_score  TINYINT NULL,
  notes       TEXT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (user_id, survey_date),
  INDEX (survey_date),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE survey_question (
  question_id   INT AUTO_INCREMENT PRIMARY KEY,
  prompt        TEXT NOT NULL,
  question_type ENUM('text','scale','multi_choice','yes_no') NOT NULL DEFAULT 'text',
  active        TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (active),
  INDEX (question_type)
);

CREATE TABLE survey_response (
  response_id   INT AUTO_INCREMENT PRIMARY KEY,
  question_id   INT NOT NULL,
  user_id       INT NOT NULL,
  response_date DATE NOT NULL,
  answer_text   TEXT NULL,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (question_id, user_id, response_date),
  INDEX (user_id, response_date),
  FOREIGN KEY (question_id) REFERENCES survey_question(question_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE points_wallet (
  user_id    INT PRIMARY KEY,
  balance    INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (balance),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- balance lives in points_wallet, this table is the history
CREATE TABLE points_txn (
  txn_id       INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  delta_points INT NOT NULL,
  reason       VARCHAR(255) NOT NULL,
  ref_type     VARCHAR(50) NULL,
  ref_id       INT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (created_at),
  INDEX (ref_type, ref_id),
  FOREIGN KEY (user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- a user goal that others can bet points on, settled manually or via admin
CREATE TABLE prediction_market (
  market_id       INT AUTO_INCREMENT PRIMARY KEY,
  creator_user_id INT NOT NULL,
  title           VARCHAR(200) NOT NULL,
  goal_text       TEXT NOT NULL,
  end_date        DATE NOT NULL,
  status          ENUM('open','closed','settled','cancelled') NOT NULL DEFAULT 'open',
  created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (status),
  INDEX (end_date),
  FOREIGN KEY (creator_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- one row per user per market, unique key enforces you can't bet twice on the same market
CREATE TABLE prediction (
  prediction_id     INT AUTO_INCREMENT PRIMARY KEY,
  market_id         INT NOT NULL,
  predictor_user_id INT NOT NULL,
  prediction_value  ENUM('yes','no') NOT NULL,
  points_wagered    INT NOT NULL DEFAULT 0,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (market_id, predictor_user_id),
  INDEX (prediction_value),
  FOREIGN KEY (market_id) REFERENCES prediction_market(market_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (predictor_user_id) REFERENCES users_immutables(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE landing_testimonial (
  testimonial_id     INT AUTO_INCREMENT PRIMARY KEY,
  before_after_story TEXT NULL,
  text               TEXT NOT NULL,
  rating             TINYINT NULL,
  display_order      INT NOT NULL DEFAULT 0,
  created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (display_order),
  INDEX (rating)
);

CREATE TABLE progress_showcase_media (
  media_id       INT AUTO_INCREMENT PRIMARY KEY,
  media_url      VARCHAR(255) NOT NULL,
  media_type     ENUM('image','video') NOT NULL,
  testimonial_id INT NULL,
  created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (media_type),
  FOREIGN KEY (testimonial_id) REFERENCES landing_testimonial(testimonial_id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE feature (
  feature_id    INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(120) NOT NULL,
  description   TEXT NULL,
  icon          VARCHAR(120) NULL,
  display_order INT NOT NULL DEFAULT 0,
  active        TINYINT(1) NOT NULL DEFAULT 1,
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX (active),
  INDEX (display_order)
);

CREATE TABLE coach_featured (
  coach_featured_id INT AUTO_INCREMENT PRIMARY KEY,
  coach_id          INT NOT NULL,
  display_order     INT NOT NULL DEFAULT 0,
  start_date        DATE NULL,
  end_date          DATE NULL,
  active            TINYINT(1) NOT NULL DEFAULT 1,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY (coach_id, active),
  INDEX (display_order),
  INDEX (active),
  INDEX (start_date, end_date),
  FOREIGN KEY (coach_id) REFERENCES coach(coach_id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- audit triggers

DELIMITER $$

CREATE TRIGGER trg_users_ins
AFTER INSERT ON users_immutables FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'users_immutables', CAST(NEW.user_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('email', NEW.email, 'first_name', NEW.first_name, 'last_name', NEW.last_name));
END$$

CREATE TRIGGER trg_users_upd
AFTER UPDATE ON users_immutables FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'users_immutables', CAST(NEW.user_id AS CHAR), 'UPDATE', NOW(),
          JSON_OBJECT('old_email', OLD.email, 'new_email', NEW.email));
END$$

CREATE TRIGGER trg_users_del
AFTER DELETE ON users_immutables FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (OLD.user_id, 'users_immutables', CAST(OLD.user_id AS CHAR), 'DELETE', NOW(),
          JSON_OBJECT('email', OLD.email));
END$$

CREATE TRIGGER trg_message_ins
AFTER INSERT ON message FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.sender_user_id, 'message', CAST(NEW.message_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('conversation_id', NEW.conversation_id, 'sent_at', NEW.sent_at));
END$$

CREATE TRIGGER trg_message_upd
AFTER UPDATE ON message FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.sender_user_id, 'message', CAST(NEW.message_id AS CHAR), 'UPDATE', NOW(),
          JSON_OBJECT('edited_at', NEW.edited_at, 'deleted_at', NEW.deleted_at));
END$$

CREATE TRIGGER trg_after_points_txn_insert
AFTER INSERT ON points_txn FOR EACH ROW
BEGIN
  INSERT INTO audit_event (actor_user_id, entity_table, entity_pk, action_type, action_at, details)
  VALUES (NEW.user_id, 'points_txn', CAST(NEW.txn_id AS CHAR), 'INSERT', NOW(),
          JSON_OBJECT('delta_points', NEW.delta_points, 'reason', NEW.reason, 'ref_type', NEW.ref_type, 'ref_id', NEW.ref_id));
END$$

DELIMITER ;
