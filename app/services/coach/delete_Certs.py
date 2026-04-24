from app.services import run_query

def delete_coach_certification(coach_id: int, cert_id: int):
    try:
        # The WHERE clause ensures the cert belongs to the coach
        run_query(
            """
            DELETE FROM certifications
            WHERE cert_id = :cert_id AND coach_id = :coach_id
            """,
            {
                "cert_id": cert_id,
                "coach_id": coach_id
            },
            fetch=False,
            commit=True
        )
        return True
    except Exception as e:
        raise Exception(f"Failed to delete certification: {str(e)}")