
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class PasswordHandler:



    def __init__(self):
        pass

    def hash_password(self, password: str) -> str:
        with open("security_debug.txt", "a") as f:
            f.write(f"Hashing: {password} with len {len(password)}\n")
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pwd_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(pwd_bytes, hashed_bytes)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

class JWTHandler:

    def __init__(self):

        self._secret_key = settings.secret_key
        self._algorithm = settings.algorithm
        self._expire_minutes = settings.access_token_expire_minutes

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:

        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self._expire_minutes)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            self._secret_key,
            algorithm=self._algorithm
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:

        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification error: {e}")
            return None

    def decode_token(self, token: str) -> Optional[str]:

        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None

password_handler = PasswordHandler()
jwt_handler = JWTHandler()

def hash_password(password: str) -> str:

    return password_handler.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:

    return password_handler.verify_password(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:

    return jwt_handler.create_access_token(data, expires_delta)

def verify_token(token: str) -> Optional[Dict[str, Any]]:

    return jwt_handler.verify_token(token)
