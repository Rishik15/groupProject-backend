-- users
INSERT INTO users_immutables (dob, first_name, last_name, email, phone_number) VALUES
  ('2000-01-01', 'Alex',   'Taylor', 'alex@example.com',   '555-1000'),
  ('1998-06-15', 'Sam',    'Nguyen', 'sam@example.com',    '555-2000'),
  ('1995-11-20', 'Jordan', 'Patel',  'jordan@example.com', '555-3000'),
  ('1997-02-11', 'Taylor', 'Brooks', 'taylor@example.com', '555-4000'),
  ('1994-09-23', 'Morgan', 'Lee',    'morgan@example.com', '555-5000'),
  ('2001-07-04', 'Riley',  'Chen',   'riley@example.com',  '555-6000'),
  ('1999-12-18', 'Casey',  'Diaz',   'casey@example.com',  '555-7000');

INSERT INTO user_mutables (user_id, profile_picture, weight, height, goal_weight) VALUES
  (1, 'https://cdn.example.com/pfp/alex.png', 180, 70, 170),
  (2, 'https://cdn.example.com/pfp/sam.png',  150, 66, 145),
  (3, NULL, 210, 72, 190),
  (4, NULL, 165, 68, 155),
  (5, NULL, 140, 64, 135),
  (6, NULL, 190, 71, 180),
  (7, NULL, 155, 67, 150);

INSERT INTO user_creds (user_id, username, password_hash, email) VALUES
  (1, 'alex_t',   'hash_abc123', 'alex@example.com'),
  (2, 'sam_n',    'hash_def456', 'sam@example.com'),
  (3, 'jordan_p', 'hash_ghi789', 'jordan@example.com'),
  (4, 'taylor_b', 'hash_t1',     'taylor@example.com'),
  (5, 'morgan_l', 'hash_m1',     'morgan@example.com'),
  (6, 'riley_c',  'hash_r1',     'riley@example.com'),
  (7, 'casey_d',  'hash_c1',     'casey@example.com');

INSERT INTO coach (coach_id, coach_description, price) VALUES
  (2, 'Certified coach focusing on strength + habit building.', 75.00),
  (4, 'HIIT and conditioning specialist.',                      65.00);

INSERT INTO admin (admin_id) VALUES (3);

INSERT INTO certifications (coach_id, cert_name, provider_name, description, issued_date, expires_date) VALUES
  (2, 'CPT',             'NASM',               'Certified Personal Trainer',      '2022-01-01', '2026-01-01'),
  (2, 'Nutrition Coach', 'Precision Nutrition', 'Nutrition coaching fundamentals', '2023-05-01', NULL),
  (4, 'CSCS',            'NSCA',                NULL,                              '2021-03-01', NULL),
  (4, 'CPR/AED',         'Red Cross',           NULL,                              '2023-01-15', NULL);

-- workouts
INSERT INTO workout_plan (plan_name) VALUES
  ('Beginner Full Body A'),
  ('Upper/Lower Split'),
  ('Push Pull Legs'),
  ('Beginner Cardio Plan'),
  ('Hypertrophy Focus');

INSERT INTO exercise (exercise_name, equipment, video_url) VALUES
  ('Push-Up',       'Bodyweight', 'https://video.example.com/pushup'),
  ('Goblet Squat',  'Dumbbell',   'https://video.example.com/goblet_squat'),
  ('Lat Pulldown',  'Machine',    'https://video.example.com/lat_pulldown'),
  ('Bench Press',   'Barbell',    NULL),
  ('Deadlift',      'Barbell',    NULL),
  ('Treadmill Run', 'Treadmill',  NULL),
  ('Plank',         'Bodyweight', NULL);

INSERT INTO plan_exercise (plan_id, exercise_id, order_in_workout, sets_goal, reps_goal, weight_goal) VALUES
  (1, 1, 1, 3, 10, NULL),
  (1, 2, 2, 3, 12, 40.00),
  (1, 3, 3, 3, 10, 70.00),
  (3, 4, 1, 4,  8, NULL),
  (3, 5, 2, 3,  5, NULL),
  (4, 6, 1, 1,  1, NULL),
  (5, 7, 1, 3, 60, NULL);

-- events
INSERT INTO event (user_id, event_date, start_time, end_time, event_type, description, workout_plan_id) VALUES
  (1, '2026-03-02', '18:00:00', '19:00:00', 'workout',       'Full body session.', 1),
  (2, '2026-03-02', '09:00:00', '09:30:00', 'coach_session', 'Check-in call.',     NULL),
  (4, '2026-03-03', '07:00:00', '08:00:00', 'workout',       'Morning lift',       NULL),
  (5, '2026-03-04', '12:00:00', '12:30:00', 'meal',          'Lunch prep',         NULL),
  (6, '2026-03-05', '18:00:00', '18:30:00', 'reminder',      'Stretching',         NULL);

