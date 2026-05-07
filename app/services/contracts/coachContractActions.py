from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.services import run_query


def _get_valid_timezone(user_timezone: str | None):
    if not user_timezone:
        return "America/New_York"

    try:
        ZoneInfo(user_timezone)
        return user_timezone
    except ZoneInfoNotFoundError:
        return "America/New_York"


def _get_today_for_user(user_timezone: str | None):
    valid_timezone = _get_valid_timezone(user_timezone)
    return datetime.now(ZoneInfo(valid_timezone)).date().isoformat()


def _utc_now_string():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _format_date(value):
    if value is None:
        return None

    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _format_datetime(value, user_timezone: str | None = None):
    if value is None:
        return None

    if isinstance(value, datetime):
        parsed_datetime = value
    else:
        try:
            parsed_datetime = datetime.fromisoformat(str(value).replace(" ", "T"))
        except (ValueError, TypeError):
            return str(value)

    if parsed_datetime.tzinfo is None:
        parsed_datetime = parsed_datetime.replace(tzinfo=timezone.utc)

    if user_timezone:
        parsed_datetime = parsed_datetime.astimezone(
            ZoneInfo(_get_valid_timezone(user_timezone))
        )

    return parsed_datetime.strftime("%Y-%m-%dT%H:%M:%S")


def parse_contract_text(contract_text):
    details = {
        "training_reason": "",
        "goals": "",
        "preferred_schedule": "",
        "notes": "",
        "payment_type": "",
        "price": "",
        "payment_note": "",
    }

    if not contract_text:
        return details

    parts = str(contract_text).split("|")

    for part in parts:
        if ":" not in part:
            continue

        key, value = part.split(":", 1)
        key = key.strip()
        value = value.strip()

        if key in details:
            details[key] = value

    return details


def get_contract_status_label(contract):
    if contract.get("active") == 1:
        return "active"

    if contract.get("end_date"):
        return "closed"

    return "pending"


def format_contract(contract, user_timezone: str | None = None):
    request_details = parse_contract_text(contract.get("contract_text"))

    formatted_contract = {
        **contract,
        "status": get_contract_status_label(contract),
        "request_details": request_details,
    }

    formatted_contract["start_date"] = _format_date(contract.get("start_date"))
    formatted_contract["end_date"] = _format_date(contract.get("end_date"))
    formatted_contract["created_at"] = _format_datetime(
        contract.get("created_at"),
        user_timezone,
    )
    formatted_contract["updated_at"] = _format_datetime(
        contract.get("updated_at"),
        user_timezone,
    )

    return formatted_contract


def format_contracts(contracts, user_timezone: str | None = None):
    return [format_contract(contract, user_timezone) for contract in contracts]


def getCoachContractsService(coach_id: int, user_timezone: str | None = None):
    try:
        contracts = run_query(
            """
            SELECT
                ucc.user_id,
                ucc.coach_id,
                ucc.contract_id,
                ucc.created_at,
                ucc.updated_at,
                ucc.start_date,
                ucc.end_date,
                ucc.agreed_price,
                ucc.contract_text,
                ucc.active,
                ucc.is_recurring,
                ui.first_name,
                ui.last_name
            FROM user_coach_contract AS ucc
            JOIN users_immutables AS ui
                ON ui.user_id = ucc.user_id
            WHERE ucc.coach_id = :coach_id
            ORDER BY ucc.created_at DESC;
            """,
            {"coach_id": coach_id},
            commit=False,
            fetch=True,
        )

        return format_contracts(contracts or [], user_timezone)

    except Exception as e:
        raise e


def getUsersPerContract(user_id: int):
    try:
        ret = run_query(
            """
            SELECT
                first_name,
                last_name
            FROM users_immutables
            WHERE user_id = :user_id;
            """,
            {"user_id": user_id},
            commit=False,
            fetch=True,
        )

        return ret

    except Exception as e:
        raise e


def getUserGivenContract(contract_id: int):
    try:
        ret = run_query(
            """
            SELECT user_id
            FROM user_coach_contract
            WHERE contract_id = :contract_id;
            """,
            {"contract_id": contract_id},
            commit=False,
            fetch=True,
        )

        return ret

    except Exception as e:
        raise e


def getCoachContractsByStatusService(
    coach_id: int,
    active: int,
    user_timezone: str | None = None,
):
    try:
        contracts = run_query(
            """
            SELECT
                ucc.contract_id,
                ucc.coach_id,
                ucc.user_id,
                ucc.agreed_price,
                ucc.start_date,
                ucc.end_date,
                ucc.contract_text,
                ucc.active,
                ucc.is_recurring,
                ucc.created_at,
                ucc.updated_at,
                ui.first_name,
                ui.last_name
            FROM user_coach_contract AS ucc
            JOIN users_immutables AS ui
                ON ui.user_id = ucc.user_id
            WHERE ucc.coach_id = :coach_id
              AND ucc.active = :active
            ORDER BY ucc.created_at DESC;
            """,
            {"coach_id": coach_id, "active": active},
            commit=False,
            fetch=True,
        )

        return format_contracts(contracts or [], user_timezone)

    except Exception as e:
        raise e


