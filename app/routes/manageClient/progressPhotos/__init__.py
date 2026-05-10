from flask import Blueprint

manage_progress_photos_bp = Blueprint("manage_progress_photos", __name__)

from . import progressPhotoRoutes
