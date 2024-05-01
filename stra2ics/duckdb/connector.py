import datetime
from typing import Literal, overload

import duckdb

from stra2ics.utils.namespace import NAMESPACE


class DuckDBConnector:
    def __init__(self) -> None:
        self.namespace = NAMESPACE

    @overload
    def _execute_query(
        self, query: str, parameters: tuple, fetched: Literal[False]
    ) -> duckdb.DuckDBPyConnection: ...
    @overload
    def _execute_query(
        self, query: str, parameters: tuple, fetched: Literal[True]
    ) -> tuple | None: ...

    def _execute_query(
        self, query: str, parameters: tuple, fetched: bool = False
    ) -> duckdb.DuckDBPyConnection | tuple | None:
        connection = duckdb.connect(
            database=self.namespace.filename_database.as_posix()
        )
        result = connection.execute(query=query, parameters=parameters)
        if fetched:
            result = result.fetchone()

        connection.close()

        return result

    def write_credentials(
        self,
        calendar_url: str,
        access_token: str,
        refresh_token: str,
        expires_at: int,
    ) -> None:
        """Inserts or updates the credentials in the database."""
        query = f"""
                INSERT INTO {self.namespace.tablename_credentials}
                (hash, access_token, refresh_token, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(hash) DO UPDATE SET
                access_token = excluded.access_token,
                refresh_token = excluded.refresh_token,
                expires_at = excluded.expires_at
                """

        parameters = (calendar_url, access_token, refresh_token, expires_at)
        self._execute_query(query=query, parameters=parameters, fetched=False)

    def write_metadata(self, calendar_url: str, now: datetime.datetime) -> None:
        """Inserts or updates the metadata in the database."""
        query = f"""
                INSERT INTO {self.namespace.tablename_metadata}
                (hash, last_request)
                VALUES (?, ?)
                ON CONFLICT(hash) DO UPDATE SET
                last_request = excluded.last_request
                """
        parameters = (calendar_url, now)

        self._execute_query(query=query, parameters=parameters, fetched=False)

    def check_if_credentials_exist(self, calendar_url: str) -> tuple | None:
        """Reads the matching hash from the credentials table."""
        query = f"""
                SELECT * FROM {self.namespace.tablename_credentials}
                WHERE hash = ?
                """
        parameters = (calendar_url,)
        return self._execute_query(
            query=query, parameters=parameters, fetched=True
        )
