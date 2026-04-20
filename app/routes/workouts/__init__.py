from flask import Blueprint

workoutAction_bp = Blueprint("workoutAction", __name__)
exerciseLog_bp =   Blueprint("exerciseLog", __name__)
workouts_bp =      Blueprint("workouts", __name__)
from . import exerciseLogging
from . import workoutActions
from . import predefinedPlans
from . import assignPlan
from . import exercisesInPlan
from . import createWorkoutPlan
from . import myWorkouts
