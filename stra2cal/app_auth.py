import hashlib
import os
from datetime import datetime

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse
from stravalib import Client

from stra2cal.duckdb.connector import DuckDBConnector
from stra2cal.utils.namespace import NAMESPACE

TEMPLATES = Jinja2Templates(directory="stra2cal/login/")


def login(request: Request) -> _TemplateResponse:
    c = Client()
    url = c.authorization_url(
        client_id=NAMESPACE.credentials.STRAVA_CLIENT_ID,
        redirect_uri=os.path.join(NAMESPACE.web_url, "logged_in"),
        approval_prompt="auto",
        scope=["activity:read_all"],
    )
    return TEMPLATES.TemplateResponse(
        name="login.html", context={"request": request, "authorize_url": url}
    )


async def logged_in(
    request: Request, connector: DuckDBConnector
) -> _TemplateResponse:
    error = request.query_params.get("error")
    if error:
        return TEMPLATES.TemplateResponse(
            name="login_error.html",
            context={"request": request, "error": error},
        )
    else:
        code = request.query_params.get("code")
        if code is None:
            raise ValueError("Code is None")
        client = Client()
        access_token = client.exchange_code_for_token(
            client_id=NAMESPACE.credentials.STRAVA_CLIENT_ID,
            client_secret=NAMESPACE.credentials.STRAVA_CLIENT_SECRET,
            code=code,
        )

        # salt is the current timestamp as a string
        now = datetime.now()
        calendar_url = hashlib.sha256(
            (str(now) + access_token["access_token"]).encode("utf-8")
        ).hexdigest()

        connector.write_credentials(calendar_url=calendar_url, **access_token)
        connector.write_metadata(calendar_url=calendar_url, now=now)

        return TEMPLATES.TemplateResponse(
            "login_results.html",
            {
                "request": request,
                "athlete": client.get_athlete(),
                "access_token": access_token,
                "calendar_url": os.path.join(
                    NAMESPACE.web_url, "calendar", calendar_url
                ),
            },
        )


async def refresh_token(
    calendar_url: str, connector: DuckDBConnector
) -> dict[str, str]:
    token = connector.check_if_credentials_exist(calendar_url)
    if token is not None:
        client = Client()
        token_response = client.refresh_access_token(
            client_id=NAMESPACE.credentials.STRAVA_CLIENT_ID,
            client_secret=NAMESPACE.credentials.STRAVA_CLIENT_SECRET,
            refresh_token=token.refresh_token,
        )
        new_access_token = token_response["access_token"]
        new_expires_at = token_response["expires_at"]
        new_refresh_token = token_response["refresh_token"]

        connector.write_credentials(calendar_url=calendar_url, **token_response)
        return {
            "status": "ok",
            "old_token": token.access_token,
            "new_access_token": new_access_token,
            "new_expires_at": str(new_expires_at),
            "new_refresh_token": new_refresh_token,
        }
    else:
        return {"status": "error", "message": ""}


async def update_access_token_if_expired(
    calendar_url: str, connector: DuckDBConnector
) -> None:
    token = connector.check_if_credentials_exist(calendar_url)
    if token is not None:
        expires_at = token.expires_at
        if datetime.now().timestamp() > expires_at:
            await refresh_token(calendar_url, connector)


async def get_latest_request(
    calendar_url: str, connector: DuckDBConnector
) -> datetime:
    return connector.get_latest_request(calendar_url)
