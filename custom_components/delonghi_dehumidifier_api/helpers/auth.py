"""Auth (Gigya OIDC + Ayla tokens)."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from typing import Any

import aiohttp

from ..const import (
    API_KEY,
    APP_ID,
    APP_SECRET,
    AYLA_REFRESH_TOKEN_URL,
    AYLA_TOKEN_SIGN_IN_URL,
    BROWSER_USER_AGENT,
    CLIENT_ID,
    CONSENT_SIGNATURE_PREFIX,
    CONSENT_SIGNATURE_SUFFIX,
    DELONGHI_CONSENT_URL,
    DELONGHI_OIDC_PAGE_URL,
    GIGYA_AUTHORIZE_CONTINUE_URL,
    GIGYA_AUTHORIZE_URL,
    GIGYA_FORMAT_JSON,
    GIGYA_GET_IDS_URL,
    GIGYA_GET_USER_INFO_URL,
    GIGYA_LOGIN_URL,
    GIGYA_RISK_CONTEXT_BASE,
    GIGYA_SDK,
    GIGYA_SESSION_EXPIRATION,
    GIGYA_TOKEN_URL,
    HTTP_OK,
    OAUTH_REDIRECT_URI,
    OAUTH_SCOPE,
    OAUTH_SCOPE_PLUS,
    SDK_BUILD,
    TIME_FORMAT_HMS,
)
from .headers import (
    browser_headers,
    token_form_headers,
    token_json_headers,
    token_user_agent_headers,
)
from .urls import get_query_param, url_encode

_LOGGER = logging.getLogger(__name__)


class AylaAuth:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        language: str,
        email: str,
        password: str,
    ) -> None:
        self.session = session
        self.language = language
        self.email = email
        self.password = password
        self.refresh_token: str | None = None
        self.access_token: str | None = None
        self.token_expiry = time.time()

    async def get_access_token(self) -> str | None:
        if (
            self.access_token is not None
            and self.access_token != ""
            and self.token_expiry > time.time()
        ):
            return self.access_token
        return await self._refresh_or_login()

    async def _refresh_or_login(self) -> str | None:
        if self.refresh_token is None or self.refresh_token == "":
            return await self._full_login()
        return await self._refresh_access_token()

    async def _refresh_access_token(self) -> str | None:
        body = {"user": {"refresh_token": self.refresh_token}}
        http_resp = await self.session.post(
            AYLA_REFRESH_TOKEN_URL, headers=token_json_headers(), json=body
        )
        if http_resp.status != HTTP_OK:
            body_text = await http_resp.text()
            _LOGGER.error(
                "Failed retrieving new access token HTTP %s: %s",
                http_resp.status,
                body_text,
            )
            return await self._full_login()

        data = await http_resp.json()
        self._store_tokens(data)
        return self.access_token

    async def _full_login(self) -> str | None:
        headers = browser_headers()

        params = {
            "client_id": CLIENT_ID,
            "response_type": "code",
            "redirect_uri": OAUTH_REDIRECT_URI,
            "scope": OAUTH_SCOPE,
            "nonce": str(int(datetime.now().timestamp())),
        }
        response = await self.session.get(
            GIGYA_AUTHORIZE_URL, headers=headers, params=params, allow_redirects=False
        )
        context = get_query_param(response.headers.get("Location"), "context")

        ids_params: dict[str, Any] = {
            "APIKey": API_KEY,
            "includeTicket": "true",
            "pageURL": DELONGHI_OIDC_PAGE_URL,
            "sdk": GIGYA_SDK,
            "sdkBuild": SDK_BUILD,
            "format": GIGYA_FORMAT_JSON,
        }
        http_resp = await self.session.get(
            GIGYA_GET_IDS_URL, headers=headers, params=ids_params
        )
        response = json.loads(await http_resp.text())
        ucid = response["ucid"]
        gmid = response["gmid"]
        gmid_ticket = response["gmidTicket"]

        risk_context = {
            **GIGYA_RISK_CONTEXT_BASE,
            "b6": BROWSER_USER_AGENT,
            "b8": datetime.now().strftime(TIME_FORMAT_HMS),
        }
        data = {
            "loginID": self.email,
            "password": self.password,
            "sessionExpiration": GIGYA_SESSION_EXPIRATION,
            "targetEnv": "jssdk",
            "include": "profile,data,emails,subscriptions,preferences",
            "includeUserInfo": "true",
            "loginMode": "standard",
            "lang": self.language,
            "riskContext": url_encode(json.dumps(risk_context)),
            "APIKey": API_KEY,
            "source": "showScreenSet",
            "sdk": GIGYA_SDK,
            "authMode": "cookie",
            "pageURL": DELONGHI_OIDC_PAGE_URL,
            "gmid": gmid,
            "ucid": ucid,
            "sdkBuild": SDK_BUILD,
            "format": GIGYA_FORMAT_JSON,
        }
        http_resp = await self.session.post(GIGYA_LOGIN_URL, headers=headers, data=data)
        response = json.loads(await http_resp.text())

        if "sessionInfo" not in response:
            _LOGGER.error(
                "Gigya login failed (no sessionInfo). language=%s keys=%s error=%s",
                self.language,
                list(response.keys()) if isinstance(response, dict) else type(response),
                response.get("errorMessage")
                or response.get("errorDetails")
                or response.get("statusReason")
                or response,
            )
            return None

        login_token = response["sessionInfo"]["login_token"]

        data = {
            "enabledProviders": "*",
            "APIKey": API_KEY,
            "sdk": GIGYA_SDK,
            "login_token": login_token,
            "authMode": "cookie",
            "pageURL": DELONGHI_OIDC_PAGE_URL,
            "gmid": gmid,
            "ucid": ucid,
            "sdkBuild": SDK_BUILD,
            "format": GIGYA_FORMAT_JSON,
        }
        http_resp = await self.session.post(
            GIGYA_GET_USER_INFO_URL, headers=headers, data=data
        )
        response = json.loads(await http_resp.text())
        user_uid = response["UID"]
        user_uid_signature = response["UIDSignature"]
        user_signature_timestamp = response["signatureTimestamp"]

        params = {
            "lang": self.language,
            "context": context or "",
            "clientID": CLIENT_ID,
            "scope": OAUTH_SCOPE_PLUS,
            "UID": user_uid,
            "UIDSignature": user_uid_signature,
            "signatureTimestamp": user_signature_timestamp,
        }
        http_resp = await self.session.get(
            DELONGHI_CONSENT_URL, headers=headers, params=params
        )
        html = await http_resp.text()
        signature = html.split(CONSENT_SIGNATURE_PREFIX)[1].split(
            CONSENT_SIGNATURE_SUFFIX
        )[0]

        params = {
            "context": context or "",
            "login_token": login_token,
            "consent": json.dumps(
                {
                    "scope": OAUTH_SCOPE,
                    "clientID": CLIENT_ID,
                    "context": context,
                    "UID": user_uid,
                    "consent": True,
                },
                separators=(",", ":"),
            ),
            "sig": signature,
            "gmidTicket": gmid_ticket,
        }
        response = await self.session.get(
            GIGYA_AUTHORIZE_CONTINUE_URL,
            headers=headers,
            params=params,
            allow_redirects=False,
        )
        code = get_query_param(response.headers.get("Location"), "code")

        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": OAUTH_REDIRECT_URI,
        }
        http_resp = await self.session.post(
            GIGYA_TOKEN_URL, headers=token_form_headers(), data=data
        )
        response = json.loads(await http_resp.text())
        idp_token = response["access_token"]

        data = {
            "app_id": APP_ID,
            "app_secret": APP_SECRET,
            "token": idp_token,
        }
        http_resp = await self.session.post(
            AYLA_TOKEN_SIGN_IN_URL, headers=token_user_agent_headers(), data=data
        )
        response = json.loads(await http_resp.text())
        self._store_tokens(response)
        return self.access_token

    def _store_tokens(self, data: dict) -> None:
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.token_expiry = time.time() + int(data["expires_in"])
