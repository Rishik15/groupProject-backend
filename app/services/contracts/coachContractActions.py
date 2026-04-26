from sqlalchemy import false

from app.services import run_query
from datetime import date, datetime


def getCoachContractsService(coach_id: int):
    try:
        ret = run_query(
            """
            SELECT
                ucc.user_id,
                ucc.contract_id,
                ucc.created_at,
                ucc.updated_at,
                ucc.start_date,
                ucc.end_date,
                ucc.agreed_price,
                ucc.contract_text,
                ucc.active
            FROM user_coach_contract AS ucc
            WHERE ucc.coach_id = :c_id
            ORDER BY ucc.created_at DESC;
            """,
            {"c_id": coach_id},
            commit=False,
            fetch=True,
        )
        return ret
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


def getCoachContractsByStatusServie(coach_id: int, active: int):
    try:
        ret = run_query(
            """
            SELECT
                contract_id,
                coach_id,
                user_id,
                agreed_price,
                start_date,
                end_date,
                contract_text,
                active,
                created_at,
                updated_at
            FROM user_coach_contract
            WHERE coach_id = :coach_id
              AND active = :active
            ORDER BY created_at DESC;
            """,
            {"coach_id": coach_id, "active": active},
            commit=False,
            fetch=True,
        )
        return ret
    except Exception as e:
        raise e


def getSingleCoachContractService(coach_id: int, contract_id: int):
    try:
        ret = run_query(
            """
            SELECT
                contract_id,
                coach_id,
                user_id,
                agreed_price,
                start_date,
                end_date,
                contract_text,
                active,
                created_at,
                updated_at
            FROM user_coach_contract
            WHERE coach_id = :coach_id
              AND contract_id = :contract_id
            LIMIT 1;
            """,
            {"coach_id": coach_id, "contract_id": contract_id},
            commit=False,
            fetch=True,
        )
        return ret[0] if ret else None
    except Exception as e:
        raise e


def buildDefaultConversation(contract_id: int, coach_id: int, user_id: int):
    try:

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
                INSERT INTO conversation_member (conversation_id, user_id, role, unread_count)
                VALUES (:conversation_id, :coach_id, 'owner', 1);
            """,
            {"conversation_id": conversation_id, "coach_id": coach_id},
            commit=False,
            fetch=False,
        )

        run_query(
            """
                INSERT INTO conversation_member (conversation_id, user_id, role, unread_count)
                VALUES (:conversation_id, :user_id, 'member', 1);
            """,
            {"conversation_id": conversation_id, "user_id": user_id},
            commit=False,
            fetch=False,
        )

        dt = datetime.now().replace(microsecond=0)

        run_query(
            """
                INSERT INTO message
                (
                    conversation_id, sender_user_id, content, sent_at
                )
                VALUES
                (
                    :conversation_id,
                    :coach_id,
                    'This is the beginning of a great conversation!',
                    :dt
                );
            """,
            {"conversation_id": conversation_id, "dt": dt, "coach_id": coach_id},
            commit=True,
            fetch=False,
        )

        return conversation_id

    except Exception as e:
        raise e

def coachAcceptsContractService(contract_id: int, coach_id: int, user_id: int):
    try:
        today = date.today().isoformat()

        contract = run_query(
            """
            SELECT agreed_price, is_recurring
            FROM user_coach_contract
            WHERE contract_id = :contract_id
            """,
            {"contract_id": contract_id},
            fetch=True, commit=False
        )

        if contract:
            contract     = contract[0]
            is_recurring = contract["is_recurring"]
            agreed_price = contract["agreed_price"]

            run_query(
                """
                UPDATE user_coach_contract
                SET active = 1,
                    start_date = :today,
                    contract_text = :contract_text
                WHERE contract_id = :contract_id;
                """,
                {
                    "contract_id":   contract_id,
                    "today":         today,
                    "contract_text": f"{'Recurring subscription' if is_recurring else 'One-time coaching'} at ${agreed_price}/session. Active from {today}."
                },
                fetch=False,
                commit=True,
            )

            payment_method = run_query(
                """
                SELECT payment_method_id FROM user_payment_method
                WHERE user_id = :user_id AND is_default = 1
                LIMIT 1
                """,
                {"user_id": user_id},
                fetch=True, commit=False
            )

            payment_method_id = payment_method[0]["payment_method_id"] if payment_method else None

            run_query(
                """
                INSERT INTO payment
                    (user_id, coach_id, payment_method_id, amount, currency, status, payment_type, description, paid_at)
                VALUES
                    (:user_id, :coach_id, :payment_method_id, :amount, 'USD', 'completed', :payment_type, :description, NOW())
                """,
                {
                    "user_id":           user_id,
                    "coach_id":          coach_id,
                    "payment_method_id": payment_method_id,
                    "amount":            agreed_price,
                    "payment_type":      "subscription" if is_recurring else "coaching_fee",
                    "description":       f"Monthly subscription to coach #{coach_id}" if is_recurring else f"Coaching fee for contract #{contract_id}"
                },
                fetch=False, commit=True
            )

            if is_recurring:
                run_query(
                    """
                    UPDATE user_coach_contract
                    SET next_billing_date = DATE_ADD(CURDATE(), INTERVAL 1 MONTH)
                    WHERE contract_id = :contract_id
                    """,
                    {"contract_id": contract_id},
                    fetch=False, commit=True
                )

        buildDefaultConversation(contract_id, coach_id, user_id)

    except Exception as e:
        raise e

def coachRejectsContractService(contract_id: int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id;
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True,
        )
    except Exception as e:
        raise e


def coachTerminatesContractService(contract_id: int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 0,
                end_date = :today
            WHERE contract_id = :contract_id;
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True,
        )
    except Exception as e:
        raise e
