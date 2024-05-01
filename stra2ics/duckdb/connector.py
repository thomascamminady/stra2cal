import datetime

import duckdb

from stra2ics.utils.namespace import NAMESPACE


class DuckDBConnector:
    def __init__(self) -> None:
        self.namespace = NAMESPACE

    def _execute_query(
        self, query: str, parameters: tuple
    ) -> duckdb.DuckDBPyConnection:
        connection = duckdb.connect(
            database=self.namespace.filename_database.as_posix()
        )
        result = connection.execute(query=query, parameters=parameters)
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
        self._execute_query(query=query, parameters=parameters)

    def write_metadata(self, calendar_url: str, now: datetime.datetime) -> None:
        """Inserts or updates the metadata in the database."""
        query = f"""
                INSERT INTO {self.namespace.tablename_metadata}
                (hash, timestamp)
                VALUES (?, ?)
                ON CONFLICT(hash) DO UPDATE SET
                timestamp = excluded.timestamp
                """
        parameters = (calendar_url, now)

        self._execute_query(query=query, parameters=parameters)

    def check_if_credentials_exist(self, calendar_url: str) -> bool:
        """Reads the matching hash from the credentials table."""
        query = f"""
                SELECT * FROM {self.namespace.tablename_credentials}
                WHERE hash = ?
                """
        parameters = (calendar_url,)
        result = self._execute_query(
            query=query, parameters=parameters
        ).fetchone()
        return result is not None
