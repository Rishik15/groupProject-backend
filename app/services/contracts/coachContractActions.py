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
            fetch=True
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
            fetch=True
        )
        return ret
    except Exception as e:
        raise e

def getUserGivenContract(contract_id: int):
    try:
        ret = run_query(
            """
                SELECT user_id from user_coach_contract where contract_id = :contract_id;
            """
            , {"contract_id": contract_id},
            commit= False, fetch=True

        )

        return ret
    except Exception as e : 
        raise e

def getCoachContractsByStatusService(coach_id: int, active: int):
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
            fetch=True
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
            fetch=True
        )
        return ret[0] if ret else None
    except Exception as e:
        raise e


def coachAcceptsContractService(contract_id: int, coach_id: int, user_id : int):
    try:
        today = date.today().isoformat()
        run_query(
            """
            UPDATE user_coach_contract
            SET active = 1,
                start_date = :today
            WHERE contract_id = :contract_id;
            """,
            {"contract_id": contract_id, "today": today},
            fetch=False,
            commit=True
        )
        run_query(
            """
                INSERT INTO conversation 
                (conversation_type, created_by, title)              
                VALUES ('dm', :coach_id, NULL); 
            """,
            {"coach_id": coach_id},
            commit=True, 
            fetch=False
        )
        conversation_id = run_query (
            """
                (SELECT LAST_INSERT_ID() as conversation_id);
            """, {}, commit=False, fetch=True
        )[0]["conversation_id"]

        run_query(
            """
            INSERT INTO conversation_member (conversation_id, user_id, role, unread_count)
            VALUES (:conversation_id, :coach_id, 'owner', 1);
            """,
            {
                "conversation_id": conversation_id,
                "coach_id": coach_id,
            },
            commit=True,
            fetch=False
        )

        run_query(
            """
            INSERT INTO conversation_member (conversation_id, user_id, role, unread_count)
            VALUES (:conversation_id, :user_id, 'member', 1);
            """,
            {
                "conversation_id": conversation_id,
                "user_id": user_id,
            },
            commit=True,
            fetch=False
        )
        
        dt = datetime.now() 
        ms = str(dt.time()).split(".")[1]
        dt = str(dt).replace(ms, "")
        dt = str(dt).replace(".", "")

        run_query (
            """
                INSERT INTO message 
                (
                    conversation_id, sender_user_id, content, sent_at
                ) 
                VALUES 
                (
                    :conversation_id, 1, 'This is the beginning of a great relationship! Conversations can be managed here!', :dt
                );
            """,
            {"conversation_id": conversation_id, "dt": dt}, 
            commit=True, 
            fetch=False
        )
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
            commit=True
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
            commit=True
        )
    except Exception as e:
        raise e