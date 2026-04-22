from app import bcrypt

passwords = ["Rishik@1"]

for p in passwords:
    print(p, "->", bcrypt.generate_password_hash(p).decode("utf-8"))