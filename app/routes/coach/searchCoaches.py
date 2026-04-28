from flask import jsonify, request, session
from . import coach_bp
from app.services.coach.search_coaches import search_coaches

@coach_bp.route("/search", methods=["POST"])
def search_coaches_route():
    """
Search coaches
---
tags:
  - coach
parameters:
  - name: body
    in: body
    required: false
    schema:
      type: object
      properties:
        name:
          type: string
        filters:
          type: array
          items:
            type: string
        is_certified:
          type: boolean
        max_price:
          type: number
        min_rating:
          type: number
        sort_by:
          type: string
          enum:
            - price
            - rating
responses:
  200:
    description: List of coaches
    schema:
      type: object
      properties:
        coaches:
          type: array
          items:
            type: object
  400:
    description: Invalid input
    """
    data = request.get_json()

    name = data.get("name", "")
    filters = data.get("filters", [])
    is_certified = data.get("is_certified", False) 

    max_price = data.get("max_price")
    min_rating = data.get("min_rating")

    sort_by = data.get("sort_by", "price")
    
    try:
        if max_price is not None:
            max_price = float(max_price)
        if min_rating is not None:
            min_rating = float(min_rating)

        coaches = search_coaches(
            name=name, 
            filters=filters, 
            is_certified=is_certified, 
            max_price=max_price, 
            min_rating=min_rating,
            sort_by=sort_by
        )
        
        return jsonify({"coaches": coaches}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500