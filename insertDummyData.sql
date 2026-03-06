
/*  USERS  */
INSERT INTO users_immutables (dob, first_name, last_name, email, phone_number)
VALUES
('1997-02-11','Taylor','Brooks','taylor@example.com','555-4000'),
('1994-09-23','Morgan','Lee','morgan@example.com','555-5000'),
('2001-07-04','Riley','Chen','riley@example.com','555-6000'),
('1999-12-18','Casey','Diaz','casey@example.com','555-7000');

INSERT INTO user_mutables (user_id, profile_picture, weight, height, goal_weight)
VALUES
(4,NULL,165,68,155),
(5,NULL,140,64,135),
(6,NULL,190,71,180),
(7,NULL,155,67,150);

INSERT INTO user_creds (user_id, username, password_hash, email)
VALUES
(4,'taylor_b','hash_t1','taylor@example.com'),
(5,'morgan_l','hash_m1','morgan@example.com'),
(6,'riley_c','hash_r1','riley@example.com'),
(7,'casey_d','hash_c1','casey@example.com');

/* Promote one more coach */
INSERT INTO coach (coach_id, coach_description, price)
VALUES
(4,'HIIT and conditioning specialist.',65.00);

/* Additional certifications */
INSERT INTO certifications (coach_id, cert_name, provider_name, issued_date)
VALUES
(4,'CSCS','NSCA','2021-03-01'),
(4,'CPR/AED','Red Cross','2023-01-15');

/*  WORKOUTS  */
INSERT INTO workout_plan (plan_name)
VALUES
('Push Pull Legs'),
('Beginner Cardio Plan'),
('Hypertrophy Focus');

INSERT INTO exercise (exercise_name, equipment)
VALUES
('Bench Press','Barbell'),
('Deadlift','Barbell'),
('Treadmill Run','Treadmill'),
('Plank','Bodyweight');

/* Map exercises */
INSERT INTO plan_exercise (plan_id, exercise_id, order_in_workout, sets_goal, reps_goal)
VALUES
(3,4,1,4,8),
(3,5,2,3,5),
(4,6,1,1,1),
(5,7,1,3,60);

/*  EVENTS  */
INSERT INTO event (user_id, event_date, start_time, end_time, event_type, description)
VALUES
(4,'2026-03-03','07:00:00','08:00:00','workout','Morning lift'),
(5,'2026-03-04','12:00:00','12:30:00','meal','Lunch prep'),
(6,'2026-03-05','18:00:00','18:30:00','reminder','Stretching');

/*  MEALS  */
INSERT INTO meal (name, calories, protein, carbs, fats)
VALUES
('Salmon Plate',550,40,30,25),
('Protein Shake',220,30,10,5),
('Avocado Toast',350,12,40,18);

INSERT INTO meal_plan (user_id, plan_name)
VALUES
(2,'Maintenance Week'),
(4,'Lean Bulk');

/*  MESSAGING  */
INSERT INTO conversation (conversation_type, created_by, title)
VALUES
('group',4,'HIIT Squad');

INSERT INTO conversation_member (conversation_id, user_id, role)
VALUES
(3,4,'owner'),
(3,5,'member'),
(3,6,'member');

INSERT INTO message (conversation_id, sender_user_id, content)
VALUES
(3,4,'Let’s crush today’s HIIT.'),
(3,5,'Ready when you are!');

/*  REVIEWS  */
INSERT INTO coach_review (coach_id, reviewer_user_id, rating, review_text)
VALUES
(2,5,4,'Very structured and clear.'),
(4,6,5,'High energy and motivating.');

/*  WORKOUT SESSIONS  */
INSERT INTO workout_session (user_id, workout_plan_id, notes)
VALUES
(4,3,'Push day complete.'),
(5,4,'Cardio session.'),
(6,3,'Heavy pull day.');

INSERT INTO exercise_set_log (session_id, exercise_id, set_number, reps, weight)
VALUES
(2,4,1,8,135),
(3,5,1,5,225);

/*  METRICS  */
INSERT INTO daily_metrics (user_id, metric_date, weight)
VALUES
(2,'2026-03-02',149.0),
(4,'2026-03-02',164.0),
(5,'2026-03-02',139.0);

/*  SURVEYS  */
INSERT INTO mental_wellness_survey (user_id, survey_date, mood_score)
VALUES
(2,'2026-03-02',7),
(4,'2026-03-02',9);

INSERT INTO survey_response (question_id, user_id, response_date, answer_text)
VALUES
(1,2,'2026-03-02','5'),
(2,4,'2026-03-02','Feeling energized.');

/*  POINTS  */
INSERT INTO points_txn (user_id, delta_points, reason)
VALUES
(2,25,'Workout bonus'),
(4,40,'Challenge completed');

/*  PREDICTION MARKET  */
INSERT INTO prediction_market (creator_user_id, title, goal_text, end_date)
VALUES
(1,'Will Sam complete 3 workouts this week?','Goal: 3 logged sessions.','2026-03-10');

INSERT INTO prediction (market_id, predictor_user_id, prediction_value, points_wagered)
VALUES
(2,1,'yes',15),
(2,4,'no',10);

/*  LANDING  */
INSERT INTO landing_testimonial (text, rating, display_order)
VALUES
('Lost 8 lbs and gained confidence!',5,2),
('Best app I’ve used for tracking.',4,3);

INSERT INTO feature (title, description, icon)
VALUES
('Progress Charts','Visualize trends over time.','chart-line'),
('Community Challenges','Compete with friends.','trophy');
