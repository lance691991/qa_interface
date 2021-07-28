import asyncio
import json
import typing
import urllib.parse
from datetime import datetime, timedelta
from typing import Any, Union

import aiohttp
import requests
from fastapi import HTTPException, Request
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


class ServiceAuthenticator(object):
    """Service Authenticator"""

    def __init__(
        self,
        service_name: str,
        *,
        dapr_http_base_url: str = 'http://127.0.0.1:3500',
        auth_service_name: str = 'authorization',
        auth_service_method: str = 'service_auth',
    ):
        self.service_name = service_name
        self.auth_service_name = auth_service_name
        self.auth_service_method = auth_service_method
        self.dapr_http_base_url = dapr_http_base_url
        self.dapr_http_url = urllib.parse.urljoin(
            self.dapr_http_base_url, 'v1.0/invoke/' + self.auth_service_name + '/method/' + self.auth_service_method
        )

    async def auth(self, req: Request, data: typing.Optional[dict] = None, *, is_json: bool = True) -> None:
        """Auth service method"""

        headers = dict(req.headers.mutablecopy())
        # Remove invalid headers to avoid aiohttp.Client send block
        for header_name in ['content-length', 'host', 'connection']:
            headers.pop(header_name, None)

        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

        body = data
        if body is None and is_json:
            try:
                body = await req.json()
            except Exception as e:
                raise HTTPException(detail='invalid json request', status_code=400)

        method = req.scope.get('path', '')
        if len(method) > 0:
            method = method[1:]

        data = {
            'service': self.service_name,
            'method': method,
            'verb': req.method.lower(),
            'query': dict(req.query_params),
            'data': body
        }

        try:
            resp = await session.post(
                self.dapr_http_url,
                json=data,
                headers=headers
            )
        except Exception as e:
            raise HTTPException(detail=str(e), status_code=500)

        if resp.status == 200:
            d = await resp.json()
            if d['result']:
                return

            # auth failed
            raise HTTPException(status_code=403, detail="auth failed")

        # request failed
        raise HTTPException(status_code=500, detail="invoke authorization service failed")
