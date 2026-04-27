from flask import Blueprint

coach_session_bp = Blueprint("coachsession", __name__)

from . import coachSessionRoutes
