import bcrypt
import server.database as db
import secrets
import hashlib
import base64

"""
    if password_match is -1 password is less than 8 characters try again
    if password_match is 0 we know they are trying to register but the passwords dont match
    if password_match is 1 we know they are trying to register and the passwords match!
"""
def check_password_match_and_length(password1, password2) -> int:
    if password1 != password2:
        print("password 1 and 2 dont match")
        return 0
    if len(password1) < 8:
        print("the length of password 1 is less than 8")
        return -1
    print("password 1 and 2 do match")
    return 1

"""
Go to auth.py file to create these hashes and salt
1. generate some salt from bcrypt
2. hash the password 
• Randomly generate salt, appended to password
• Hash the salted password
"""
def generateSalt() -> bytes:
    salt = bcrypt.gensalt(15)
    return salt

def generate_new_hashed_password_with_salt(salt: bytes, untouchedPassword: bytes) -> bytes:
    # first append the salt to the end of the users password
    hashedSaltedPassword = bcrypt.hashpw(untouchedPassword, salt)
    return hashedSaltedPassword



def store_user_and_password(hashSaltedPassword: bytes, username: bytes, salt: bytes) -> None:
    db.store_passwords(hashSaltedPassword, username, salt)

def find_user_in_collection(username: bytes):
    user = db.find_username_in_password_collection(username)
    if user:
        return user
    else:
        return None

def generate_auth_token() -> str:
    auth_token = secrets.token_urlsafe(30)
    return auth_token

def store_auth_token_auth(authT: bytes, username: bytes):
    db.store_auth_token(authT, username)

def find_auth_token_in_collection(auth_token):
    print("we are in find_auth_token_in_collection in the auth.py file")
    print("this is the auth_token : ", auth_token, flush=True)
    # wait I don't want to generate a new hash with a normal auth_token from the headers I 
    hashed_token= generate_hash_for_auth_token(auth_token)
    print("this is the hashed token: ", hashed_token)
    auth_token_dict = db.retrieve_auth_token(hashed_token)
    print("this is the auth_token_dict if it is in the db, ", auth_token_dict)
    if auth_token_dict:
        # means the auth_token was a match
        # get user name from dict that matches
        username = auth_token_dict["username"]
        return username
    else:
        return None

def generate_hash_for_auth_token(auth_token):
    hash_token = hashlib.sha256(auth_token.encode()).hexdigest()
    return hash_token