-- meals
INSERT INTO meal (name, calories, protein, carbs, fats) VALUES
  ('Chicken Bowl',  650, 45.00, 70.00, 18.00),
  ('Greek Yogurt',  140, 15.00, 10.00,  3.00),
  ('Salmon Plate',  550, 40.00, 30.00, 25.00),
  ('Protein Shake', 220, 30.00, 10.00,  5.00),
  ('Avocado Toast', 350, 12.00, 40.00, 18.00);

INSERT INTO food_item (user_id, name, calories, protein, carbs, fats) VALUES
  (1, 'Homemade Oatmeal', 300, 10.00, 50.00, 6.00);

INSERT INTO meal_plan (user_id, plan_name, start_date, end_date, total_calories) VALUES
  (1, 'Cut Plan Week 1',  '2026-03-02', '2026-03-08', 2000),
  (2, 'Maintenance Week', NULL,         NULL,          NULL),
  (4, 'Lean Bulk',        NULL,         NULL,          NULL);

INSERT INTO user_meal (meal_id, meal_plan_id, meal_type, servings, day_of_week) VALUES
  (1, 1, 'dinner',    1.00, 'Mon'),
  (2, 1, 'breakfast', 1.00, 'Mon');

INSERT INTO meal_log (user_id, meal_id, food_item_id, eaten_at, servings, notes) VALUES
  (1, 2,    NULL, '2026-03-02 08:10:00', 1.00, 'Quick breakfast.'),
  (1, NULL, 1,    '2026-03-02 12:30:00', 1.00, 'Added berries.');

-- coaching
INSERT INTO user_coach_contract (coach_id, user_id, agreed_price, start_date, end_date, contract_text, active) VALUES
  (2, 1, 75.00, '2026-03-01', '2026-06-01', 'Monthly coaching agreement.', 1);

INSERT INTO coach_availability (coach_id, day_of_week, start_time, end_time, recurring, active) VALUES
  (2, 'Mon', '08:00:00', '11:00:00', 1, 1),
  (2, 'Wed', '14:00:00', '18:00:00', 1, 1);

-- messaging
INSERT INTO conversation (conversation_type, created_by, title) VALUES
  ('dm',    1, NULL),
  ('group', 2, 'Week 1 Accountability'),
  ('group', 4, 'HIIT Squad');

INSERT INTO conversation_member (conversation_id, user_id, role) VALUES
  (1, 1, 'owner'),
  (1, 2, 'member'),
  (2, 2, 'owner'),
  (2, 1, 'member'),
  (2, 3, 'admin'),
  (3, 4, 'owner'),
  (3, 5, 'member'),
  (3, 6, 'member');

INSERT INTO message (conversation_id, sender_user_id, content, sent_at) VALUES
  (1, 1, 'Hey coach, excited to start.',                      '2026-03-02 07:55:00'),
  (1, 2, 'Let''s do it. Keep it simple, keep it consistent.', '2026-03-02 08:00:00'),
  (3, 4, 'Let''s crush today''s HIIT.',                       '2026-03-03 06:50:00'),
  (3, 5, 'Ready when you are!',                               '2026-03-03 06:55:00');

-- reviews
INSERT INTO coach_review (coach_id, reviewer_user_id, rating, review_text) VALUES
  (2, 1, 5, 'Clear, practical, and motivating.'),
  (2, 5, 4, 'Very structured and clear.'),
  (4, 6, 5, 'High energy and motivating.');

-- reports
INSERT INTO user_report (reported_user_id, reporter_user_id, reason, status, admin_action, resolved_by_admin_id) VALUES
  (1, 3, 'Test report: spam content.', 'resolved', 'No action needed (test).', 3);

-- sessions
INSERT INTO workout_session (user_id, started_at, ended_at, workout_plan_id, notes) VALUES
  (1, '2026-03-02 18:00:00', '2026-03-02 18:55:00', 1, 'Felt good.'),
  (4, '2026-03-03 07:00:00', NULL,                   3, 'Push day complete.'),
  (5, '2026-03-04 12:00:00', NULL,                   4, 'Cardio session.'),
  (6, '2026-03-05 18:00:00', NULL,                   3, 'Heavy pull day.');

INSERT INTO exercise_set_log (session_id, exercise_id, set_number, reps, weight, rpe, performed_at) VALUES
  (1, 1, 1, 10, NULL,   7.5, '2026-03-02 18:10:00'),
  (1, 2, 1, 12, 40.00,  8.0, '2026-03-02 18:25:00'),
  (1, 3, 1, 10, 70.00,  8.0, '2026-03-02 18:40:00'),
  (2, 4, 1,  8, 135.00, NULL, '2026-03-03 07:10:00'),
  (3, 5, 1,  5, 225.00, NULL, '2026-03-04 12:10:00');

