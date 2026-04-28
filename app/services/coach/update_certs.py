from app.services import run_query

def update_coach_certification(coach_id: int, cert_id: int, cert_name: str, provider: str, description: str = None, expires_date: str = None):
    try:
        run_query(
            """
            UPDATE certifications
            SET 
                cert_name = :name,
                provider_name = :provider,
                description = :desc,
                expires_date = :expires
            WHERE cert_id = :cert_id AND coach_id = :coach_id
            """,
            {
                "name": cert_name,
                "provider": provider,
                "desc": description,
                "expires": expires_date,
                "cert_id": cert_id,
                "coach_id": coach_id
            },
            fetch=False,
            commit=True
        )
        return True
    except Exception as e:
        raise Exception(f"Failed to update certification: {str(e)}")