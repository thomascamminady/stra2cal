import datetime
import hashlib
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from starlette.templating import _TemplateResponse
from stravalib import Client

from stra2ics.duckdb.connector import DuckDBConnector
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
        calendar_url = os.path.join(
            NAMESPACE.web_url,
            "calendar",
            hashlib.sha256(
                (str(now) + access_token["access_token"]).encode("utf-8")
            ).hexdigest(),
        )

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
                "calendar_url": calendar_url,
            },
        )


@APP.get("/calendar/{calendar_url}")
async def calendar(calendar_url: str) -> dict[str, str]:
    if DuckDBConnector.check_if_credentials_exist(calendar_url):
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Calendar not found"}
