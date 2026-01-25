import bcrypt

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        print(f"Error: {e}")
        return False

pw = "1234"
hashed = get_password_hash(pw)
print(f"Hashed: {hashed}")
result = verify_password(pw, hashed)
print(f"Match: {result}")
