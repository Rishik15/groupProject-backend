from flask import Blueprint

workoutAction_bp = Blueprint("workoutAction", __name__)
exerciseLog_bp = Blueprint("exerciseLog", __name__)
from . import exerciseLogging
from . import workoutActions