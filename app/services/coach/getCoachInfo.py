from .. import run_query
def getCoachInformation(coach_id: int):
    try:
        return run_query(
        """
        SELECT
            ui.first_name,
            ui.last_name,
            c.price,
            c.coach_description,
            um.profile_picture,
            um.weight,
            um.height
        FROM coach AS c
        INNER JOIN users_immutables AS ui
            ON c.coach_id = ui.user_id
        INNER JOIN user_mutables AS um
            ON ui.user_id = um.user_id
        WHERE c.coach_id = :cid;
        """,
        {"cid": coach_id},
        commit=False,
        fetch=True
    )
        return ret
    except Exception as e:
        raise e