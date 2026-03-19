from flask import Blueprint

exerciseLog_bp = Blueprint("setLogging", __name__)
markExerciseDone_bp = Blueprint("WorkoutDone", __name__)

from . import exerciseLogging