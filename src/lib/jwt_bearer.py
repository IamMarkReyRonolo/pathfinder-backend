import sys, os
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
from lib import jwt_handler
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, ):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        credentials.credentials = credentials.credentials.replace('"', "")
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token.")

            request.state.user_details = jwt_handler.decodeJWT(
                credentials.credentials)
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid = False

        try:
            payload = jwt_handler.decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
