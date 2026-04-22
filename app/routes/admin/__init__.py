from flask import Blueprint

admin_bp = Blueprint("admin", __name__)

from . import dashboard
from . import users
from . import reports
from . import coach_applications
from . import exercises
from . import videos
from . import workouts