INSERT INTO cardio_log (session_id, user_id, performed_at, steps, distance_km, duration_min, calories, avg_hr) VALUES
  (NULL, 1, '2026-03-02 12:00:00', 6500, 4.800, 45, 280, 118);

-- metrics
INSERT INTO daily_metrics (user_id, metric_date, weight, sleep_hours, resting_hr) VALUES
  (1, '2026-03-02', 179.5, 7.25, 58),
  (2, '2026-03-02', 149.0, NULL, NULL),
  (4, '2026-03-02', 164.0, NULL, NULL),
  (5, '2026-03-02', 139.0, NULL, NULL);

-- wellness
INSERT INTO mental_wellness_survey (user_id, survey_date, mood_score, notes) VALUES
  (1, '2026-03-02', 8, 'Pretty solid day.'),
  (2, '2026-03-02', 7, NULL),
  (4, '2026-03-02', 9, NULL);

INSERT INTO survey_question (prompt, question_type, active) VALUES
  ('How stressed do you feel today (1-10)?', 'scale', 1),
  ('Any notes about your mood?',             'text',  1);

INSERT INTO survey_response (question_id, user_id, response_date, answer_text) VALUES
  (1, 1, '2026-03-02', '3'),
  (2, 1, '2026-03-02', 'Felt focused and productive.'),
  (1, 2, '2026-03-02', '5'),
  (2, 4, '2026-03-02', 'Feeling energized.');

-- points
INSERT INTO points_wallet (user_id, balance) VALUES
  (1, 100),
  (2, 250),
  (3, 500);

INSERT INTO points_txn (user_id, delta_points, reason, ref_type, ref_id) VALUES
  (1,  50, 'Completed workout session', 'workout_session',   1),
  (1, -10, 'Prediction wager',          'prediction_market', NULL),
  (2,  25, 'Workout bonus',             NULL,                NULL),
  (4,  40, 'Challenge completed',       NULL,                NULL);

-- prediction market
INSERT INTO prediction_market (creator_user_id, title, goal_text, end_date, status) VALUES
  (3, 'Will Alex hit 175 by April?',             'Goal: reach 175 lbs by 2026-04-01.', '2026-04-01', 'open'),
  (1, 'Will Sam complete 3 workouts this week?', 'Goal: 3 logged sessions.',            '2026-03-10', 'open');

INSERT INTO prediction (market_id, predictor_user_id, prediction_value, points_wagered) VALUES
  (1, 1, 'yes', 10),
  (1, 2, 'no',  20),
  (2, 1, 'yes', 15),
  (2, 4, 'no',  10);

-- landing
INSERT INTO landing_testimonial (before_after_story, text, rating, display_order) VALUES
  ('Lost 12 lbs in 8 weeks.', 'I finally found a plan I can stick to.', 5, 1),
  (NULL,                       'Lost 8 lbs and gained confidence!',      5, 2),
  (NULL,                       'Best app I''ve used for tracking.',       4, 3);

INSERT INTO progress_showcase_media (media_url, media_type, testimonial_id) VALUES
  ('https://cdn.example.com/progress/alex_before_after.jpg', 'image', 1);

INSERT INTO feature (title, description, icon, display_order, active) VALUES
  ('Workout Plans',        'Build and follow structured plans.', 'dumbbell',       1, 1),
  ('Meal Tracking',        'Log meals and monitor macros.',      'utensils',       2, 1),
  ('Coach Messaging',      'Chat with your coach in-app.',       'message-circle', 3, 1),
  ('Progress Charts',      'Visualize trends over time.',        'chart-line',     4, 1),
  ('Community Challenges', 'Compete with friends.',              'trophy',         5, 1);

INSERT INTO coach_featured (coach_id, display_order, start_date, end_date, active) VALUES
  (2, 1, '2026-03-01', '2026-04-01', 1);

INSERT INTO workout_plan_template (plan_id, author_user_id, is_public, description) VALUES
  (1, 2, 1, 'A simple full-body routine for beginners.');

INSERT INTO coach_assignment_log (coach_id, user_id, assigned_type, workout_plan_id, meal_plan_id, template_id, assigned_at, note) VALUES
  (2, 1, 'workout_plan', 1,    NULL, NULL, '2026-03-01 10:00:00', 'Start with this plan for 2 weeks.'),
  (2, 1, 'meal_plan',    NULL, 1,    NULL, '2026-03-01 10:05:00', 'Keep calories consistent.'),
  (2, 1, 'template',     NULL, NULL, 1,    '2026-03-01 10:10:00', 'Public template reference.');

select * from user_meal; 
select * from points_wallet; 
