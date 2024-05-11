import logging
from pathlib import Path

from pydantic import BaseModel, BaseSettings, DirectoryPath, FilePath


class Settings(BaseSettings):
    STRAVA_CLIENT_ID: int
    STRAVA_CLIENT_SECRET: str

    class Config:
        """Read .env."""

        env_file = ".env"


class Namespace(BaseModel):
    # Define the root folder path as the grandparent of the folder containing this file
    directory_root: DirectoryPath = Path(
        __file__
    ).parent.parent.parent.resolve()
    # Define the log folder path as a subfolder named 'logs' in the root folder
    directory_log: DirectoryPath = directory_root / "logs"
    # Define the debug log file path as a file named 'debug.log' in the log folder
    filename_debug_log: FilePath = directory_log / "debug.log"

    # Define the log levels for the logger and the two handlers
    # These levels represent the lowest severity of messages that will be handled.
    logger_level: int = logging.DEBUG
    logger_shell_level: int = logging.DEBUG
    logger_file_level: int = logging.DEBUG

    # Define the log formats for shell and file handlers
    # These formats determine how the log messages will be formatted
    logger_shell_fmt: str = "%(message)s"
    logger_file_fmt: str = "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] \t%(message)s"

    directory_databases: DirectoryPath = directory_root / "databases"
    filename_database: FilePath = directory_databases / "stra2ics.duckdb"
    tablename_metadata: str = "metadata"
    tablename_credentials: str = "credentials"
    tablename_activities: str = "activities"

    port: int = 8080
    ip: str = "127.0.0.1"
    web_url: str = f"http://{ip}:{port}"
    reload: bool = True

    credentials: Settings = Settings()  # type: ignore


NAMESPACE = Namespace()
