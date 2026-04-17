import json

from app.services import run_query


def get_google_drive_connection():
    rows = run_query(
        """
        SELECT
            connection_id,
            account_scope,
            connected_by_user_id,
            google_email,
            access_token,
            refresh_token,
            token_uri,
            client_id,
            scopes,
            root_folder_id,
            created_at,
            updated_at
        FROM google_drive_oauth_connection
        WHERE account_scope = 'global'
        LIMIT 1
        """,
        fetch=True,
        commit=False,
    )

    if not rows:
        return None

    row = rows[0]
    row["scopes"] = json.loads(row["scopes"]) if row.get("scopes") else []
    return row


def save_google_drive_connection(
    connected_by_user_id: int,
    google_email: str | None,
    access_token: str,
    refresh_token: str | None,
    token_uri: str,
    client_id: str,
    scopes: list[str],
    root_folder_id: str | None,
):
    existing = get_google_drive_connection()

    if existing is None:
        run_query(
            """
            INSERT INTO google_drive_oauth_connection
            (
                account_scope,
                connected_by_user_id,
                google_email,
                access_token,
                refresh_token,
                token_uri,
                client_id,
                scopes,
                root_folder_id
            )
            VALUES
            (
                'global',
                :connected_by_user_id,
                :google_email,
                :access_token,
                :refresh_token,
                :token_uri,
                :client_id,
                :scopes,
                :root_folder_id
            )
            """,
            {
                "connected_by_user_id": connected_by_user_id,
                "google_email": google_email,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_uri": token_uri,
                "client_id": client_id,
                "scopes": json.dumps(scopes),
                "root_folder_id": root_folder_id,
            },
            fetch=False,
            commit=True,
        )
        return

    new_refresh_token = refresh_token if refresh_token else existing.get("refresh_token")

    run_query(
        """
        UPDATE google_drive_oauth_connection
        SET
            connected_by_user_id = :connected_by_user_id,
            google_email = :google_email,
            access_token = :access_token,
            refresh_token = :refresh_token,
            token_uri = :token_uri,
            client_id = :client_id,
            scopes = :scopes,
            root_folder_id = :root_folder_id
        WHERE account_scope = 'global'
        """,
        {
            "connected_by_user_id": connected_by_user_id,
            "google_email": google_email,
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_uri": token_uri,
            "client_id": client_id,
            "scopes": json.dumps(scopes),
            "root_folder_id": root_folder_id,
        },
        fetch=False,
        commit=True,
    )


def clear_google_drive_connection():
    run_query(
        """
        DELETE FROM google_drive_oauth_connection
        WHERE account_scope = 'global'
        """,
        fetch=False,
        commit=True,
    )