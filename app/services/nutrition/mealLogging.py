from .. import run_query
from datetime import datetime


def _coerce_db_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    raise TypeError("unsupported datetime value returned from db")


def partialFoodItemUpdate(
    user_id, food_id, name, calories, protein, carbs, fats, image_url
):
    try:
        run_query(
            """
                UPDATE food_item
                SET
                    name = :name,
                    calories = :calories,
                    protein = :protein,
                    carbs = :carbs,
                    fats = :fats,
                    image_url = :image_url
                WHERE user_id = :uid AND food_item_id = :food_id
            """,
            {
                "uid": user_id,
                "food_id": food_id,
                "name": name,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
                "image_url": image_url,
            },
            commit=True,
            fetch=False,
        )

    except Exception as e:
        raise e


def getFoodItem(user_id: int):
    try:
        rows = run_query(
            """
                SELECT
                    fi.food_item_id,
                    fi.name,
                    fi.calories,
                    fi.protein,
                    fi.carbs,
                    fi.fats,
                    fi.image_url,
                    fi.created_at,
                    fi.updated_at
                FROM food_item AS fi
                WHERE fi.user_id = :uid
                ORDER BY fi.created_at DESC, fi.food_item_id DESC
            """,
            {"uid": user_id},
            fetch=True,
            commit=False,
        )

        for row in rows:
            row["created_at"] = _coerce_db_datetime(row["created_at"]).isoformat()
            row["updated_at"] = _coerce_db_datetime(row["updated_at"]).isoformat()

        return rows

    except Exception as e:
        raise e


def createFoodItem(
    user_id: int, name: str, cals: int, pro: float, carbs: float, fats: float, img: str
):
    try:
        run_query(
            query="""
                INSERT INTO food_item
                (
                    user_id,
                    name,
                    calories,
                    protein,
                    carbs,
                    fats,
                    image_url
                )
                VALUES
                (
                    :uid,
                    :name,
                    :cals,
                    :pro,
                    :carbs,
                    :fats,
                    :img
                );
            """,
            params={
                "uid": user_id,
                "name": name,
                "cals": cals,
                "pro": pro,
                "carbs": carbs,
                "fats": fats,
                "img": img,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def _getFoodItemsForMeal(user_id: int, food_item_ids: list[int]):
    try:
        placeholders = []
        params = {"uid": user_id}

        for i, fid in enumerate(food_item_ids):
            key = f"fid_{i}"
            placeholders.append(f":{key}")
            params[key] = fid

        query = f"""
            SELECT
                fi.food_item_id,
                fi.name,
                fi.calories,
                fi.protein,
                fi.carbs,
                fi.fats,
                fi.image_url
            FROM food_item AS fi
            WHERE fi.user_id = :uid
              AND fi.food_item_id IN ({",".join(placeholders)})
            ORDER BY fi.food_item_id ASC
        """

        return run_query(query=query, params=params, fetch=True, commit=False)

    except Exception as e:
        raise e


def _createMeal(
    meal_name: str, calories: int, protein: float, carbs: float, fats: float
):
    try:
        run_query(
            query="""
                INSERT INTO meal
                (
                    name,
                    calories,
                    protein,
                    carbs,
                    fats
                )
                VALUES
                (
                    :name,
                    :calories,
                    :protein,
                    :carbs,
                    :fats
                );
            """,
            params={
                "name": meal_name,
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fats": fats,
            },
            fetch=False,
            commit=False,
        )

        created = run_query(
            query="SELECT LAST_INSERT_ID() AS meal_id",
            params={},
            fetch=True,
            commit=False,
        )

        if not created or created[0]["meal_id"] is None:
            raise Exception("failed to fetch created meal id")

        return created[0]["meal_id"]

    except Exception as e:
        raise e


def mealLogInsert(
    user_id: int,
    meal_name: str,
    eaten_at: str,
    servings: int,
    notes: str | None,
    photo_url: str | None,
    food_item_ids: list[int],
):
    try:
        eaten_dt = datetime.fromisoformat(eaten_at)

        if len(food_item_ids) != 1:
            raise ValueError("exactly one food item must be provided")

        food_item_id = food_item_ids[0]

        food_rows = _getFoodItemsForMeal(user_id=user_id, food_item_ids=[food_item_id])

        if not food_rows:
            raise ValueError("food item not found for this user")

        run_query(
            query="""
                INSERT INTO meal_log
                (
                    user_id,
                    meal_id,
                    food_item_id,
                    eaten_at,
                    servings,
                    notes,
                    photo_url
                )
                VALUES
                (
                    :uid,
                    NULL,
                    :food_item_id,
                    :eaten_at,
                    :servings,
                    :notes,
                    :photo_url
                );
            """,
            params={
                "uid": user_id,
                "food_item_id": food_item_id,
                "eaten_at": eaten_dt.isoformat(),
                "servings": servings,
                "notes": notes,
                "photo_url": photo_url,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def getLoggedMeals(
    user_id: int, start_dt: str | None = None, end_dt: str | None = None
):
    try:
        query = """
            SELECT
                ml.log_id,
                ml.user_id,
                ml.meal_id,
                ml.food_item_id,
                ml.eaten_at,
                ml.servings,
                ml.notes,
                ml.photo_url,
                ml.created_at,
                ml.updated_at,
                COALESCE(m.name, fi.name) AS meal_name,
                COALESCE(m.calories, fi.calories) AS calories,
                COALESCE(m.protein, fi.protein) AS protein,
                COALESCE(m.carbs, fi.carbs) AS carbs,
                COALESCE(m.fats, fi.fats) AS fats
            FROM meal_log AS ml
            LEFT JOIN meal AS m
                ON ml.meal_id = m.meal_id
            LEFT JOIN food_item AS fi
                ON ml.food_item_id = fi.food_item_id
            WHERE ml.user_id = :uid
        """

        params = {"uid": user_id}

        if start_dt is not None:
            start_obj = datetime.fromisoformat(start_dt)
            query += " AND ml.eaten_at >= :start_dt"
            params["start_dt"] = start_obj.isoformat()

        if end_dt is not None:
            end_obj = datetime.fromisoformat(end_dt)
            query += " AND ml.eaten_at <= :end_dt"
            params["end_dt"] = end_obj.isoformat()

        query += " ORDER BY ml.eaten_at DESC, ml.log_id DESC"

        rows = run_query(query=query, params=params, fetch=True, commit=False)

        for row in rows:
            row["eaten_at"] = _coerce_db_datetime(row["eaten_at"]).isoformat()
            row["created_at"] = _coerce_db_datetime(row["created_at"]).isoformat()
            row["updated_at"] = _coerce_db_datetime(row["updated_at"]).isoformat()

        return rows

    except Exception as e:
        raise e
