import datetime
import hashlib
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from starlette.templating import _TemplateResponse
from stravalib import Client

from stra2ics.duckdb.connector import DuckDBConnector
from stra2ics.pretty_json import PrettyJSONResponse
from stra2ics.utils.namespace import NAMESPACE


class Settings(BaseSettings):
    strava_client_id: int
    strava_client_secret: str


SETTINGS = Settings()  # type: ignore
APP = FastAPI()
TEMPLATES = Jinja2Templates(directory="stra2ics/login/")
DuckDBConnector = DuckDBConnector()


@APP.route("/login")
def login(request: Request) -> _TemplateResponse:
    c = Client()
    url = c.authorization_url(
        client_id=SETTINGS.strava_client_id,
        redirect_uri=os.path.join(NAMESPACE.web_url, "logged_in"),
        approval_prompt="auto",
        scope=["activity:read_all"],
    )
    return TEMPLATES.TemplateResponse(
        name="login.html", context={"request": request, "authorize_url": url}
    )


@APP.get("/logged_in", response_class=HTMLResponse)
async def logged_in(request: Request) -> _TemplateResponse:
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
            client_id=SETTINGS.strava_client_id,
            client_secret=SETTINGS.strava_client_secret,
            code=code,
        )

        # salt is the current timestamp as a string
        now = datetime.datetime.now()
        calendar_url = hashlib.sha256(
            (str(now) + access_token["access_token"]).encode("utf-8")
        ).hexdigest()

        DuckDBConnector.write_credentials(
            calendar_url=calendar_url, **access_token
        )
        DuckDBConnector.write_metadata(calendar_url=calendar_url, now=now)

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


@APP.get("/refresh_token/{calendar_url}")
async def refresh_token(calendar_url: str) -> dict[str, str]:
    tokens = DuckDBConnector.check_if_credentials_exist(calendar_url)
    if tokens is not None:
        client = Client()
        token_response = client.refresh_access_token(
            client_id=SETTINGS.strava_client_id,
            client_secret=SETTINGS.strava_client_secret,
            refresh_token=tokens[2],
        )
        new_access_token = token_response["access_token"]
        new_expires_at = token_response["expires_at"]
        new_refresh_token = token_response["refresh_token"]

        DuckDBConnector.write_credentials(
            calendar_url=calendar_url, **token_response
        )
        return {
            "status": "ok",
            "old_token": tokens[1],
            "new_access_token": new_access_token,
            "new_expires_at": str(new_expires_at),
            "new_refresh_token": new_refresh_token,
        }
    else:
        return {"status": "error", "message": ""}


@APP.get("/update_access_tokens_if_expired/{calendar_url}")
async def update_access_tokens_if_expired(calendar_url: str) -> None:
    tokens = DuckDBConnector.check_if_credentials_exist(calendar_url)
    if tokens is not None:
        expires_at = tokens[3]
        if datetime.datetime.now().timestamp() > expires_at:
            await refresh_token(calendar_url)


@APP.get("/get_latest_request/{calendar_url}")
async def get_latest_request(calendar_url: str) -> datetime.datetime:
    return DuckDBConnector.get_latest_request(calendar_url)


@APP.get("/calendar/{calendar_url}", response_class=PrettyJSONResponse)
async def calendar(calendar_url: str) -> dict[str, Any]:
    await update_access_tokens_if_expired(calendar_url)
    tokens = DuckDBConnector.check_if_credentials_exist(calendar_url)
    if tokens is not None:
        client = Client(access_token=tokens[1])

        DuckDBConnector.write_metadata(
            calendar_url=calendar_url, now=datetime.datetime.now()
        )
        return {
            f"activity {i}": {
                "start_date": activity.start_date,
                "name": activity.name,
                "duration": activity.elapsed_time,
                "description": activity.description,
            }
            for i, activity in enumerate(
                client.get_activities(limit=4, before=datetime.datetime.now())
            )
        }
    else:
        return {"status": "error", "message": ""}
