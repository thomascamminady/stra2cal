from datetime import datetime
from typing import Any

import uvicorn
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import PlainTextResponse
from stravalib import Client

from stra2ics.app_auth import (
    logged_in,
    login,
    refresh_token,
    update_access_token_if_expired,
)
from stra2ics.duckdb.connector import DuckDBConnector
from stra2ics.utils.calendar_helper import activities_to_calendar
from stra2ics.utils.namespace import NAMESPACE
from stra2ics.utils.pretty_json import PrettyJSONResponse

APP = FastAPI()
ROUTER = APIRouter()
DuckDBConnector = DuckDBConnector()


@APP.get("/")
async def root():
    return {"message": "Hello, World!"}


ROUTER.add_api_route(
    path="/login",
    endpoint=login,
)


def _logged_in(request: Request):
    return logged_in(request, DuckDBConnector)


ROUTER.add_api_route(
    path="/logged_in",
    endpoint=_logged_in,
)


def _update_access_token_if_expired(
    calendar_url: str,
):
    return update_access_token_if_expired(calendar_url, DuckDBConnector)


ROUTER.add_api_route(
    path="/update_access_token_if_expired/{calendar_url}",
    endpoint=_update_access_token_if_expired,
)


def _refresh_token(calendar_url: str):
    return refresh_token(calendar_url, DuckDBConnector)


ROUTER.add_api_route(
    path="/refresh_token/{calendar_url}", endpoint=_refresh_token
)


@APP.get("/get_activities/{calendar_url}", response_class=PrettyJSONResponse)
async def get_activities(calendar_url: str) -> dict[str, Any]:
    await _update_access_token_if_expired(calendar_url)
    token = DuckDBConnector.check_if_credentials_exist(calendar_url)
    if token is not None:
        client = Client(access_token=token.access_token)

        DuckDBConnector.write_metadata(
            calendar_url=calendar_url, now=datetime.now()
        )
        return {
            f"activity {i}": activity
            for i, activity in enumerate(
                client.get_activities(limit=100, before=datetime.now())
            )
        }
    else:
        return {"status": "error", "message": ""}


@APP.get("/calendar/{calendar_url}", response_class=PlainTextResponse)
async def calendar(calendar_url: str) -> bytes:
    activities = await get_activities(calendar_url)
    return activities_to_calendar(activities).to_ical()


if __name__ == "__main__":
    uvicorn.run(
        app="app:APP",
        host=NAMESPACE.ip,
        port=NAMESPACE.port,
        reload=NAMESPACE.reload,
    )
