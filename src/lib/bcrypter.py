
import sys, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
import time

class Hasher():
    def __init__(self):
        pass      

    def hash_password(self, password: str):
        password_encoded = password.encode('utf-8')        
        return pwd_context.hash(password_encoded)                
    
    def verify_password(self, login_password, member_password):
        matched: bool = False
        try:                                        
            if pwd_context.verify(login_password.encode('utf-8'), member_password.encode('utf-8')):
                matched = True
        except Exception as error:
            print(f"Hasher(): Error: {error}")            
        return matched