from flask import Blueprint

manage_workouts_bp = Blueprint("manage_workouts", __name__)

from . import workoutRoutes