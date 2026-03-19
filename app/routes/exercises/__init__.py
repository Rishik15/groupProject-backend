from flask import Blueprint

exerciseLog_bp = Blueprint("setLogging", __name__)
markExerciseDone_bp = Blueprint("WorkoutDone", __name__)
workoutSession_bp = Blueprint("workoutSession", __name__)
cardioLog_bp = Blueprint("cardioLog", __name__)

from . import exerciseLogging