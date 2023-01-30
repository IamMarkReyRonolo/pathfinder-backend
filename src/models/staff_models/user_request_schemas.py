import sys, os, pdb, json, imp, re, typing
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from pydantic import BaseModel, root_validator
from typing import Optional, List

def is_not_empty(cls, values):
    for attr, value in values.items():
        if (attr != "code"):
            if(value == ""):
                raise ValueError(f'{attr} field should not be empty')

    return values


class LogIn(BaseModel):
    username: str
    password: str
    _no_empty_required_fields = root_validator(allow_reuse=True)(is_not_empty)


class Registration(BaseModel):
    full_name: str
    username: str
    password: str
    _no_empty_required_fields = root_validator(allow_reuse=True)(is_not_empty)

class RoomSession(BaseModel):
    room_code: str
    users_responded: Optional[List[str]]
    users_requested: Optional[List[str]]

class Notification(BaseModel):
    notification_title: str
    notification_message: str
    friend_ids: List[str]
    code: Optional[str]
    _no_empty_required_fields = root_validator(allow_reuse=True)(is_not_empty)



