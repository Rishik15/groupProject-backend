from flask import Blueprint

survey_bp = Blueprint("survey", __name__)

from . import reward