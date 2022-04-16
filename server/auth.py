import bcrypt


"""
    if password_match is -1 password is less than 8 characters try again
    if password_match is 0 we know they are trying to register but the passwords dont match
    if password_match is 1 we know they are trying to register and the passwords match!
"""
def check_password_match_and_length(password1, password2):
    if password1 != password2:
        print("password 1 and 2 dont match")
        return 0
    if len(password1) < 8:
        print("the length of password 1 is less than 8")
        return -1
    print("password 1 and 2 do match")
    return 1