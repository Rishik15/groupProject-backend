from .test import test_bp
from .auth import auth_bp
from .client import client_bp
from .onboarding import onboard_bp
from .coach import coach_bp
from .nutrition import nutrition_bp
from .exercises import exercise_bp
from .chat import chat_bp
from .metrics import metric_bp
from .notifications import notify_bp
from .contracts import contract_bp
from .workouts import workoutAction_bp, exerciseLog_bp, workouts_bp
from .landing import landing_bp
from .admin import admin_bp
from .dashboard import dashboard_bp


def register_routes(app):
    app.register_blueprint(test_bp, url_prefix="/test")
    app.register_blueprint(landing_bp, url_prefix="/landing")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(onboard_bp, url_prefix="/onboard")
    app.register_blueprint(coach_bp, url_prefix="/coach")
    app.register_blueprint(workoutAction_bp, url_prefix="/workoutAction")
    app.register_blueprint(exerciseLog_bp, url_prefix="/exerciseLog")
    app.register_blueprint(workouts_bp, url_prefix="/workouts")
    app.register_blueprint(nutrition_bp, url_prefix="/nutrition")
    app.register_blueprint(exercise_bp, url_prefix="/exercise")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(metric_bp, url_prefix="/metrics")
    app.register_blueprint(notify_bp, url_prefix="/notifications")
    app.register_blueprint(contract_bp, url_prefix="/contract")
    app.register_blueprint(admin_bp, url_prefix="/admin")
