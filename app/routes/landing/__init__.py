from flask import Blueprint

topCoaches_bp = Blueprint("topCoaches", __name__)

from . import topFiveCoaches