from flask import Blueprint

nutrition_bp = Blueprint("nutrition", __name__)

from . import logMeals