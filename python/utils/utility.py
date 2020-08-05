from datetime import datetime as dt
import subprocess
import secrets
import hashlib

def get_salt():
    return secrets.token_hex(64)


def get_passwordhash(salt, password):
    string = password + salt
    for _ in range(1000):
        string = hashlib.sha256(string.encode()).hexdigest()
    return string


def get_today():
    now = dt.today()
    result = now.strftime('%Y-%m-%d %H:%M:%S')
    return result
