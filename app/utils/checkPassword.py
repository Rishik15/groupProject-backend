from app import bcrypt

stored_hash = "$2b$12$7RLskAPYg.QqaTnf4lHGXO1MvsXs.BINL5QhChxfUfDfPyKcAW4L2"

print(bcrypt.check_password_hash(stored_hash, "Rishik@1"))
