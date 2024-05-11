import duckdb

from stra2cal.utils.namespace import NAMESPACE

if __name__ == "__main__":
    # If database directory does not exist, create it
    if not NAMESPACE.directory_databases.exists():
        NAMESPACE.directory_databases.mkdir()

    # Connect to the DuckDB database
    connection = duckdb.connect(NAMESPACE.filename_database.as_posix())

    # Create the metadata table
    connection.execute(
        query=f"""CREATE TABLE IF NOT EXISTS {NAMESPACE.tablename_metadata}
            (
                hash TEXT,
                last_request TIMESTAMP,
                PRIMARY KEY (hash)
            )"""
    )
    # Create the activities table
    connection.execute(
        query=f"""CREATE TABLE IF NOT EXISTS {NAMESPACE.tablename_activities}
            (
                hash TEXT,
                activity_start TIMESTAMP,
                activity_stop TIMESTAMP,
                activity_name TEXT,
                activity_text TEXT,
                PRIMARY KEY (hash)
            )"""
    )
    # Create the credentials table
    connection.execute(
        query=f"""CREATE TABLE IF NOT EXISTS {NAMESPACE.tablename_credentials}
        (
            hash TEXT,
            access_token TEXT,
            refresh_token TEXT,
            expires_at INTEGER,
            PRIMARY KEY (hash)
        )"""
    )
