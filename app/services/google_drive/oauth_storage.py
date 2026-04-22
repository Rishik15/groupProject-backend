import json

from app.services import run_query


def _normalize_connection_row(row):
    if row is None:
        return None

    row["scopes"] = json.loads(row["scopes"]) if row.get("scopes") else []
    return row


def get_google_drive_connection(account_scope: str = "global", owner_user_id: int | None = None):
    if account_scope == "global":
        rows = run_query(
            """
            SELECT
                connection_id,
                account_scope,
                owner_user_id,
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
    else:
        rows = run_query(
            """
            SELECT
                connection_id,
                account_scope,
                owner_user_id,
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
            WHERE account_scope = 'user'
              AND owner_user_id = :owner_user_id
            LIMIT 1
            """,
            {
                "owner_user_id": owner_user_id,
            },
            fetch=True,
            commit=False,
        )

    if not rows:
        return None

    return _normalize_connection_row(rows[0])


def get_effective_google_drive_connection(user_id: int):
    personal = get_google_drive_connection(
        account_scope="user",
        owner_user_id=user_id,
    )
    if personal is not None:
        return personal

    return get_google_drive_connection(account_scope="global", owner_user_id=None)


def save_google_drive_connection(
    connected_by_user_id: int,
    google_email: str | None,
    access_token: str,
    refresh_token: str | None,
    token_uri: str,
    client_id: str,
    scopes: list[str],
    root_folder_id: str | None,
    account_scope: str = "global",
    owner_user_id: int | None = None,
):
    existing = get_google_drive_connection(
        account_scope=account_scope,
        owner_user_id=owner_user_id,
    )

    if existing is None:
        run_query(
            """
            INSERT INTO google_drive_oauth_connection
            (
                account_scope,
                owner_user_id,
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
                :account_scope,
                :owner_user_id,
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
                "account_scope": account_scope,
                "owner_user_id": owner_user_id,
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

    if account_scope == "global":
        run_query(
            """
            UPDATE google_drive_oauth_connection
            SET
                owner_user_id = NULL,
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
        return

    run_query(
        """
        UPDATE google_drive_oauth_connection
        SET
            account_scope = 'user',
            owner_user_id = :owner_user_id,
            connected_by_user_id = :connected_by_user_id,
            google_email = :google_email,
            access_token = :access_token,
            refresh_token = :refresh_token,
            token_uri = :token_uri,
            client_id = :client_id,
            scopes = :scopes,
            root_folder_id = :root_folder_id
        WHERE account_scope = 'user'
          AND owner_user_id = :owner_user_id
        """,
        {
            "owner_user_id": owner_user_id,
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


def clear_google_drive_connection(account_scope: str = "global", owner_user_id: int | None = None):
    if account_scope == "global":
        run_query(
            """
            DELETE FROM google_drive_oauth_connection
            WHERE account_scope = 'global'
            """,
            fetch=False,
            commit=True,
        )
        return

    run_query(
        """
        DELETE FROM google_drive_oauth_connection
        WHERE account_scope = 'user'
          AND owner_user_id = :owner_user_id
        """,
        {
            "owner_user_id": owner_user_id,
        },
        fetch=False,
        commit=True,
    )