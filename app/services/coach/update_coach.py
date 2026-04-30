from app.services import run_query


def _create_price_change_request(coach_id: int, proposed_price):
    if proposed_price is None or proposed_price == "":
        raise ValueError("price is required")

    try:
        proposed_price = float(proposed_price)
    except Exception:
        raise ValueError("price must be a valid number")

    if proposed_price < 0:
        raise ValueError("price cannot be negative")

    coach_rows = run_query(
        """
        SELECT coach_id, price
        FROM coach
        WHERE coach_id = :coach_id
        """,
        params={"coach_id": coach_id},
        fetch=True,
        commit=False,
    )

    if not coach_rows:
        raise ValueError("Coach not found")

    current_price = float(coach_rows[0]["price"])

    if current_price == proposed_price:
        return {
            "message": "Price is already set to this amount",
            "request_created": False,
        }

    pending_rows = run_query(
        """
        SELECT request_id
        FROM coach_price_change_request
        WHERE coach_id = :coach_id
        AND status = 'pending'
        LIMIT 1
        """,
        params={"coach_id": coach_id},
        fetch=True,
        commit=False,
    )

    if pending_rows:
        raise ValueError("You already have a pending price change request")

    request_id = run_query(
        """
        INSERT INTO coach_price_change_request
        (
            coach_id,
            proposed_price,
            status
        )
        VALUES
        (
            :coach_id,
            :proposed_price,
            'pending'
        )
        """,
        params={
            "coach_id": coach_id,
            "proposed_price": proposed_price,
        },
        fetch=False,
        commit=True,
        return_lastrowid=True,
    )

    return {
        "message": "Price change request submitted for admin review",
        "request_created": True,
        "request_id": request_id,
        "proposed_price": proposed_price,
    }


def update_coach_profile(coach_id, update_json):
    if not coach_id:
        raise ValueError("Unauthorized")

    if not update_json:
        return {
            "message": "No valid fields provided",
            "profile_updated": False,
            "price_request_created": False,
        }

    response = {
        "message": "Profile updated successfully",
        "profile_updated": False,
        "price_request_created": False,
        "price_request": None,
    }

    if "coach_description" in update_json:
        run_query(
            """
            UPDATE coach
            SET coach_description = :coach_description
            WHERE coach_id = :coach_id
            """,
            params={
                "coach_description": update_json["coach_description"],
                "coach_id": int(coach_id),
            },
            fetch=False,
            commit=True,
        )

        response["profile_updated"] = True

    if "price" in update_json:
        price_request = _create_price_change_request(
            coach_id=int(coach_id),
            proposed_price=update_json["price"],
        )

        response["price_request"] = price_request
        response["price_request_created"] = price_request.get(
            "request_created",
            False,
        )

    if not response["profile_updated"] and not response["price_request"]:
        response["message"] = "No valid fields provided"

    if response["profile_updated"] and response["price_request_created"]:
        response["message"] = (
            "Profile updated. Price change request submitted for admin review."
        )
    elif response["profile_updated"]:
        response["message"] = "Profile updated successfully"
    elif response["price_request_created"]:
        response["message"] = "Price change request submitted for admin review"
    elif response["price_request"]:
        response["message"] = response["price_request"]["message"]

    return response
