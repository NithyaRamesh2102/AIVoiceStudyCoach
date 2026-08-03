"""
OAuth2 bearer scheme used by dependencies to extract the token from
the Authorization header.
"""
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
