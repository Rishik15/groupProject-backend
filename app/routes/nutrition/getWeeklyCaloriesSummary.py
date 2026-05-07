           user_id=int(user_id),
            user_timezone=_get_session_timezone(),
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
