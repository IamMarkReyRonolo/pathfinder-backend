import sys, os, json, cryptocode
from jose import JWTError, jwt
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from os import access
from typing import Dict
import time

PAYLOAD_SECRET = 'ubF5I41SuaVY2wmTnz43qA'
JWT_SECRET = "3a2c3158a8a428c1a0c1998360f7e452"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "access_token": token
    }

# function used for signing the JWT string


def encodePayload(payload):
    converted = json.dumps(payload)
    encoded_text = cryptocode.encrypt(converted, PAYLOAD_SECRET)

    return encoded_text


def decodePayload(payload):
    decoded = cryptocode.decrypt(payload, PAYLOAD_SECRET)
    return decoded


def signJWT(uuid: str, name: str) -> Dict[str, str]:
    expiration_duration = 60 * 60 * 24
    data = {
        "uuid": uuid, 
        "name": name,
        "expires": time.time() + expiration_duration
    }

    payload = {
        'data': encodePayload(data)
    }
    token = jwt.encode(payload, JWT_SECRET,
                       algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        decoded_payload = json.loads(decodePayload(decoded_token['data']))

        if decoded_payload["expires"] >= time.time():
            return decoded_payload
        else:
            return None
    except:
        return {}
