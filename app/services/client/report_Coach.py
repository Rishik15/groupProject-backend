from app.services import run_query

def create_user_report(reporter_id: int, reported_id: int, reason_text: str):
    try:
        run_query(
            """
            INSERT INTO user_report (reported_user_id, reporter_user_id, reason)
            VALUES (:reported, :reporter, :reason)
            """,
            {
                "reported": reported_id,
                "reporter": reporter_id,
                "reason": reason_text
            },
            fetch=False,
            commit=True
        )
        return True
    except Exception as e:
        raise Exception(f"Failed to submit report: {str(e)}")