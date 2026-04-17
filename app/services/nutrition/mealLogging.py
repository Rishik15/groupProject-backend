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


def partialFoodItemUpdate(user_id, food_id, name, calories, protein, carbs, fats, image_url):
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
            commit=False
        )

        for row in rows:
            row["created_at"] = _coerce_db_datetime(row["created_at"]).isoformat()
            row["updated_at"] = _coerce_db_datetime(row["updated_at"]).isoformat()

        return rows

    except Exception as e:
        raise e


def createFoodItem(
    user_id: int,
    name: str,
    cals: int,
    pro: float,
    carbs: float,
    fats: float,
    img: str
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
                "img": img
            },
            fetch=False,
            commit=True
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

        return run_query(
            query=query,
            params=params,
            fetch=True,
            commit=False
        )

    except Exception as e:
        raise e


def _createMeal(
    meal_name: str,
    calories: int,
    protein: float,
    carbs: float,
    fats: float
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
                "fats": fats
            },
            fetch=False,
            commit=True
        )

        created = run_query(
            query="""
                SELECT
                    meal_id,
                    created_at
                FROM meal
                WHERE name = :name
                ORDER BY meal_id DESC
                LIMIT 1
            """,
            params={"name": meal_name},
            fetch=True,
            commit=False
        )

        if not created:
            raise Exception("failed to fetch created meal")

        return created[0]["meal_id"]

    except Exception as e:
        raise e


def mealLogInsert(
    user_id: int,
    meal_name: str,
    eaten_at: str,
    servings: int,
    notes: str | None,
    photo_url: str,
    food_item_ids: list[int]
):
    try:
        eaten_dt = datetime.fromisoformat(eaten_at)

        food_rows = _getFoodItemsForMeal(user_id=user_id, food_item_ids=food_item_ids)

        if len(food_rows) != len(food_item_ids):
            raise ValueError("one or more food items do not exist for this user")

        total_calories = 0
        total_protein = 0.0
        total_carbs = 0.0
        total_fats = 0.0

        for item in food_rows:
            total_calories += int(item["calories"])
            total_protein += float(item["protein"])
            total_carbs += float(item["carbs"])
            total_fats += float(item["fats"])

        meal_id = _createMeal(
            meal_name=meal_name,
            calories=total_calories,
            protein=total_protein,
            carbs=total_carbs,
            fats=total_fats
        )

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
                    :meal_id,
                    NULL,
                    :eaten_at,
                    :servings,
                    :notes,
                    :photo_url
                );
            """,
            params={
                "uid": user_id,
                "meal_id": meal_id,
                "eaten_at": eaten_dt.isoformat(),
                "servings": servings,
                "notes": notes,
                "photo_url": photo_url
            },
            fetch=False,
            commit=True
        )

    except Exception as e:
        raise e


def getLoggedMeals(user_id: int, start_dt: str | None = None, end_dt: str | None = None):
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
                m.name AS meal_name,
                m.calories,
                m.protein,
                m.carbs,
                m.fats
            FROM meal_log AS ml
            LEFT JOIN meal AS m
                ON ml.meal_id = m.meal_id
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

        rows = run_query(
            query=query,
            params=params,
            fetch=True,
            commit=False
        )

        for row in rows:
            row["eaten_at"] = _coerce_db_datetime(row["eaten_at"]).isoformat()
            row["created_at"] = _coerce_db_datetime(row["created_at"]).isoformat()
            row["updated_at"] = _coerce_db_datetime(row["updated_at"]).isoformat()

        return rows

    except Exception as e:
        raise e