def getSingleCoachContractService(
    coach_id: int,
    contract_id: int,
    user_timezone: str | None = None,
):
    try:
        rows = run_query(
            """
            SELECT
                ucc.contract_id,
                ucc.coach_id,
                ucc.user_id,
                ucc.agreed_price,
                ucc.start_date,
                ucc.end_date,
                ucc.contract_text,
                ucc.active,
                ucc.is_recurring,
                ucc.created_at,
                ucc.updated_at,
                ui.first_name,
                ui.last_name
            FROM user_coach_contract AS ucc
            JOIN users_immutables AS ui
                ON ui.user_id = ucc.user_id
            WHERE ucc.coach_id = :coach_id
              AND ucc.contract_id = :contract_id
            LIMIT 1;
            """,
            {"coach_id": coach_id, "contract_id": contract_id},
            commit=False,
            fetch=True,
        )

        return format_contract(rows[0], user_timezone) if rows else None

    except Exception as e:
        raise e


def buildDefaultConversation(contract_id: int, coach_id: int, user_id: int):
    try:
        existing_conversation = run_query(
            """
            SELECT c.conversation_id
            FROM conversation AS c
            JOIN conversation_member AS coach_member
                ON coach_member.conversation_id = c.conversation_id
                AND coach_member.user_id = :coach_id
            JOIN conversation_member AS client_member
                ON client_member.conversation_id = c.conversation_id
                AND client_member.user_id = :user_id
            WHERE c.conversation_type = 'dm'
            LIMIT 1;
            """,
            {"coach_id": coach_id, "user_id": user_id},
            commit=False,
            fetch=True,
        )

        if existing_conversation:
            return int(existing_conversation[0]["conversation_id"])

        run_query(
            """
            INSERT INTO conversation (conversation_type, created_by, title)
            VALUES ('dm', :coach_id, NULL);
            """,
            {"coach_id": coach_id},
            commit=False,
            fetch=False,
        )

        conversation_id_raw = run_query(
            """
            SELECT LAST_INSERT_ID() AS conversation_id;
            """,
            {},
            commit=False,
            fetch=True,
        )

        if (
            not conversation_id_raw
            or conversation_id_raw[0].get("conversation_id") is None
        ):
            raise ValueError("Error inserting into conversation table")

        conversation_id = int(conversation_id_raw[0]["conversation_id"])

        run_query(
            """
            INSERT INTO conversation_member
                (conversation_id, user_id, role, unread_count)
            VALUES
                (:conversation_id, :coach_id, 'owner', 1);
            """,
            {"conversation_id": conversation_id, "coach_id": coach_id},
            commit=False,
            fetch=False,
        )

        run_query(
            """
            INSERT INTO conversation_member
                (conversation_id, user_id, role, unread_count)
            VALUES
                (:conversation_id, :user_id, 'member', 1);
            """,
            {"conversation_id": conversation_id, "user_id": user_id},
            commit=False,
            fetch=False,
        )

        run_query(
            """
            INSERT INTO message
                (conversation_id, sender_user_id, content, sent_at)
            VALUES
                (
                    :conversation_id,
                    :coach_id,
                    'This is the beginning of a great conversation!',
                    :sent_at
                );
            """,
            {
                "conversation_id": conversation_id,
                "sent_at": _utc_now_string(),
                "coach_id": coach_id,
            },
            commit=True,
            fetch=False,
        )

        return conversation_id

    except Exception as e:
        raise e


def coachAcceptsContractService(
    contract_id: int,
    coach_id: int,
    user_id: int,
    user_timezone: str | None = None,
):
    try:
        today = _get_today_for_user(user_timezone)

        contract = run_query(
            """
            SELECT
                is_recurring
            FROM user_coach_contract
            WHERE contract_id = :contract_id
              AND coach_id = :coach_id
              AND user_id = :user_id
            LIMIT 1;
            """,
            {
                "contract_id": contract_id,
                "coach_id": coach_id,
                "user_id": user_id,
            },
            fetch=True,
            commit=False,
        )

        if not contract:
            raise Exception("Contract not found")

        is_recurring = contract[0]["is_recurring"]

        run_query(
            """
            UPDATE user_coach_contract
            SET active = 1,
                start_date = :today,
                next_billing_date =
                    CASE
                        WHEN :is_recurring = 1
                        THEN DATE_ADD(:today, INTERVAL 1 MONTH)
                        ELSE NULL
                    END
            WHERE contract_id = :contract_id
              AND coach_id = :coach_id
              AND user_id = :user_id;
            """,
            {
                "contract_id": contract_id,
                "coach_id": coach_id,
                "user_id": user_id,
                "today": today,
                "is_recurring": 1 if is_recurring else 0,
            },
            fetch=False,
            commit=True,
        )

        buildDefaultConversation(contract_id, coach_id, user_id)

    except Exception as e:
        raise e


def coachRejectsContractService(
    contract_id: int,
    user_timezone: str | None = None,
):
    try:
        today = _get_today_for_user(user_timezone)

        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id;
            """,
            {
                "contract_id": contract_id,
                "today": today,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e


def coachTerminatesContractService(
    contract_id: int,
    user_timezone: str | None = None,
):
    try:
        today = _get_today_for_user(user_timezone)

        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id;
            """,
            {
                "contract_id": contract_id,
                "today": today,
            },
            fetch=False,
            commit=True,
        )

    except Exception as e:
        raise e
